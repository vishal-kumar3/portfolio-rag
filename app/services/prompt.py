from langchain.prompts import PromptTemplate


class Prompt_Template:

  def rag_prompt(self):
    prompt_template = """
    Use the following pieces of context to answer the question. 
    If you don't know the answer, just say that you don't know, don't try to make up an answer. 
    
    Context: {context}
    
    Question: {question}
    
    Helpful Answer:
    """

    prompt = PromptTemplate(template=prompt_template,
                            input_variables=["context", "question"])

    return prompt
