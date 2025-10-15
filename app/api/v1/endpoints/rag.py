from datetime import datetime
from fastapi.routing import APIRouter
from fastapi import HTTPException, Request
from langchain_core.messages import HumanMessage, AIMessage

from app.schemas.rag import ChatBotQuerySchema
from app.services.chat import ChatSession
from app.services.rag import RAGService

router = APIRouter()


@router.get('/chat_history/{user_id}')
async def chat_history(
    user_id: str,
    request: Request
):
    try:
        chat_session: ChatSession = request.app.state.chat_session
        history = chat_session.get_chat_history(user_id)

        return {
            "chat_history": history,
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post('/query')
async def chat_bot(
  body: ChatBotQuerySchema,
  request: Request
):
  try:
    rag_service: RAGService = request.app.state.rag_service
    chat_session: ChatSession = request.app.state.chat_session
    question = f"[current_time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]: " + body.query

    if not (body.userId and chat_session.session_exists(body.userId)):
      _, user_id = chat_session.create_chat()
      body.userId = user_id

    chat_session.add_message(body.userId, HumanMessage(content=question))

    chain = await rag_service.rag_query_chain(body.userId)
    response = await chain.ainvoke({"question": question})

    chat_session.add_message(body.userId, AIMessage(content=response.content))

    return {
        "response": response.content,
        "userId": body.userId
    }

  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
