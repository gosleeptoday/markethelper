from aiogram import Router, types, F
from datetime import datetime
from backend.services.file_service import FileService
from tortoise.exceptions import DoesNotExist
from bot.keyboards.cookie import file_actions_kb
from bot.services.api_client import APIClient
from bot.keyboards.profile_menu import profile_menu_kb
from bot.keyboards import subscription 

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
        f"💰 <b>Бонусы:</b> {data.get('bonus_balance')}"
    )

    await message.answer(text, reply_markup=profile_menu_kb())

@router.callback_query(F.data == "profile:referral")
async def referral_info(callback: types.CallbackQuery):
    tg_id = callback.from_user.id
    try:
        data = await api.get_referral_info(tg_id)
    except Exception as e:
        await callback.message.answer(f"error {str(e)}")
        print(f"[ERROR referral_info] {e}")
        return

    link = data.get("ref_link")
    count = data.get("ref_count", 0)

    await callback.message.answer(
        f"🎁 Ваша реферальная ссылка:\n"
        f"<code>{link}</code>\n\n"
        f"👥 Количество рефералов: <b>{count}</b>"
    )
    await callback.answer()

@router.callback_query(F.data == "profile:get_file")
async def get_file_handler(callback: types.CallbackQuery):
    try:
        file_info = await FileService.get_file(file_id=1)  # 🔧 пока тестовый id
    except DoesNotExist:
        await callback.message.answer("❌ Файл не найден.")
        await callback.answer()
        return

    text = (
        f"📅 Обновлён: <code>{file_info['last_updated']}</code>\n"
    )

    await callback.message.answer(
        text,
        parse_mode="HTML",
        reply_markup=file_actions_kb(file_info["id"])
    )
    await callback.answer()
    
@router.callback_query(F.data == "profile:support")
async def support_handler(callback: types.CallbackQuery):
    support_username = "YourSupportOperator"
    await callback.message.answer(
        f"📞 Связаться с оператором можно здесь: @{support_username}"
    )
    await callback.answer()

@router.callback_query(F.data == "profile:renew")
async def renew_subscription(callback: types.CallbackQuery):
    await callback.message.answer(
        "Выберите тариф для продления:",
        reply_markup=subscription.tariffs_kb()
    )
    await callback.answer()
