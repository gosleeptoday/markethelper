from aiogram import Router, types, F
from bot.services.api_client import APIClient
from bot.keyboards.main_menu import main_menu_kb

router = Router()
api = APIClient()

@router.message(F.text == "/start")
async def cmd_start(message: types.Message):
    tg = message.from_user
    try:
        await api.create_user(
            tg.id,
            tg.username,
            f"{tg.first_name or ''} {tg.last_name or ''}".strip()
        )
    except Exception as e:
        print(f"[ERROR create_user] {e}")

    try:
        profile = await api.get_profile(tg.id)
    except Exception:
        profile = None

    has_active = bool(profile and profile.get("active_until"))

    await message.answer(
        "👋 Добро пожаловать в <b>MarketHelper</b>!\n\n"
        "Здесь вы сможете оформить подписку на SalesFinder, получать доступ к файлам и использовать AI-помощника.",
        reply_markup=main_menu_kb(has_active_sub=has_active)
    )
