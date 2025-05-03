
import re
from typing import Dict, List, Type
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader, PDFMinerLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_experimental.text_splitter import SemanticChunker
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import logging
from dotenv import load_dotenv, find_dotenv

# Load environment variables
load_dotenv(find_dotenv('.env'))

# Initialize embeddings and LLMs
embeddings = AzureOpenAIEmbeddings(deployment="text-embedding-ada-002", model="text-embedding-ada-002", chunk_size=10)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
semantic_text_splitter = SemanticChunker(embeddings, breakpoint_threshold_type="interquartile")

deployment_name4 = "gpt-4o"
llm_gpt4o = AzureChatOpenAI(deployment_name=deployment_name4, model_name=deployment_name4, temperature=0, streaming=True)

# Define the input schema for the tool
class DocumentSynthesisInput(BaseModel):
    query: str = Field(..., description="The user query to be answered.")
    documents: List[Dict] = Field(..., description="List of dictionaries with document titles and paths.")

class DocumentSynthesisTool(BaseTool):
    """
    A tool for synthesizing single or multiple documents by extracting key information, themes, and narratives.
    """
    name: str = "Document_Synthesis"
    description: str = "Synthesizes information from provided documents based on a user query."
    args_schema: Type[BaseModel] = DocumentSynthesisInput

    def _run(self, query: str, documents: List[Dict]) -> str:
        """
        Synchronously synthesizes information from the provided documents.
        """
        synthesized_information = ""
        for document in documents:
            title = document.get('title')
            path = document.get('path')

            if not title or not path:
                logging.warning("Document is missing title or path.")
                continue

            logging.info(f"Processing document: {title}")
            try:
                # Load the document based on its file type
                if path.endswith(".txt"):
                    loader = TextLoader(path)
                elif path.endswith('.pdf'):
                    loader = PDFMinerLoader(path)
                elif path.endswith('.docx'):
                    loader = Docx2txtLoader(path)
                else:
                    logging.warning(f"Unsupported file type for document: {title}")
                    continue

                # Load and split the document
                document_content = loader.load()
                text = "".join([page.page_content for page in document_content])
                text = self._clean_text(text)

                # Split the document into chunks
                sem_chunks = semantic_text_splitter.create_documents([text])

                # Create a vector store and retriever
                vector_store = FAISS.from_documents(sem_chunks, embeddings)
                retriever = vector_store.as_retriever()

                # Use retrieval-based QA to generate synthesis
                qa_chain = RetrievalQA.from_chain_type(llm=llm_gpt4o, retriever=retriever)
                result = qa_chain.invoke({"query": query})

                synthesized_information += f"Title: {title}\n{result['result']}\n\n"

            except Exception as e:
                logging.error(f"Error processing document {title}: {e}")

        return synthesized_information

    def _clean_text(self, text: str) -> str:
        """
        Cleans the input text by removing unwanted characters and whitespace.
        """
        text = text.replace('\t', ' ')
        text = text.replace("\n", ' ')
        text = re.sub(" +", " ", text)
        text = re.sub("\u2022", "", text)
        text = re.sub(r"\.{3,}", "", text)
        return text

# Instantiate the tool
document_synthesis_tool = DocumentSynthesisTool()

