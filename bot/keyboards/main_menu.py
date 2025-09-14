from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu_kb(has_active_sub: bool):
    kb = []

    if has_active_sub:
        kb.append([KeyboardButton(text="👤Профиль"),
                  KeyboardButton(text="🤖ChatGPT")])
    else:
        kb.append([KeyboardButton(text="🛒Тарифы и подписка")])

    kb.extend([
        [KeyboardButton(text="❓FAQ")],
    ])

    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
