import os
import json
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader,  PDFMinerLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_experimental.text_splitter import SemanticChunker

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
from langchain.chains.summarize import load_summarize_chain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings
import re
import tiktoken
import logging
from job_manager import append_event, jobs, jobs_lock, Event
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv('.env'), override=True)

embeddings = AzureOpenAIEmbeddings(deployment="text-embedding-ada-002", model="text-embedding-ada-002", chunk_size=10)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50, length_function=len)
sem_text_splitter = SemanticChunker(
   embeddings, breakpoint_threshold_type="interquartile"
)
deployment_name4 = "gpt-4"
llm_gpt4 = AzureChatOpenAI(deployment_name=deployment_name4, model_name=deployment_name4, temperature=0, streaming=True)
deployment_name4o = "gpt-4o"
llm_gpt4o = AzureChatOpenAI(deployment_name=deployment_name4o, model_name=deployment_name4o, temperature=0, streaming=True)





def embedding_cost(chunks):
    enc = tiktoken.encoding_for_model("text-embedding-ada-002")
    total_tokens = sum([len(enc.encode(page.page_content)) for page in chunks])
    # print(f'Total tokens: {total_tokens}')
    # print(f'Cost in US Dollars: {total_tokens / 1000 * 0.0004:.6f}')
    return total_tokens
 
prompt_template = """
            
           Throughly read, digest and anaylze the content of the document. 
           Produce a thorough, comprehensive  summary that encapsulates the entire document's main findings, methodology,
           results, and implications of the study. Ensure that the summary is written in a manner that retains the core insights and nuances
             of the original paper. Include ALL key terms, definitions, descriptions, points of interest
            statements of facts and concepts, and provide any and all necessary context
           or background information. The summary should serve as a standalone piece that gives readers a comprehensive understanding
           of the paper's significance without needing to read the entire document. Be as THOROUGH and DETAILED as possible.  You MUST
           include all concepts, techniques, variables, studies, research, main findings, key terms and definitions and conclusions. 
           The summary MUST be long enough to capture ALL information in the document:
"{context}"
THOROUGH STRUCTURED SUMMARY:"""

prompt = PromptTemplate.from_template(prompt_template)
new_prompt = ChatPromptTemplate.from_messages(
   [("system", prompt_template)]
)

class DocSummaryInput(BaseModel):
   """Input schema for DocSummaryTool."""
   docs_path: str = Field(..., description="Path to the folder containing documents to summarize.")
   summaries_path: str = Field(..., description="Path to save the generated summaries.")

class DocSummaryTool(BaseTool):
   name: str = "Document_Summary"
   description: str = "Use this tool to summarize documents in a specified folder."
   args_schema: Type[BaseModel] = DocSummaryInput

   def _run(self, docs_path: str, summaries_path: str):
       
        
        summaries =[]
        
        for file_Name in os.listdir(docs_path):
          text="" 
          full_file_path = os.path.join(docs_path, file_Name)
          print("file name: ", file_Name)
          print("path : ", full_file_path)
          #  code to handle other files than pdf  
          if file_Name.endswith(".txt"):
             loader = TextLoader(full_file_path) 
          elif file_Name.endswith('.pdf'):
            #print("Preparing to sumarize: ", file_Name) 
            #loader = PyPDFLoader(full_file_path)
            loader = PDFMinerLoader(full_file_path)
          elif file_Name.endswith('.docx'):
            loader = Docx2txtLoader(file)
          else:
            logging.warning(f'The document format: {file_Name} is not supported!') 
            continue
          #loader = PyPDFLoader(full_file_path)
          document = loader.load()
          for page in document:

            text += page.page_content
          #print("Preparing text for: ", file_Name) 
          text = text.replace('\t', ' ')
          text = text.replace('\t', ' ')
          text= text.replace("\n", ' ')
          text = re.sub(" +", " ", text)
          text = re.sub("\u2022", "", text)
          text = re.sub(" +", " ", text)
          text = re.sub(r"\.{3,}", "", text)
          #print("This is the text: ", text, end='\n')
          chunks = text_splitter.create_documents([text])
          # split the text into chunks with semantic chunker
          sem_chunksCD = sem_text_splitter.create_documents([text])
          #print("Prepared semcd chunks for: ", file_Name) 
          num_tokens = embedding_cost(sem_chunksCD)
          #print("Number of tokens: ", num_tokens, "for: ", file_Name)
          
            
            
        
          chain = create_stuff_documents_chain(llm_gpt4o, new_prompt)
          summary = chain.invoke({"context":sem_chunksCD})
               
          new_file_name = file_Name.strip(".pdf")
          summaries.append({"title": file_Name, "summary":summary, "path":full_file_path})
          with open('summaries.json', 'w') as file:
               json.dump(summaries, file)  # Saving the list as JSON
          with open(f'{summaries_path}\{new_file_name}_Summary.txt', "a") as file:
               file.writelines(summary)
              #append these to event log:
          logging.info("Summary written: ", new_file_name)
          logging.info(f"Summary completed for file: {file_Name} ")
        logging.info("Summarization of all files completed")
        return summaries
   
   
doc_summary_tool = DocSummaryTool()