import streamlit as st
from chatbot import ChatBot
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

@st.cache_resource
def load_chatbot():
    bot = ChatBot()
    bot.load_documents()
    return bot

chatbot = load_chatbot()

st.title("📄 Document Chatbot with Appointment Booking")
st.caption("Tip: Say 'I want to be contacted' or 'Book appointment' to test forms")

# File uploader section
st.sidebar.header("Document Upload")
uploaded_files = st.sidebar.file_uploader(
    "Upload documents (PDF or TXT)",
    type=["pdf", "txt"],
    accept_multiple_files=True
)

if uploaded_files:
    documents_dir = Path("documents")
    documents_dir.mkdir(parents=True, exist_ok=True)
    
    for uploaded_file in uploaded_files:
        # Save file to documents directory
        file_path = documents_dir / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.sidebar.success(f"Saved {uploaded_file.name} to documents folder")
    
    # Reload documents after upload
    chatbot.load_documents()

# Display form state in sidebar
if chatbot.form_handler.state.current_form:
    st.sidebar.subheader("Current Form Status")
    st.sidebar.write(f"Form Type: {chatbot.form_handler.state.current_form.value}")
    st.sidebar.write("Collected Data:", chatbot.form_handler.state.collected_data)
    st.sidebar.write("Next Field:", 
                   chatbot.form_handler.state.required_fields[chatbot.form_handler.state.current_field_index]
                   if chatbot.form_handler.state.current_field_index < len(chatbot.form_handler.state.required_fields)
                   else "All fields collected")

# View contacts button
if st.sidebar.button("View All Contacts"):
    try:
        from storage import JSONStorage
        storage = JSONStorage()
        contacts = storage.load_all_contacts()
        st.sidebar.subheader("Saved Contacts")
        if contacts:
            for contact in contacts:
                with st.sidebar.expander(f"{contact['name']} - {contact.get('appointment_date', 'No appointment')}"):
                    st.json(contact)
        else:
            st.sidebar.write("No contacts saved yet")
    except Exception as e:
        st.sidebar.error(f"Error loading contacts: {e}")

# Chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        response = chatbot.process_message(prompt)
        st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})