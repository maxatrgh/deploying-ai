from langchain.tools import tool
from langchain_community.document_loaders import JSONLoader
from utils.logger import get_logger

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from dotenv import load_dotenv

import os



_logs = get_logger(__name__)
load_dotenv(".env")
#load_dotenv(".secrets")
load_dotenv(".secrets_max")
_logs.info(f"OPENAI_API_KEY detected: {bool(os.getenv('OPENAI_API_KEY'))}")

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_JSON_PATH = os.path.join(_THIS_DIR, "leftover_tips.json")

_logs.info("Initializing ChromaDB client...")

client = chromadb.Client()

embedding_function = OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small",
)

collection_name = "leftover_tips"
collection = client.get_or_create_collection(
    name=collection_name,
    embedding_function=embedding_function,
)

_logs.info(f"Using Chroma collection: {collection_name}")

def get_metadata(record: dict, metadata: dict) -> dict:
    """
    Add custom metadata for each leftover tip record.

    The JSON file is expected to be a list of objects like:
    {
      "id": 1,
      "title": "...",
      "text": "..."
    }
    """
    metadata["id"] = record.get("id")
    metadata["title"] = record.get("title")
    metadata["text"] = record.get("text")
    return metadata


def _load_documents():
    """
    Load leftover tips as LangChain Documents using JSONLoader.
    """
    _logs.info("Loading leftover tips from JSON using JSONLoader...")

    loader = JSONLoader(
        file_path=_JSON_PATH,
        jq_schema=".[]",
        content_key="text",
        text_content=True,
        metadata_func=get_metadata,
    )

    docs = loader.load()
    _logs.info(f"Loaded {len(docs)} leftover tip documents.")
    return docs


# Populate Chroma collection 

def _ensure_collection_populated() -> None:
    count = collection.count()
    if count > 0:
        _logs.info(
            f"Chroma collection '{collection_name}' already has {count} item(s)."
        )
        return

    _logs.info(
        f"Chroma collection '{collection_name}' is empty. Populating with leftover tips..."
    )

    docs = _load_documents()

    ids = []
    documents = []
    metadatas = []

    for idx, doc in enumerate(docs):
        meta = doc.metadata or {}
        tip_id = meta.get("id", idx)  
        ids.append(str(tip_id))
        documents.append(doc.page_content)
        metadatas.append(meta)

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )

    _logs.info(
        f"Populated Chroma collection '{collection_name}' with {len(ids)} leftover tips."
    )


# leftover_tips_helper

@tool
def leftover_tips_helper(question: str) -> str:
    """
    Answer questions about serving and preserving leftovers
    by finding the most relevant tip from a small dataset stored
    in an in-memory ChromaDB collection.

    This tool:
    - Loads leftover tips from leftover_tips.json via JSONLoader
    - Stores them in an in-memory ChromaDB collection (on first use)
    - Uses semantic search (OpenAI embeddings) to find the best matching tip

    Use this tool when the user asks about:
    - how long leftovers are safe
    - how to store or reheat leftovers
    - serving food safely, especially leftovers
    """
    _logs.debug(f"leftover_tips_helper called with question: {question!r}")

    if not question or not question.strip():
        _logs.warning("leftover_tips_helper received an empty or blank question.")
        return (
            "Please ask a specific question about leftovers, such as storage time, "
            "reheating, or how to serve them safely."
        )

    # Make sure the Chroma collection has all leftover tips
    _ensure_collection_populated()

    _logs.debug("Querying DB for the best matching leftover tip...")
    results = collection.query(
        query_texts=[question],
        n_results=1,
    )

    metadatas = results.get("metadatas", [[]])
    documents = results.get("documents", [[]])

    if not metadatas or not metadatas[0] or not documents or not documents[0]:
        _logs.warning("No matching tips returned from DB.")
        return (
            "I could not find a matching tip for that question. "
            "Try asking more directly about storage, reheating, or serving leftovers."
        )

    best_meta = metadatas[0][0]
    best_doc = documents[0][0]

    title = best_meta.get("title", "Leftover tip")

    _logs.debug(
        f"Best leftover tip found: id={best_meta.get('id')}, title={title!r}"
    )

    answer = (
        "Here is a helpful tip about leftovers:\n\n"
        f"{title}\n"
        f"{best_doc}\n\n"        
    )

    return answer
