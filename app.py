from dotenv import load_dotenv
import streamlit as st

from chatbot.config import Settings
from chatbot.ollama_service import OllamaService, OllamaServiceError

load_dotenv()


@st.cache_resource
def get_ollama_service(base_url: str, timeout_seconds: int) -> OllamaService:
    return OllamaService(base_url, timeout_seconds=timeout_seconds)


st.set_page_config(page_title="Local Ollama Chatbot")
st.title("Local Ollama Chatbot")
st.caption("Chat with a model running through your configured Ollama endpoint.")
settings = Settings.from_environment()
service = get_ollama_service(
    settings.ollama_base_url,
    settings.chat_request_timeout_seconds,
)

if "messages" not in st.session_state:
    st.session_state.messages = []
if st.session_state.pop("clear_draft_on_rerun", False):
    st.session_state.draft = ""

with st.sidebar:
    st.header("Connection")
    st.caption(settings.ollama_base_url)
    try:
        available_models = service.list_models()
    except OllamaServiceError as error:
        available_models = []
        st.warning(str(error))

    if available_models:
        options = list(available_models)
        if settings.chat_model and settings.chat_model not in options:
            options.insert(0, settings.chat_model)
        default_index = options.index(settings.chat_model) if settings.chat_model in options else 0
        model_name = st.selectbox("Chat model", options, index=default_index)
    else:
        model_name = st.text_input("Chat model", value=settings.chat_model)
        st.caption("Enter a model installed in Ollama, then retry after connecting.")

    if st.button("New chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

with st.form("chat_form", clear_on_submit=False):
    user_prompt = st.text_area("Message", key="draft", disabled=not model_name.strip())
    submitted = st.form_submit_button("Send", disabled=not model_name.strip())

if submitted and user_prompt.strip():
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        try:
            response_text = st.write_stream(
                service.stream_chat(
                    model=model_name,
                    messages=st.session_state.messages[-settings.max_history_messages :],
                )
            )
        except OllamaServiceError as error:
            st.session_state.messages.pop()
            st.error(str(error))
        else:
            st.session_state.messages.append(
                {"role": "assistant", "content": response_text}
            )
            st.session_state.clear_draft_on_rerun = True
            st.rerun()