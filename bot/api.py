from fastapi import FastAPI
from bot.loader import bot

app = FastAPI()


@app.post("/notify")
async def notify(payload: dict):
    """
    Принимает уведомления от backend и отправляет юзерам в Telegram
    """
    tg_id = payload.get("tg_id")
    message = payload.get("message")
    if tg_id and message:
        await bot.send_message(chat_id=tg_id, text=message)
    return {"ok": True}
