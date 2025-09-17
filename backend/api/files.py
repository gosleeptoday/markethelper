from fastapi import APIRouter, HTTPException
from backend.services import file_service

router = APIRouter(prefix="/files", tags=["Files"])


@router.get("/{group_id}/status")
async def group_file_status(group_id: int):
    """
    Проверить статус файла (куки) для группы
    """
    file = await file_service.get_group_file(group_id)
    return await file_service.get_file_status(file)


@router.get("/{group_id}/get")
async def get_group_file(group_id: int):
    """
    Получить содержимое файла (куки)
    """
    file = await file_service.get_group_file(group_id)
    content = await file_service.read_file_content(file)
    return {"group_id": group_id, "file": file.path, "cookies": content}


@router.post("/{group_id}/update")
async def update_group_file(group_id: int, data: dict):
    """
    Обновить файл (куки). Доступно и пользователям.
    data = { "cookies": "новые куки", "user_id": 123 }
    """
    if "cookies" not in data:
        raise HTTPException(400, "cookies are required")

    file = await file_service.get_group_file(group_id)
    file = await file_service.update_cookies(file, data["cookies"], user_id=data.get("user_id"))

    return {
        "status": "updated",
        "group_id": group_id,
        "path": file.path,
        "last_updated": file.last_updated,
        "locked_until": file.locked_until,
    }
