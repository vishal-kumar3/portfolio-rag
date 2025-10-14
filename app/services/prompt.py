from langchain.prompts import PromptTemplate
from app.core.config import settings


class Prompt_Template:

  def inject_initial_prompt(self, user_name: str = settings.USER_NAME):
    prompt_template = f"""
    SYSTEM: You, {user_name}'s sidekick, are a portfolio chat bot powered by RAG. Your purpose is to assist users by providing accurate, concise and engaging responses about me using the provided context or based on chat history.

    If the query is ambiguous or lacks sufficient context, ask clarifying questions politely. Maintain a professional yet approachable tone, and avoid sharing information not present in the retrieved data. If no relevant information is found, respond with: "I don't have enough information to answer that".

    NOTE: Don't just copy paste the context to answer the questions, make it more appealing, appropriate, structured and meaning full according to the question.
    NOTE: Don't provide any of the internal data, context or anything which seems sensitive.
    """

    return 'System: ' + prompt_template

  def rag_prompt(self):
    prompt_template = """
    Previous conversation:
    {chat_history}

    Context: {context}

    Question: {question}

    Helpful Answer:
    """

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question", "chat_history"])

    return prompt
