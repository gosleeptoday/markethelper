import aiohttp
from bot.config import BACKEND_URL


class APIClient:
    def __init__(self):
        self.base_url = BACKEND_URL

    async def create_user(self, tg_id: int, username: str | None, full_name: str | None, traffic_code: str | None = None):
        """
        Регистрируем пользователя в бекенде (для админки).
        """
        url = f"{self.base_url}/admin/users/"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={
                "tg_id": tg_id,
                "username": username,
                "full_name": full_name,
                "traffic_source_id": None,  # TODO: маппить traffic_code -> id
            }) as resp:
                return await resp.json()

    async def get_user(self, tg_id: int):
        url = f"{self.base_url}/admin/users/by_tg/{tg_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.json()

    async def create_request(self, tg_id: int, tariff_code: str, duration_months: int):
        """
        Создать заявку на подписку.
        """
        url = f"{self.base_url}/admin/requests/"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={
                "tg_id": tg_id,
                "tariff_code": tariff_code,
                "duration_months": duration_months
            }) as resp:
                return await resp.json()

    async def ensure_user(self, tg_id: int, username: str | None, full_name: str | None):
        """
        Создать пользователя, если его ещё нет (для бота).
        """
        url = f"{self.base_url}/profile/ensure"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={
                "tg_id": tg_id,
                "username": username,
                "full_name": full_name,
            }) as resp:
                return await resp.json()

    async def get_profile(self, tg_id: int):
        """
        Получить профиль пользователя (тариф, дата окончания и т.д.)
        """
        url = f"{self.base_url}/profile/{tg_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.json()
