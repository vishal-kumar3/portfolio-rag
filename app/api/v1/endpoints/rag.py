from datetime import datetime
from typing import Optional
from fastapi.responses import StreamingResponse
from fastapi.routing import APIRouter
from fastapi import HTTPException, Query, Request
from langchain_core.messages import HumanMessage, AIMessage

from app.schemas.rag import ChatBotQuerySchema
from app.services.chat import ChatSession
from app.services.rag import RAGService

router = APIRouter()


@router.get('/chat_history/{user_id}')
async def chat_history(user_id: str, request: Request):
  try:
    chat_session: ChatSession = request.app.state.chat_session
    history = chat_session.get_chat_history_for_user(user_id)

    return {
        "chat_history": history,
    }
  except Exception as e:
    raise HTTPException(status_code=404, detail=str(e))


@router.get('/query')
async def chat_bot(request: Request,
                   query: str = Query(..., description="User query"),
                   userId: Optional[str] = Query(
                       None, description="Optional user ID")):
  try:
    rag_service: RAGService = request.app.state.rag_service
    chat_session: ChatSession = request.app.state.chat_session
    question = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]: " + query

    user_id = userId if userId else ""
    if not (user_id and chat_session.session_exists(user_id)):
      _, new_user_id = chat_session.create_chat()
      user_id = new_user_id
      userId = new_user_id

    chat_session.add_message(user_id, HumanMessage(content=question))

    chain = await rag_service.rag_query_chain(user_id, streaming=True)

    async def generate_response():
      import json
      current_response = []
      timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

      try:
        async for chunk in chain.astream({"question": question}):
          if chunk.content:
            current_response.append(chunk.content)
            response_data = {
                "type": "chunk",
                "content": chunk.content,
                "userId": user_id
            }
            yield f"data: {json.dumps(response_data)}\n\n"

        # Store the complete response in chat history
        full_response = "".join(current_response)

        chat_session.add_message(
            user_id, AIMessage(content=f"[{timestamp}]: {full_response}"))

        # Send completion message
        yield f"data: {json.dumps({'type': 'done', 'userId': user_id})}\n\n"

      except Exception as e:
        error_data = {"type": "error", "error": str(e), "userId": user_id}
        yield f"data: {json.dumps(error_data)}\n\n"

    return StreamingResponse(generate_response(),
                             media_type="text/event-stream",
                             headers={
                                 "Cache-Control": "no-cache",
                                 "Connection": "keep-alive",
                             })

  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
