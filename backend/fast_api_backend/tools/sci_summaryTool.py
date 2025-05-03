import os
import json
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader,  PDFMinerLoader, PyMuPDFLoader
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
           Include: 
            **Authors:** Extract author names.
            - **DOI:** Extract the DOI of the paper.
            - **Title:** Extract the title of the paper.
            - **Abstract:** Extract the paper abstract.
            - **Research Problem:** Define the research problem being addressed.
            - **Objectives:** Describe the research objectives.
            - **Methodology:** Summarize the methodology used.
            - **Key Findings:** Summarize major findings.
            - **Limitations:** List study limitations.
            - **Gaps in Literature:** Highlight knowledge gaps.
            - **Future Research Directions:** Suggest further research areas.
            - **Key Terms:** Extract main terms.
            - **Summary:** comprehensive  summary that encapsulates the entire document's main findings, methodology,
                results, and implications of the study. Ensure that the summary is written in a manner that retains the core insights and nuances
                of the original paper. Include ALL key terms, definitions, descriptions, points of interest
                statements of facts and concepts, and provide any and all necessary context
                or background information. The summary should serve as a standalone piece that gives readers a comprehensive understanding
                of the paper's significance without needing to read the entire document. Be as THOROUGH and DETAILED as possible.Summaries
                There should be several sections of the summary that capture each of the key findings and concepts in the paper 
           - **The summary MUST be long enough to capture ALL information in the document:
"{context}"
THOROUGH STRUCTURED SUMMARY:"""


extraction_prompt_template = """
You are an expert researcher. Your task is to extract structured information from the given scientific paper summary.
You MUST return a JSON-style dictionary with the following keys:

{
    "authors": "Extracted AUTHORS",
    "abstract": "Extracted ABSTRACT",
    "research_problem": "Extracted RESEARCH PROBLEM",
    "objectives": "Extracted OBJECTIVES",
    "methodology": "Extracted METHODOLOGY",
    "findings": "Extracted FINDINGS",
    "limitations": "Extracted LIMITATIONS",
    "gaps": "Extracted GAPS IN LITERATURE",
    "future_work": "Extracted FUTURE RESEARCH DIRECTIONS",
    "keywords": ["Extracted", "KEY", "TERMS"]
    "summary": " Exyracted  detailed thourugh SUMMARY
}

ONLY return a valid dictionary. Do NOT include extra text or formatting.

**Summary:** {context}
"""
prompt = PromptTemplate.from_template(prompt_template)
new_prompt = ChatPromptTemplate.from_messages(
   [("system", prompt_template)]
)

extraction_prompt = ChatPromptTemplate.from_messages([("system", extraction_prompt_template)])

class SciDocSummaryInput(BaseModel):
   """Input schema for DocSummaryTool."""
   docs_path: str = Field(..., description="Path to the folder containing documents to summarize.")
   summaries_path: str = Field(..., description="Path to save the generated summaries.")

class SciDocSummaryTool(BaseTool):
   name: str = "Scientific Document_Summary"
   description: str = "Summarizes research papers with structured sections."
   args_schema: Type[BaseModel] = SciDocSummaryInput

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
            loader = PyMuPDFLoader(full_file_path)
          elif file_Name.endswith('.docx'):
            loader = Docx2txtLoader(file)
          else:
            logging.warning(f'The document format: {file_Name} is not supported!') 
            continue
          #loader = PyPDFLoader(full_file_path)
          document = loader.load()

          if isinstance(document, list):
            for page in document:
                 if hasattr(page, "page_content"):
                     text += page.page_content + "\n"
                 else:
                     logging.warning(f"Missing page content in {file_Name}")
          else:
              logging.error(f"Unexpected format for {file_Name}. Expected a list of pages.")
                 
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
          
            
            
          new_file_name = file_Name.strip(".pdf")
          chain = create_stuff_documents_chain(llm_gpt4o, new_prompt)
          summary = chain.invoke({"context":sem_chunksCD})

          extraction_chain = create_stuff_documents_chain(llm_gpt4o, extraction_prompt)
          try:
                extracted_data_json = extraction_chain.invoke({"context": summary})
                extracted_data = json.loads(extracted_data_json)  # ✅ Ensure valid JSON parsing
          except Exception as e:
                logging.warning(f"Extraction failed for {file_Name}: {e}")
                extracted_data = {} 

          structured_summary = {
                "title": new_file_name,
                "summary": summary,
                "authors": extracted_data.get("authors", "Unknown"),
                "abstract": extracted_data.get("abstract", "Not provided"),
                "research_problem": extracted_data.get("research_problem", "Not provided"),
                "objectives": extracted_data.get("objectives", "Not provided"),
                "methodology": extracted_data.get("methodology", "Not provided"),
                "findings": extracted_data.get("findings", "Not provided"),
                "limitations": extracted_data.get("limitations", "Not provided"),
                "gaps": extracted_data.get("gaps", "Not provided"),
                "future_work": extracted_data.get("future_work", "Not provided"),
                "keywords": extracted_data.get("keywords", []),
                "path": full_file_path,
            }

          summaries.append(structured_summary)   
          



          #summaries.append({"title": new_file_name, "summary":summary, "path":full_file_path})
          with open('summaries.json', 'w') as file:
               json.dump(summaries, file)  # Saving the list as JSON
          with open(f'{summaries_path}\{new_file_name}_Summary.txt', "a") as file:
               file.writelines(summary)
              #append these to event log:
          logging.info("Summary written: ", new_file_name)
          logging.info(f"Summary completed for file: {file_Name} ")
        logging.info("Summarization of all files completed")
        return summaries
   
   
sci_doc_summary_tool = SciDocSummaryTool()