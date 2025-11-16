from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
import re
import unicodedata



# Extract Data From the PDF Files


def load_pdf_file(data):
    loader = DirectoryLoader(
        data,
        glob="*.pdf",
        loader_cls=PyPDFLoader
    )
    
    documents = loader.load()
    return documents




def clean_text(text: str) -> str:
    # Normalize weird unicode 
    text = unicodedata.normalize("NFKC", text)

    # Remove trailing spaces before newlines: 
    text = re.sub(r"[ \t]+\n", "\n", text)

    # Collapse many blank lines into a single blank line
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Collapse multiple spaces inside a line
    text = re.sub(r"[ \t]{2,}", " ", text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text

# Chunking
def text_split(cleaned_docs):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    
    text_chunks = text_splitter.split_documents(cleaned_docs)
    return text_chunks

# Download the Embeddings from Hugging Face
def download_hugging_face_embeddings():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2" # 384 dimensional dense vector space
    )
    return embeddings

