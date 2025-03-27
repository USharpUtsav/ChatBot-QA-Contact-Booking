# ChatBot-QA-Contact-Booking
A chatbot build with Langchain and Gemini that covers 3 logic:-QA system, Contact Form and Booking Appointment Form

# Document Chatbot with Appointment Booking

## Task Completion Summary

I've successfully implemented all requirements from the ML task:

### Core Features Implemented

**Document Q&A System**  
- Built using LangChain and Gemini 
- Supports PDF and TXT documents
- Automatic document indexing upon upload
- Answers questions using document content

**Conversational Forms**  
- Contact collection form (name, email, phone)
- Appointment booking form (with date scheduling)
- Context-aware form handling within chat flow

**Advanced Form Features**  
- Phone number validation with country code support
- Email format validation
- Natural language date parsing ("next Monday" → YYYY-MM-DD)
- Real-time input validation

**Technical Implementation**  
- Integrated form handling with LangChain agents
- Used Pydantic for robust data validation
- Implemented FAISS vector store for document search
- Added proper error handling throughout

**Storage System**  
- All contact/appointment data saved to JSON
- Persistent storage between sessions
- View all contacts functionality

### How to Run
-pip install -r requirements.txt
-streamlit run app.py
