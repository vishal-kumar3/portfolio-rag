from datetime import datetime
from fastapi.routing import APIRouter
from fastapi import HTTPException, Request
from langchain_core.messages import HumanMessage, AIMessage

from app.schemas.rag import ChatBotQuerySchema

router = APIRouter()


@router.get('/chat_history')
async def chat_history(
  request: Request
):
  try:
    rag_service = request.app.state.rag_service
    history = rag_service.get_chat_history_for_user()

    return {
      "chat_history": history
    }
  except Exception as e:
    raise HTTPException(status_code=404, detail=str(e))

@router.post('/query')
async def chat_bot(
  body: ChatBotQuerySchema,
  request: Request
):
  try:
    rag_service = request.app.state.rag_service
    question = f"[current_time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]: " + body.query

    rag_service.add_message(HumanMessage(content=question))

    chain = await rag_service.rag_query_chain()
    response = await chain.ainvoke({"question": question})

    rag_service.add_message(AIMessage(content=response.content))

    return {
        "response": response.content,
    }

  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
