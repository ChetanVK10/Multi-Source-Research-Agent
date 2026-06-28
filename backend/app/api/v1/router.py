from fastapi import APIRouter

from app.api.v1.routes import chat, chats, documents, health, models

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(chats.router, prefix="/chats", tags=["chats"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
