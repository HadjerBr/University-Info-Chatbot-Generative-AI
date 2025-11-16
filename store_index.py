from dotenv import load_dotenv
import os
import re
import unicodedata
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from langchain_pinecone import PineconeVectorStore

from src.helper import (
    load_pdf_file,
    text_split,
    download_hugging_face_embeddings,
    clean_text,
)

load_dotenv()

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

extracted_data = load_pdf_file(data='Data/')
cleaned_docs = []

for doc in extracted_data:
    doc.page_content = clean_text(doc.page_content)
    cleaned_docs.append(doc)

text_chunks = text_split(cleaned_docs)
embeddings = download_hugging_face_embeddings()


PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

pc = Pinecone(PINECONE_API_KEY)

index_name = "campusmate-db"

if not pc.has_index(index_name):
    pc.create_index(
        name=index_name,
        vector_type="dense",
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        ),
        deletion_protection="disabled",
        tags={
            "environment": "development"
        }
    )

# Create embeddings for each chunk and upload them to the Pinecone index
docsearch = PineconeVectorStore.from_documents(
    documents=text_chunks,
    index_name=index_name,
    embedding=embeddings,
)

