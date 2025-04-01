import streamlit as st
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_community.vectorstores import FAISS
import json
from langchain.prompts import PromptTemplate


# === Конфигурация Azure ===
embeddings = AzureOpenAIEmbeddings(
    api_key=st.secrets["AZURE_EMBEDDINGS_API_KEY"],
    azure_endpoint=st.secrets["AZURE_EMBEDDINGS_ENDPOINT"],
    deployment="text-embedding-ada-002",
    api_version="2023-05-15"
)


# Инструкция модели (как вести себя AI-риэлтору)
system_prompt = """
Eres un asistente virtual de la municipalidad de Esmeraldas. Tu tarea es responder preguntas relacionadas con servicios públicos, trámites, documentos, normativas y eventos municipales.

Tus responsabilidades:
- Responde de manera clara, formal y útil.
- Usa solo la información contenida en el contexto.
- Si no tienes información suficiente, sugiere consultar con un funcionario o visitar la página correspondiente.
- No inventes información. Sé transparente si no sabes algo.
- Ayuda a navegar los documentos oficiales y entender los procedimientos.

Historial del diálogo:
{chat_history}

Contexto municipal:
{context}

Pregunta del ciudadano: {question}
Respuesta del asistente municipal:

"""


llm = AzureChatOpenAI(
    api_key=st.secrets["AZURE_OPENAI_API_KEY"],
    azure_endpoint=st.secrets["AZURE_OPENAI_ENDPOINT"],
    azure_deployment="gpt-4",
    api_version="2024-02-15-preview"
)


# Загрузка FAISS и метаданные
index = FAISS.load_local("esm_faiss", embeddings, allow_dangerous_deserialization=True)


with open("esm_metadata.json", "r", encoding="utf-8") as file:
    metadata = json.load(file)


# Инициализация памяти в сессии Streamlit
if "memory" not in st.session_state:
    st.session_state["memory"] = ConversationBufferMemory(
        memory_key="chat_history",
        input_key="question",
        output_key="answer",
        return_messages=True
    )


template = """
Eres un asistente virtual de la municipalidad de Esmeraldas. Tu tarea es responder preguntas relacionadas con servicios públicos, trámites, documentos, normativas y eventos municipales.

Tus responsabilidades:
- Responde de manera clara, formal y útil.
- Usa solo la información contenida en el contexto.
- Si no tienes información suficiente, sugiere consultar con un funcionario o visitar la página correspondiente.
- No inventes información. Sé transparente si no sabes algo.
- Ayuda a navegar los documentos oficiales y entender los procedimientos.

Historial del diálogo:
{chat_history}

Contexto municipal:
{context}

Pregunta del ciudadano: {question}
Respuesta del asistente municipal:

"""

PROMPT = PromptTemplate(
    input_variables=["context", "chat_history", "question"],
    template=template
)



qa = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=index.as_retriever(search_kwargs={"k": 10}),
    memory=st.session_state["memory"],
    combine_docs_chain_kwargs={"prompt": PROMPT}
)


# Визуальная часть Streamlit
st.set_page_config(page_title="AI Vicko", page_icon="")


# CSS стили интерфейса
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    padding-bottom: 60px;
}

[data-testid="stSidebar"] {
    background-color: transparent !important;
}

div.stTextInput {
    position: fixed !important;
    bottom: 20px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    width: 60% !important;
    background-color: #262730 !important;
    padding: 10px !important;
    border-radius: 10px !important;
    z-index: 1000;
}
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;700&display=swap');

        * {
            font-family: 'Inter', sans-serif !important;
        }
[data-testid="stVerticalBlock"] {
    flex-grow: 1;
    overflow-y: auto;
}
</style>
""", unsafe_allow_html=True)



# Название приложения
st.sidebar.markdown("# 🏖️ Vicko AI")


# Основной контейнер для вывода ответов
content_container = st.container()


# Поле ввода
query = st.chat_input("Qué quieres saber?")


# Обработка запросов и отображение ответов
if query:
    result = qa({"question": query})

    with content_container:
        st.subheader("La respuesta del asistente.:")
        st.write(result["answer"])

        # Скрытая история диалога
        with st.expander("💬 Historia del diálogo"):
            for message in st.session_state["memory"].chat_memory.messages:
                role = "Tú" if message.type == "human" else "AI"
                st.markdown(f"**{role}:** {message.content}")
