from pathlib import Path

import streamlit as st

from backend.rag_engine import RAGEngine


ROOT = Path(__file__).resolve().parent
KB_PATH = ROOT / "data" / "tollywood_kb.json"


@st.cache_resource
def load_engine():
    return RAGEngine(KB_PATH)


st.set_page_config(
    page_title="Tollywood RAG Chatbot",
    page_icon="T",
    layout="centered",
)

st.title("Tollywood RAG Chatbot")
st.caption("Ask questions about the Telugu film industry, major films, directors, stars, music, and pan-Indian releases.")

engine = load_engine()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hi! Ask me anything about the Tollywood film industry.",
            "sources": [],
        }
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message.get("sources"):
            with st.expander("Sources"):
                for source in message["sources"]:
                    st.markdown(f"**{source['title']}** · {source['category']} · score `{source['score']}`")
                    st.write(source["text"])

sample_questions = [
    "What is Tollywood known for?",
    "Tell me about Baahubali and RRR.",
    "Who are important directors in Telugu cinema?",
    "How did Telugu cinema become pan-Indian?",
]

with st.sidebar:
    st.header("Try a Question")
    for question in sample_questions:
        if st.button(question, use_container_width=True):
            st.session_state.pending_question = question

question = st.chat_input("Ask a Tollywood question...")
if "pending_question" in st.session_state:
    question = st.session_state.pop("pending_question")

if question:
    st.session_state.messages.append({"role": "user", "content": question, "sources": []})
    with st.chat_message("user"):
        st.write(question)

    result = engine.answer(question)
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result["answer"],
            "sources": result["sources"],
        }
    )

    with st.chat_message("assistant"):
        st.write(result["answer"])
        if result["sources"]:
            with st.expander("Sources"):
                for source in result["sources"]:
                    st.markdown(f"**{source['title']}** · {source['category']} · score `{source['score']}`")
                    st.write(source["text"])
