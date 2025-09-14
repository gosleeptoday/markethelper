from aiogram import Router, types, F
from bot.services.api_client import APIClient
from bot.keyboards.main_menu import main_menu_kb

router = Router()
api = APIClient()

@router.message(F.text.startswith("/start"))
async def cmd_start(message: types.Message):
    tg = message.from_user
    args = message.text.split(maxsplit=1)
    referrer_id = None

    if len(args) > 1 and args[1].startswith("ref_"):
        try:
            referrer_id = int(args[1].replace("ref_", ""))
        except ValueError:
            referrer_id = None

    try:
        await api.create_user(
            tg.id,
            tg.username,
            f"{tg.first_name or ''} {tg.last_name or ''}".strip(),
        )
    except Exception as e:
        print(f"[ERROR create_user] {e}")

    if referrer_id and referrer_id != tg.id:
        await api.bind_referral(referred_tg=tg.id, referrer_tg=referrer_id)

    profile = await api.get_profile(tg.id)
    has_active = bool(profile and profile.get("active_until"))

    await message.answer(
        "👋 Добро пожаловать в <b>MarketHelper</b>!",
        reply_markup=main_menu_kb(has_active_sub=has_active)
    )
