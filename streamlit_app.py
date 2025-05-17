import streamlit as st
from openai import OpenAI
import fitz  # PyMuPDF
import os
import chat_openrouter
import embedder

st.set_page_config(layout="wide", page_title="OpenRouter chatbot app")
st.title("OpenRouter chatbot app")

# API key and base URL from secrets
api_key, base_url = st.secrets["API_KEY"], st.secrets["BASE_URL"]
selected_model = "google/gemma-3-1b-it:free"

# Initialize chat session state
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

selected_model = "mistralai/mistral-7b-instruction:free"
model = ChatOpenRouter(model_name=selected_model)

def answer_question(question, documents, model):
    context = "\n\n".join([doc["text"] for doc in documents])
    prompt = ChatPromptTemplate.from_template(template)
    chain = prommpt | model
    return chain.invoke({"question": question, "context": context})

# File upload for PDF
uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file:
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        pdf_text = ""
        for page in doc:
            pdf_text += page.get_text()
    st.text_area("Extracted PDF Text", pdf_text, height=300)
    
    # Option to append PDF text to conversation
    if st.button("Send PDF content to assistant"):
        st.session_state.messages.append({"role": "user", "content": pdf_text})
        st.chat_message("user").write(pdf_text)
        client = OpenAI(api_key=api_key, base_url=base_url)
        response = client.chat.completions.create(
            model=selected_model,
            messages=st.session_state.messages
        )
        msg = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)

# Display past messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Chat input
if prompt := st.chat_input():
    if not api_key:
        st.info("Invalid API key.")
        st.stop()
    client = OpenAI(api_key=api_key, base_url=base_url)
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response = client.chat.completions.create(
        model=selected_model,
        messages=st.session_state.messages
    )
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)
