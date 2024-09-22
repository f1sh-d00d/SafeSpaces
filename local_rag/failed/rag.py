#local RAG LLM system built mostly by following this guide: https://medium.com/@vndee.huynh/build-your-own-rag-and-run-it-locally-langchain-ollama-streamlit-181d42805895

from langchain_community.vectorstores import Chroma
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain.schema.output_parser import StrOutputParser
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.runnable import RunnablePassthrough
from langchain.prompts import PromptTemplate
from langchain.vectorstores.utils import filter_complex_metadata
from langchain import hub


class ChatFile:
    vector_store = None
    retriever = None
    chain = None

    def __init__(self):
        self.model = ChatOllama(model="llama3.1")
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=100)
        self.prompt = prompt = hub.pull("rlm/rag-prompt-llama3")                                        #https://smith.langchain.com/hub/rlm/rag-prompt-llama3, using this template instead of the one in the Medium article


    def ingest(self, file_path):
        docs = PyPDFLoader(file_path=file_path).load()
        chunks = self.text_splitter.split_documents(docs)
        chunks = filter_complex_metadata(chunks)
        
        vector_store = Chroma.from_documents(documents=chunks, embedding=FastEmbedEmbeddings())
        self.retriever = vector_store.as_retriever(search_type="similarity_score_threshold", search_kwargs={"k":3, "score_threshold": 0.5,},)
        self.chain = ({"context": self.retriever, "question":RunnablePassthrough()}| self.prompt| self.model| StrOutputParser())

    def ask(self, query):
        if not self.chain:
            return "Please add a PDF document."

        return self.chain.invoke(query)

    def clear(self):
        self.vector_store = None
        self.retriever = None
        self.chain = None

