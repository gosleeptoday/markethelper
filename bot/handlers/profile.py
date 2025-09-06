from aiogram import Router, types, F
from datetime import datetime
from bot.services.api_client import APIClient
from bot.keyboards.profile_menu import profile_menu_kb
from bot.keyboards.profile_menu import profile_menu_kb  # для продления подписки

router = Router()
api = APIClient()


def _fmt_date(dt_iso: str | None) -> str:
    if not dt_iso:
        return "—"
    try:
        return datetime.fromisoformat(dt_iso.replace("Z", "+00:00")).strftime("%d.%m.%Y")
    except Exception:
        return dt_iso


@router.message(F.text == "👤Профиль")
@router.message(F.text == "/profile")
async def show_profile(message: types.Message):
    tg = message.from_user
    data = await api.get_profile(tg.id)

    active_until = data.get("active_until")
    if not active_until:
        await message.answer("❌ У вас нет активной подписки. Оформите её в меню.")
        return

    text = (
        f"👤 <b>Пользователь:</b> @{data.get('username') or '—'}\n"
        f"⭐️ <b>Тариф:</b> {data.get('tariff_name') or 'нет'}\n"
        f"🗓️ <b>Активен до:</b> { _fmt_date(active_until) }\n"
        f"📁 <b>Файл:</b> {data.get('access_file_path') or '—'} "
        f"(группа {data.get('access_group') or '—'})\n"
        f"🏆 <b>Уровень:</b> {data.get('level_name') or '—'}\n"
        f"✨ <b>XP:</b> {data.get('xp')}\n"
        f"💰 <b>Бонусы:</b> {data.get('bonus_balance')}"
    )

    await message.answer(text, reply_markup=profile_menu_kb())
