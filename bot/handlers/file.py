import os
from aiogram import Router, types, F
from backend.models.file import AccessFile
from backend.services.utils import generate_and_save_cookies
from aiogram.types import FSInputFile

router = Router()

@router.callback_query(F.data.startswith("file:update:"))
async def update_cookies_handler(callback: types.CallbackQuery):
    file_id = int(callback.data.split(":")[2])

    file = await AccessFile.get_or_none(id=file_id)
    if not file:
        await callback.message.answer("❌ Файл не найден.")
        await callback.answer()
        return

    file = await generate_and_save_cookies(file)
    await callback.message.answer(
        f"🔄 Куки для файла <code>{file.id}</code> обновлены!\n"
        f"📅 Последнее обновление: <b>{file.last_updated}</b>",
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("file:get:"))
async def get_file_download_handler(callback: types.CallbackQuery):
    file_id = int(callback.data.split(":")[2])

    file = await AccessFile.get_or_none(id=file_id)
    if not file or not file.path or not os.path.exists(file.path):
        await callback.message.answer("❌ Файл отсутствует на диске.")
        await callback.answer()
        return

    document = FSInputFile(file.path, filename=f"cookies_{file.id}.txt")
    await callback.message.answer_document(document=document, caption="📂 Ваши куки")
    await callback.answer()