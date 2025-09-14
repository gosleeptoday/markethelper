from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from bot.keyboards.exit_ai import chatgpt_kb
from bot.keyboards.profile_menu import profile_menu_kb
from bot.services.api_client import APIClient
from bot.states.ai_states import AIChatStates

router = Router()
api = APIClient()

@router.message(F.text == "🤖ChatGPT")
async def start_chatgpt(message: types.Message, state: FSMContext):
    await state.set_state(AIChatStates.chatting)
    await message.answer(
        "💬 Отправьте мне свой вопрос, и я спрошу у ChatGPT.\n"
        "Чтобы выйти из режима, нажмите кнопку ниже 👇",
        reply_markup=chatgpt_kb()
    )


@router.message(F.text.in_({"/exit", "🚪 Выйти"}))
async def exit_chatgpt(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "✅ Вы вышли из режима ChatGPT",
        reply_markup=profile_menu_kb()
    )


@router.message(AIChatStates.chatting)
async def gpt_chat(message: types.Message, state: FSMContext):
    question = message.text
    thinking_msg = await message.answer("⌛ Думаю...")

    try:
        answer = await api.query_ai(question)
        await thinking_msg.delete()
        await message.answer(answer, parse_mode="Markdown")
    except Exception as e:
        await thinking_msg.delete()
        await message.answer(f"⚠️ Ошибка: {str(e)}")