from fastapi import FastAPI
from backend.api import profile, users, subscriptions, files, referrals, requests, mailing, ai, session_updater
from backend.core.db import init_db, close_db

def create_app() -> FastAPI:
    app = FastAPI(title="MarketHelper Admin API")

    app.include_router(users.router)
    """app.include_router(subscriptions.router)
    app.include_router(files.router)"""
    app.include_router(referrals.router)
    app.include_router(requests.router)
    """app.include_router(mailing.router)
    app.include_router(session_updater.router)"""
    app.include_router(ai.router)
    app.include_router(profile.router)


    @app.on_event("startup")
    async def startup_event():
        await init_db()

    @app.on_event("shutdown")
    async def shutdown_event():
        await close_db()

    return app
