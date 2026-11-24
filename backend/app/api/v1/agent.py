from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.core.rate_limit import limiter
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.core.database import get_db
from app.models.entities import User, Conversation, Message
from app.schemas.schemas import ChatRequest, ChatResponse
from app.api.deps import get_current_user
from app.services.agent_service import agent_service

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
@limiter.limit("30/minute")
def chat_with_agent(
    request: Request,
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = agent_service.chat(
        db=db,
        user_id=current_user.id,
        message=req.message,
        conversation_id=req.conversation_id
    )
    return result

@router.get("/conversations")
def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    convos = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.updated_at.desc()).all()
    return convos

@router.get("/conversations/{conversation_id}/messages")
def get_conversation_messages(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    convo = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    if not convo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).all()
    return {
        "conversation": convo,
        "messages": messages
    }
