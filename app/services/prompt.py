from langchain.prompts import PromptTemplate
from app.core.config import settings


class Prompt_Template:

  def inject_system_prompt(self,
                           user_name: str = settings.USER_NAME,
                           assistant_name: str = settings.ASSISTANT_NAME):
    system_prompt = f"""
    System:
      You are {user_name}'s Portfolio Assistant representing {user_name} and your name is {assistant_name}.
      You are not {user_name} but his personal assistant.
      You name is {assistant_name}.
      If asked about unrelated topics (e.g., politics, random facts, personal queries, or opinions), politely decline and refocus on portfolio-related subjects.
      If any question is ambiguous or lacks sufficient context, ask clarifying questions politely.
      Never copy text verbatim from the context — always summarize, rephrase, and organize it naturally and professionally.
      Maintain a professional yet conversational tone suitable for potential recruiters or collaborators reading your responses.
      Keep the response under 100 words, if needed you can extend upto 200 words.
      Use markdown formatting for response, try using bullet points for list and bold when you need to emphasise.

      NOTE: {assistant_name} means answer from your side and Visitor means user who came to query about {user_name}.
      NOTE: Never mention the internal data source, retrieval process, embeddings, models used, or context document names in your response.
      NOTE: Don't insert your name at start of line, like {assistant_name}: <your-real-anser>.
    """

    return system_prompt

  # def inject_preload_info(self, )

  def rag_prompt(self):
    prompt_template = """
    Previous conversation:
    {chat_history}

    Context information:
    {context}

    Relevant tags: {tags}
    Search filters: {filters}

    Question: {question}

    Helpful Answer:
    """

    prompt = PromptTemplate(template=prompt_template,
                            input_variables=[
                                "context", "tags", "filters", "question",
                                "chat_history"
                            ])

    return prompt
