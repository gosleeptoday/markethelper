import os
import asyncio
import logging
import uuid
import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import AsyncOpenAI
import pdfplumber

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai_service")

OPENAI_API_KEY = ""

client_openai = AsyncOpenAI(api_key=OPENAI_API_KEY)

os.environ["OMP_NUM_THREADS"] = "2"

semaphore = asyncio.Semaphore(1)
client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(
    name="knowledge",
    embedding_function=embedding_functions.DefaultEmbeddingFunction()
)

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)


async def add_text(text: str, metadata: dict):
    logger.info("Начало добавления текста в ChromaDB")

    try:
        doc_id = str(uuid.uuid4())  # генерируем уникальный ID
        await asyncio.to_thread(
            lambda: collection.add(
                ids=[doc_id],
                documents=[text],
                metadatas=[metadata],
            )
        )
        logger.info(f"Текст добавлен: {doc_id[:8]}...")

    except Exception as e:
        logger.error(f"Ошибка при добавлении текста: {e}")
        raise

async def list_texts():
    logger.info("Запрос списка всех текстов")
    try:
        result = await asyncio.to_thread(lambda: collection.get())
        docs = result["documents"]
        metas = result["metadatas"]
        texts = [{"text": d, "metadata": m} for d, m in zip(docs, metas)]
        logger.info(f"Найдено {len(texts)} текстов")
        return texts
    except Exception as e:
        logger.error(f"Ошибка при получении текстов: {e}")
        return []

async def query_ai(question: str) -> str:
    logger.info(f"Запрос AI: {question}")

    context = ""
    try:
        results = await asyncio.to_thread(
            lambda: collection.query(query_texts=[question], n_results=3)
        )
        if results and results["documents"]:
            context = "\n".join(results["documents"][0])
            logger.info(f"Найден контекст: {context[:100]}...")
    except Exception as e:
        logger.error(f"Ошибка при поиске контекста: {e}")

    prompt = f"""
Ты — умный ассистент, который помогает отвечать на вопросы с учётом базы знаний.

Вопрос пользователя:
{question}

Контекст (фрагменты из базы знаний):
{context}

Твоя задача:
1. Ответь строго по теме вопроса.
2. Обязательно используй информацию из контекста — процитируй или перескажи важные части.
3. Если в контексте есть данные, которые помогают лучше оптимизировать или уточнить ответ, примени их.
4. Если контекста не хватает — честно скажи об этом, но всё равно постарайся дать полезный совет.

Форматируй ответ красиво, на русском языке, понятно и как эксперт.
"""
    print(prompt)
    try:
        response = await client_openai.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        answer = response.choices[0].message.content
        logger.info("Ответ от OpenAI получен")
        return answer
    except Exception as e:
        logger.error(f"Ошибка при запросе к OpenAI: {e}")
        return "❌ Ошибка при обработке запроса AI"

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200):
    """
    Разбиваем длинный текст на чанки для векторной БД.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start += chunk_size - overlap
    return [c for c in chunks if c]
