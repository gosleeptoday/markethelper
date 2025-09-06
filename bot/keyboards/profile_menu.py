from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def profile_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔑 Получить файл доступа", callback_data="profile:get_file")],
        [InlineKeyboardButton(text="🔄 Проверить/Обновить сессию", callback_data="profile:update_session")],
        [InlineKeyboardButton(text="💳 Продлить подписку", callback_data="profile:renew")],
        [InlineKeyboardButton(text="🎁 Реферальная ссылка", callback_data="profile:referral")],
    ])
