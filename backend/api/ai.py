import logging
import time
from fastapi import APIRouter, HTTPException
from backend.services import ai_service

router = APIRouter(prefix="/ai", tags=["AI"])
logger = logging.getLogger("ai_service")

@router.post("/texts")
async def add_text(data: dict):
    """
    Добавить текст в базу знаний (ChromaDB).
    data = { "text": "любой текст", "metadata": {...} }
    """
    if "text" not in data:
        raise HTTPException(400, "text is required")

    await ai_service.add_text(
        data["text"],
        metadata=data.get("metadata", {})
    )
    return {"status": "ok"}


@router.get("/texts")
async def list_texts():
    """
    Получить список всех сохранённых текстов.
    """
    texts = await ai_service.list_texts()
    return texts


@router.delete("/texts/{text_id}")
async def delete_text(text_id: str):
    """
    Удалить текст по id.
    """
    ok = await ai_service.delete_text(text_id)
    if not ok:
        raise HTTPException(404, "text not found")
    return {"status": "deleted", "id": text_id}


@router.post("/query")
async def query_ai(data: dict):
    """
    Задать вопрос к базе знаний (через RAG).
    data = { "question": "вопрос пользователя" }
    """
    if "question" not in data:
        raise HTTPException(400, "question is required")

    start_time = time.time()  # начало отсчета времени
    logger.info(f"Запрос AI: {data['question']}")

    # Вызов сервиса AI
    answer = await ai_service.query_ai(data["question"])

    elapsed = time.time() - start_time  # время обработки
    logger.info(f"Время обработки запроса: {elapsed:.3f} сек")

    return {
        "answer": answer,
        "time_seconds": elapsed  # можно возвращать пользователю
    }

@router.get("/health")
async def health_check():
    """
    Проверка, что сервис AI работает.
    """
    return {"status": "ok"}
