from fastapi import APIRouter, HTTPException, BackgroundTasks
from backend.models import User, Tariff, Duration, Request, Status, Subscription, Referral
from backend.schemas import RequestOut
from datetime import datetime, timedelta
import httpx

router = APIRouter(prefix="/admin/requests", tags=["Admin - Requests"])

BOT_URL = "http://bot:8001/notify" 


async def notify_user(tg_id: int, message: str):
    async with httpx.AsyncClient() as client:
        try:
            await client.post(BOT_URL, json={"tg_id": tg_id, "message": message})
        except Exception as e:
            print(f"⚠ Ошибка при отправке уведомления: {e}")

async def get_status(type: str, code: str):
    status = await Status.get_or_none(type=type, code=code)
    if not status:
        status = await Status.create(type=type, code=code, name=code.capitalize())
    return status


@router.get("/", response_model=list[RequestOut])
async def list_requests():
    """
    Получить все заявки
    """
    requests = await Request.all().prefetch_related('user', 'tariff', 'duration', 'status')
    return [RequestOut.from_orm(req) for req in requests]


@router.post("/")
async def create_request(data: dict):
    """
    Создание заявки из бота
    data = { tg_id, tariff_code, duration_months }
    """
    print(f"Received data: {data}")

    user = await User.get_or_none(tg_id=data["tg_id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    tariff = await Tariff.get_or_none(code=data["tariff_code"])
    if not tariff:
        raise HTTPException(status_code=400, detail="Invalid tariff")

    duration = await Duration.get_or_none(months=data["duration_months"])
    if not duration:
        raise HTTPException(status_code=400, detail="Invalid duration")

    status = await get_status(type="request", code="PENDING")

    req = await Request.create(
        user=user,
        tariff=tariff,
        duration=duration,
        status=status,
    )

    return {"received_data": data, "id": req.id, "message": "Request created"}


@router.post("/{request_id}/approve")
async def approve_request(request_id: int, background_tasks: BackgroundTasks):
    req = await Request.get_or_none(id=request_id).prefetch_related("user", "tariff", "duration")
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    active_status = await get_status(type="subscription", code="ACTIVE")
    approved_status = await get_status(type="request", code="APPROVED")

    end_date = datetime.utcnow() + timedelta(days=30 * req.duration.months)

    subscription = await Subscription.create(
        user_id=req.user.id,
        tariff_id=req.tariff.id,
        duration_id=req.duration.id,
        status_id=active_status.id,
        start_date=datetime.utcnow(),
        end_date=end_date,
    )

    req.status = approved_status
    await req.save()

    # 🎁 проверка реферала
    referral = await Referral.get_or_none(referred=req.user)
    if referral and not referral.activated:
        referral.activated = True
        await referral.save()

        referrer = await referral.referrer
        referrer.bonus_balance += 100  # бонус за оплату
        await referrer.save()

        background_tasks.add_task(
            notify_user,
            referrer.tg_id,
            f"🎉 Ваш реферал @{req.user.username} активировал подписку! "
            f"+100 бонусов на баланс."
        )

    background_tasks.add_task(
        notify_user,
        req.user.tg_id,
        f"✅ Ваша заявка #{req.id} на тариф {req.tariff.name} одобрена!\nНапишите /start еще раз для появления кнопки Профиль."
    )

    return {"message": f"Request {request_id} approved", "subscription_id": subscription.id}

@router.post("/{request_id}/reject")
async def reject_request(request_id: int, background_tasks: BackgroundTasks):
    """
    Отклонить заявку
    """
    req = await Request.get_or_none(id=request_id).prefetch_related("user", "tariff")
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    rejected_status = await get_status(type="request", code="REJECTED")
    req.status = rejected_status
    await req.save()

    background_tasks.add_task(
        notify_user,
        req.user.tg_id,
        f"❌ Ваша заявка #{req.id} на тариф {req.tariff.name} отклонена."
    )

    return {"message": f"Request {request_id} rejected"}
