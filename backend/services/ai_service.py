import os
import asyncio
import logging
import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import AsyncOpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai_service")

OPENAI_API_KEY = "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"

client_openai = AsyncOpenAI(api_key=OPENAI_API_KEY)

os.environ["OMP_NUM_THREADS"] = "2"

semaphore = asyncio.Semaphore(1)
client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(
    name="knowledge",
    embedding_function=embedding_functions.DefaultEmbeddingFunction()
)

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)


async def add_text(content: str, metadata: dict | None = None):
    logger.info("Начало добавления текста в ChromaDB")
    chunks = splitter.split_text(content)
    logger.info(f"Текст разбит на {len(chunks)} чанков")

    for i, chunk in enumerate(chunks):
        logger.info(f"Добавляю чанк {i}")
        try:
            await asyncio.to_thread(
                collection.add,
                documents=[chunk],
                ids=[f"{metadata.get('source', 'doc')}_{i}" if metadata else f"doc_{i}"],
                metadatas=[metadata or {}]
            )
        except Exception as e:
            logger.error(f"Ошибка при добавлении чанка {i}: {e}")
    logger.info("Текст успешно добавлен")


async def list_texts() -> list[str]:
    logger.info("Запрос списка всех текстов")
    try:
        texts = await asyncio.to_thread(lambda: [doc for doc in collection.get()["documents"]])
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
            model="gpt-4o-mini",  # можно заменить на gpt-4o или gpt-3.5-turbo
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        answer = response.choices[0].message.content
        logger.info("Ответ от OpenAI получен")
        return answer
    except Exception as e:
        logger.error(f"Ошибка при запросе к OpenAI: {e}")
        return "❌ Ошибка при обработке запроса AI"