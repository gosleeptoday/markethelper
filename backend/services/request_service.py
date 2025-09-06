from backend.models import Request, Status
from backend.schemas import RequestOut
from tortoise.exceptions import DoesNotExist


class RequestService:

    @staticmethod
    async def list_requests() -> list[RequestOut]:
        return await RequestOut.from_queryset(Request.all())

    @staticmethod
    async def get_request(request_id: int) -> RequestOut:
        request = await Request.get(id=request_id)
        return RequestOut.from_orm(request)

    @staticmethod
    async def approve_request(request_id: int, group_id: int | None = None) -> dict:
        request = await Request.get(id=request_id)

        # находим статус "subscription.ACTIVE"
        status = await Status.get(type="subscription", code="ACTIVE")

        request.status = status
        await request.save()

        # TODO: создать подписку пользователю, привязать к группе если group_id передан
        return {"message": f"Заявка {request_id} одобрена", "group": group_id}

    @staticmethod
    async def reject_request(request_id: int) -> dict:
        request = await Request.get(id=request_id)

        # находим статус "request.REJECTED"
        status = await Status.get(type="request", code="REJECTED")

        request.status = status
        await request.save()

        return {"message": f"Заявка {request_id} отклонена"}
