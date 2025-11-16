from dotenv import load_dotenv

# === Third-Party Libraries ===
from flask import Flask, render_template, jsonify, request
from langchain_openai import OpenAI
from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_openai import ChatOpenAI


# === Local Modules ===
from src.helper import download_hugging_face_embeddings
from src.prompt import *
import os

app = Flask(__name__)

load_dotenv()

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

embeddings = download_hugging_face_embeddings()



index_name = "campusmate-db"

docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings
)

retriever = docsearch.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}
)

llm = ChatOpenAI(
    model="gpt-4o-mini",   
    temperature=0.4,
    max_tokens=500
)

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}")
])

qa_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, qa_chain)


@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/get", methods=["POST"])
def chat():
    user_msg = request.form.get("msg", "").strip()
    if not user_msg:
        return "No message provided", 400
    
    print("User:", user_msg)

    response = rag_chain.invoke({"input": user_msg})
    answer = response.get("answer", "No response generated")

    print("Response:", answer)
    return answer

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)

