import httpx
from backend.models import Status
import os
import requests
from http.cookiejar import MozillaCookieJar
from requests.cookies import create_cookie
from backend.models import AccessFile
from datetime import datetime, timedelta
from fastapi import HTTPException

BOT_URL = "http://bot:8001/notify"  # адрес API бота в docker-compose

async def notify_user(tg_id: int, message: str, has_active_sub: bool = False):
    """
    Отправка уведомления боту
    """
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                BOT_URL,
                json={
                    "tg_id": tg_id,
                    "message": message,
                    "has_active_sub": has_active_sub
                }
            )
        except Exception as e:
            print(f"⚠ Ошибка при отправке уведомления: {e}")


async def get_status(type: str, code: str):
    """
    Получение или создание статуса
    """
    status = await Status.get_or_none(type=type, code=code)
    if not status:
        status = await Status.create(type=type, code=code, name=code.capitalize())
    return status


SALESFINDER_LOGIN_URL = "https://salesfinder.ru/api/user/signIn"
SALESFINDER_CHECK_URL = "https://salesfinder.ru/api/user/getUser"

COOKIE_DIR = os.path.join(os.getcwd(), "cookie")
os.makedirs(COOKIE_DIR, exist_ok=True) 


async def generate_and_save_cookies(file: "AccessFile") -> "AccessFile":
    """
    Авторизация по логину/паролю и сохранение куков (главное — connect.sid).
    """
    if not file.login or not file.password:
        raise HTTPException(400, "У файла нет логина или пароля")

    cookie_file_path = os.path.join(COOKIE_DIR, f"{file.id}.txt")
    file.path = cookie_file_path

    session = requests.Session()
    session.cookies = MozillaCookieJar(cookie_file_path)

    try:
        response = session.post(
            SALESFINDER_LOGIN_URL,
            json={"user_email_address": file.login, "user_password": file.password},
        )

        if response.status_code != 200:
            raise HTTPException(401, f"Ошибка авторизации: {response.status_code}")

        data = response.json()

        if not any(c.name == "connect.sid" for c in session.cookies):
            connect_sid = data.get("sid") or data.get("connect.sid")
            if connect_sid:
                cookie = create_cookie(name="connect.sid", value=connect_sid, domain="salesfinder.ru")
                session.cookies.set_cookie(cookie)
                print("✅ Cookie 'connect.sid' добавлено вручную")

        session.cookies.save(ignore_discard=True, ignore_expires=True)
        print(f"✅ Куки сохранены в {cookie_file_path}")

        file.last_updated = datetime.utcnow()
        file.locked_until = datetime.utcnow() + timedelta(minutes=10)
        await file.save()

        return file

    except Exception as ex:
        raise HTTPException(500, f"Ошибка при генерации куков: {ex}")


async def is_cookie_valid(file: "AccessFile") -> tuple[bool, str]:
    """
    Проверка, что connect.sid рабочий.
    """
    cookie_file_path = file.path

    if not cookie_file_path or not os.path.exists(cookie_file_path) or os.path.getsize(cookie_file_path) == 0:
        return False, "Файл куков не найден или пуст"

    try:
        cookies = MozillaCookieJar(cookie_file_path)
        cookies.load(ignore_discard=True, ignore_expires=True)

        session = requests.Session()
        session.cookies = cookies
        response = session.get(SALESFINDER_CHECK_URL)

        if response.status_code == 200:
            if any(c.name == "connect.sid" for c in cookies):
                return True, "✅ Куки рабочие (connect.sid найден)"
            return False, "❌ Куки есть, но connect.sid отсутствует"
        else:
            return False, f"❌ Сервер отклонил куки (код {response.status_code})"

    except Exception as e:
        return False, f"Ошибка при проверке куков: {e}"


async def get_file_status(file: "AccessFile") -> dict:
    """
    Получить статус файла
    """
    return {
        "path": file.path,
        "last_updated": file.last_updated,
        "locked_until": file.locked_until,
    }


async def read_file_content(file: "AccessFile") -> str:
    """
    Прочитать содержимое файла
    """
    if not file.path or not os.path.exists(file.path):
        raise HTTPException(404, "Файл отсутствует на диске")

    with open(file.path, "r", encoding="utf-8") as f:
        return f.read()