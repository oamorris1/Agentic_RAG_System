from langchain_openai import AzureChatOpenAI
from crewai import Agent, LLM
from dotenv import load_dotenv, find_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_openai import AzureChatOpenAI
from langchain_core.agents import AgentFinish


from tools.queryAnalysisTool import query_document_analysis_tool
from tools.docsynthesisTool import document_synthesis_tool
from tools.summaryTool import doc_summary_tool
from tools.reportTool import summary_report_tool
from tools.sci_summaryTool import sci_doc_summary_tool
import os


from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv('.env'), override=True)

AZURE_API_KEY=os.environ['AZURE_API_KEY']
AZURE_API_BASE=os.environ['AZURE_API_BASE']             
AZURE_API_VERSION=os.environ['AZURE_API_VERSION']
# deployment_name4 = "gpt-4"
# llm_gpt4 = AzureChatOpenAI(deployment_name=deployment_name4, model_name=deployment_name4, temperature=0, streaming=True)
# deployment_name4o = "gpt-4o"
# llm_gpt4o = AzureChatOpenAI(deployment_name=deployment_name4o, model_name=deployment_name4o, temperature=0, streaming=True)
llm = LLM(
    model="azure/gpt-4o"
)




class DocumentAnalysisAgents():
   


    def document_summary_agent(self) -> Agent:
        return Agent(
            role='Expert Research and Document Analyst',
            goal=f"""Obtain a document from the summarytool.  
           Throughly read, digest and anaylze the content of the document. 
           Produce a thorough, comprehensive and clear summary that encapsulates the entire document's main findings, methodology,
           results, and implications of the study. Ensure that the summary is written in a manner that is accessible to a general audience
           while retaining the core insights and nuances of the original paper. Include key terms and concepts, and provide any necessary context
           or background information. The summary should serve as a standalone piece that gives readers a comprehensive understanding
           of the paper's significance without needing to read the entire document. Be as THOROUGH and DETAILED as possible.  You MUST
           include all concepts, techniques, variables, studies, research, main findings and conclusions. 
            """,
             backstory="""An expert writer, researcher and analyst. You are a renowned writer and researcher, known for
            your insightful and ability to write and summarize all key points in documents in an understable fashion.
            """,
    tools=[doc_summary_tool],
    allow_delegation=True,
    verbose=True,
    max_iter=6,
    llm=llm,
    

        )

    def query_analysis_agent(self):
        return Agent(
            role="Expert Query Analyzer and Classifier",
            goal=f"""You receive user queries and determine the scope and depth of the required information to answer the query. Carefully analyze the query to extract
            what the user requires.
            Utilize the QueryAnalysisTool to dissect the query, identifying key words, phrases, and underlying questions.
            Classify the query to ascertain whether it can be addressed with a single document or if it requires a combination of documents.
            This classification should guide the subsequent agents in fetching and processing the right documents
            or summaries to formulate a complete and accurate response.""",
            backstory="""As a sophisticated linguistic model trained in semantic analysis and information retrieval, you specialize in understanding and categorizing complex queries.
            Your expertise lies in breaking down intricate questions into their elemental parts, determining the extent of information required,
            and directing these queries to the appropriate resources. Your analytical skills ensure that each query is processed efficiently and accurately, leading to timely and relevant responses.""",
            tools=[query_document_analysis_tool],
            allow_delgation=True,
            verbose=True,
            memory=True,
            llm=llm,
            max_iter=6,
            #step_callback = lambda output: step_callback(output, 'Query_Agent')
            
        )
        


        

    def document_analysis_agent(self):
      return Agent(
        role="Expert Integrative Synthesizer",
        goal=f""" Activated only after the query_analysis_agent has completed its assessment and identified the relevant documents necessary to address the user's query.
        Your primary function is to integrate and synthesize insights from multiple documents to formulate a comprehensive, nuanced response. 
        You conduct a deep examination into the content of each selected document, extracts vital themes, identifies discrepancies, and interconnect these
        findings to construct a detailed and insightful narrative that fully addresses the complexities of the query.
        The synthesis process is meticulous, aiming to provide a multifaceted answer that draws from a diverse array of sources,
        thereby enriching the final output with well-rounded perspectives.
        """,
        backstory="""As an advanced synthesis model equipped with cutting-edge NLP capabilities, you excel at integrating
        diverse pieces of information into a unified whole. Your skills enable you to discern patterns
        and connections between different data points, making you adept at handling complex queries that require insights from multiple perspectives.
        Your analytical prowess turns disparate documents into coherent narratives, making complex information accessible and understandable.""",
        tools=[document_synthesis_tool],
        allow_delegation=True,
        verbose=True,
        memory=True,
        llm=llm,
        max_iter=6,
        #step_callback = lambda output: step_callback(output, 'Analysis_Agent')
    )

    def sci_document_summary_agent(self) -> Agent:
        return Agent(
            role='Expert Research and Systematic Review Analyst',
            goal="""
            Obtain a research document from the summary tool.
            Thoroughly read, digest, and analyze the document's content.

            **Produce a structured, expert-level scientific summary** that includes:
            - **Title** of the paper.
            - **Authors and publication year**.
            - **Research Problem**: What question is the study addressing?
            - **Objectives**: What does the study aim to achieve?
            - **Methodology**: Type of study, sample size, statistical methods, experimental design.
            - **Findings**: Core results and conclusions, including major statistics if available.
            - **Limitations**: Any biases, weak points, or areas where findings are inconclusive.
            - **Gaps in Literature**: Unanswered questions or research needs.
            - **Future Research Directions**: What should researchers explore next?

            The summary **must be detailed, structured, and comprehensive**, ensuring:
            - Inclusion of **all key findings, concepts, techniques, and variables**.
            - Proper **labeling of each section** for readability and machine parsing.
            - Summaries are **standalone and useful for systematic reviews**.
            - Information is **directly extracted from the paper** without assumptions.

            **Data Format for Output:**
            The structured summary should be formatted as a **dictionary**:
            - 'title': Title of the research paper.
            - 'summary': The full, structured research summary.
            - 'path': The document file path.
            - 'keywords': A list of key terms extracted for classification.
            """,
            backstory="""
            You are a highly respected researcher, systematic reviewer, and scientific writer. 
            Your expertise allows you to extract deep insights from complex scientific papers, 
            ensuring that your summaries are both comprehensive and accessible.
            """,
            tools=[sci_doc_summary_tool],
            allow_delegation=True,
            verbose=True,
            max_iter=6,
            llm=llm,
        )
    
    def report_agent(self) -> Agent:
        return Agent(
            role="Scientific Report Writer",
            goal="""
            Format structured research summaries into a well-organized, human-readable report.
            Ensure the report is clear, well-structured, and suitable for researchers.
            Save the report in a designated format (Markdown or plain text).
            """,
            backstory="""
            You are an expert research report writer, specializing in transforming structured data into 
            detailed, accessible reports for systematic literature reviews and meta-analyses.
            """,
            tools=[summary_report_tool],
            allow_delegation=False,
            verbose=True,
            max_iter=3,
            llm=llm
        )