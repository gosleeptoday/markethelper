from fastapi import APIRouter, HTTPException
from backend.schemas.user import ProfileOut, UserCreate
from backend.services.user_service import UserService

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("/{tg_id}", response_model=ProfileOut)
async def get_profile(tg_id: int):
    """
    Профиль по tg_id — возвращает данные для бота
    """
    return await UserService.get_profile_by_tg(tg_id)


@router.post("/ensure")
async def ensure_user(data: UserCreate):
    """
    Регистрируем пользователя по tg_id, если его ещё нет
    """
    user = await UserService.get_or_create_by_tg(data)
    return {"id": user.id, "tg_id": user.tg_id}
