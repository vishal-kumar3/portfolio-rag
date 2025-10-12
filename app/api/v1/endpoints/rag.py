from fastapi.routing import APIRouter
from fastapi import HTTPException, Request

from app.schemas.rag import ChatBotQuerySchema

router = APIRouter()


@router.post('/query')
async def chat_bot(
  body: ChatBotQuerySchema,
  request: Request
):
  try:
    rag_service = request.app.state.rag_service
    question = body.query
    chain = await rag_service.rag_query_chain()

    response = await chain.ainvoke({"question": question})
    print("\n\n\n*****AI RESPONSE******")
    print(response)
    print("*****AI RESPONSE******\n\n\n")
    return {"response": response.content}

  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
