from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import FAISS
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging
from dotenv import load_dotenv

load_dotenv()


logging.getLogger("pypdf").setLevel(logging.ERROR) 

class DocumentChatbot:
    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.vectorstore = None

    def load_documents(self, folder_path="documents"):
        documents = []
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            if file.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
            documents.extend(loader.load())
        
        # Split text into chunks
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(documents)
        
        # Create vector database
        self.vectorstore = FAISS.from_documents(chunks, self.embeddings)

    def answer_question(self, question):
        if not self.vectorstore:
            return "Please load documents first."
        
        # Search documents
        docs = self.vectorstore.similarity_search(question)
        
        # Generate answer (using Gemini)
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        
        prompt = f"""
        Answer this question based ONLY on the following context:
        {docs}
        
        Question: {question}
        """
        response = llm.invoke(prompt)
        return response.content

# Usage
bot = DocumentChatbot()
bot.load_documents()  
print(bot.answer_question("What is difference between deepseek r1 zero and deepseek r1?"))