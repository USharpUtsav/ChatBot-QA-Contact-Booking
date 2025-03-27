from typing import Dict, Any
from langchain.agents import tool
from langchain.agents import AgentExecutor
from langchain.agents import create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from document_ques_ans import DocumentChatbot
from form_handlers import FormHandler, FormType
from models import ContactInfo
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatBot:
    def __init__(self):
        self.document_qa = DocumentChatbot()
        self.form_handler = FormHandler()
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)
        self._initialize_tools()
        self.agent = self._create_agent()
        self.chat_history = []
    
    def _initialize_tools(self):
        """Initialize all tools before agent creation"""
        
        @tool
        def answer_from_documents(question: str) -> str:
            """Answers questions from documents. Use this for any factual questions."""
            try:
                doc_answer = self.document_qa.answer_question(question)
                if doc_answer and len(doc_answer.strip()) > 20:
                    return f"From documents: {doc_answer}"
                return "I couldn't find a clear answer in the documents."
            except Exception as e:
                logger.error(f"Error answering question: {e}")
                return "Sorry, I encountered an error searching the documents."

        @tool
        def start_contact_form(dummy: str = "") -> str:
            """Use when user asks to be contacted, called, or wants someone to reach out"""
            return self.form_handler.start_form(FormType.CONTACT)

        @tool
        def start_appointment_form(dummy: str = "") -> str:
            """Use when user wants to book, schedule, or make an appointment"""
            return self.form_handler.start_form(FormType.APPOINTMENT)

        self.answer_from_documents_tool = answer_from_documents
        self.start_contact_form_tool = start_contact_form
        self.start_appointment_form_tool = start_appointment_form
        
        self.tools = [
            self.answer_from_documents_tool,
            self.start_contact_form_tool,
            self.start_appointment_form_tool
        ]
    
    def _create_agent(self) -> AgentExecutor:
        """Create the LangChain agent with proper tool definitions"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful assistant with THREE capabilities:
            1. FORM HANDLING (highest priority):
               - Contact collection when user asks to be called/contacted
               - Appointment booking when scheduling is mentioned
            2. DOCUMENT ANSWERS:
               - Only for specific questions about uploaded files
            3. GENERAL KNOWLEDGE:
               - When neither forms nor documents apply"""),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        agent = create_tool_calling_agent(
            self.llm,
            self.tools,
            prompt
        )
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True)
    
    def process_message(self, user_input: str) -> str:
        """Process a user message with proper form handling priority"""
        # 1. First check if we're already in a form
        if self.form_handler.state.current_form:
            return self._handle_form_input(user_input)
        
        # 2. Check for form triggers before document search
        user_input_lower = user_input.lower()
        contact_triggers = [
            "contact me", "call me", "reach out", 
            "get in touch", "callback", "i want to be contacted"
        ]
        appointment_triggers = [
            "book", "appointment", "schedule", 
            "meeting", "set up a meeting"
        ]
        
        if any(trigger in user_input_lower for trigger in contact_triggers):
            return self.start_contact_form_tool.invoke({"dummy": ""})
        elif any(trigger in user_input_lower for trigger in appointment_triggers):
            return self.start_appointment_form_tool.invoke({"dummy": ""})
        
        # 3. Only after checking forms, try document search
        try:
            doc_response = self.document_qa.answer_question(user_input)
            if doc_response and len(doc_response.strip()) > 20:
                self.chat_history.extend([
                    HumanMessage(content=user_input),
                    AIMessage(content=doc_response)
                ])
                return doc_response
        except Exception as e:
            logger.error(f"Error in direct document query: {e}")
        
        # 4. Fall back to general knowledge if needed
        try:
            response = self.agent.invoke({
                "input": user_input,
                "chat_history": self.chat_history
            })
            return response["output"]
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return "Sorry, I encountered an error processing your request."
    
    def _handle_form_input(self, user_input: str) -> str:
        """Handle form input processing"""
        form_response = self.form_handler.process_input(user_input)
        
        if form_response["status"] == "complete":
            self.chat_history.extend([
                HumanMessage(content=user_input),
                AIMessage(content=form_response["message"])
            ])
            return form_response["message"]
        elif form_response["status"] == "error":
            return form_response["prompt"]
        else:  # in_progress
            return form_response["prompt"]
    
    def load_documents(self, folder_path="documents"):
        """Load documents into the QA system"""
        self.document_qa.load_documents(folder_path)