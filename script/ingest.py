import frontmatter
from langchain_core.documents import Document
from langchain_community.document_loaders.base import BaseLoader
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.services.vector_store import VectorStoreService

vector_store = VectorStoreService()


class FrontmatterMarkdownLoader(BaseLoader):
  """A custom loader for markdown files with YAML frontmatter."""

  def __init__(self, file_path: str):
    """Initialize with file path."""
    self.file_path = file_path

  def load(self) -> list[Document]:
    """Loads and parses the markdown file."""
    post = frontmatter.load(self.file_path)

    metadata = post.metadata
    metadata["source"] = self.file_path

    return [Document(page_content=post.content, metadata=metadata)]


def load_and_split_docs(dir_path: str):
  """Loads markdown docs using our custom loader and splits them."""

  loader = DirectoryLoader(
      path=dir_path,
      glob="**/*.md",
      loader_cls=FrontmatterMarkdownLoader,
      show_progress=True,
  )

  documents = loader.load()
  text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000,
                                                 chunk_overlap=200)
  final_chunks = []
  for doc in documents:
    doc.metadata["tags"] = ", ".join(map(str, doc.metadata["tags"]))
    if len(doc.page_content) > 3000:
      chunks = text_splitter.split_documents([doc])
      final_chunks.extend(chunks)
    else:
      final_chunks.append(doc)

  return final_chunks


def embed_and_add_to_vector_store(chunks):
  """Embeds the chunks and adds them to the vector store."""
  vector_store.add_documents(chunks)


def get_vector_data():
  """Fetches all data from the vector store."""
  return vector_store.client.get()


def main():
  # chunks = load_and_split_docs("./data")
  # embed_and_add_to_vector_store(chunks)
  # print(f"Added {len(chunks)} documents to the vector store.")
  data = get_vector_data()
  print(f"Vector store contains {len(data)} items.")

  for item in data:
    print("-----")
    print(item)


if __name__ == "__main__":
  main()
