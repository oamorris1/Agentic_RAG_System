from job_manager import append_event
import logging
from agents import DocumentAnalysisAgents
from tasks import AnalyzeDocumentsTasks
from crewai import Crew
from langchain_openai import AzureChatOpenAI
from crewai import Agent, LLM
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv('.env'), override=True)
deployment_name4o = "gpt-4o"
#llm = AzureChatOpenAI(deployment_name=deployment_name4o, model_name=deployment_name4o, temperature=0, streaming=True)
llm = LLM(
    model="azure/gpt-4o"
)
class DocumentAnalysisCrew:
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.crew = None

    def setup_crew(self,user_query, docs_path, summaries_path, summaries_path_json):
        logging.info(f"Setting up crew for {self.job_id} for document analysis")


        #agents
        agents = DocumentAnalysisAgents()
        summarizer_agent = agents.document_summary_agent()
        analyzer_agent   = agents.query_analysis_agent()
        docs_analyzer_agent = agents.document_analysis_agent() 

        #tasks
        tasks = AnalyzeDocumentsTasks(job_id=self.job_id)
        doc_sum_task = tasks.summarize_document(summarizer_agent, docs_path)
        analyze_query_task = tasks.analyze_document_query(analyzer_agent, summaries_path_json, user_query )
        docs_synthesizer_task = tasks.document_sythesis(docs_analyzer_agent, user_query)

        #create crew
        self.crew = Crew(
            agents=[summarizer_agent, analyzer_agent, docs_analyzer_agent],
            tasks=[doc_sum_task, analyze_query_task, docs_synthesizer_task],
            verbose=True,
            manager_llm=llm
        )

    def kickoff(self):
        #kick off crew
        
        if not self.crew:
            logging.info(f"No crew found for {self.job_id}")
            append_event(self.job_id, "Crew not set up")
            return
        
        append_event(self.job_id, "ANALYSIS CREW STARTED")
        try: 
            logging.info(f"Running crew for job id:  {self.job_id}")
            results = self.crew.kickoff()
            logging.info(f"Crew results for job id {self.job_id}: {results}")
            append_event(self.job_id, "ANALYSIS CREW TASKS COMPLETED")
            return results
        
        except Exception as e:
            append_event(self.job_id, f"An error occurred: {e}")
            return str(e)

class DocumentSummaryCrew:
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.crew = None

    def setup_crew(self, docs_path, summaries_path_json, save_directory):
        logging.info(f"Setting up crew for {self.job_id} for document summarization")


        #agents
        agents = DocumentAnalysisAgents()
        summarizer_agent = agents.sci_document_summary_agent()
        reporter_agent = agents.report_agent()
      

        #tasks
        tasks = AnalyzeDocumentsTasks(job_id=self.job_id)
        sci_doc_sum_task = tasks.sci_summarize_document(summarizer_agent, docs_path)
        reporter_task = tasks.generate_report(reporter_agent, summaries_path_json, save_directory)
        
       

        #create crew
        self.crew = Crew(
            agents=[summarizer_agent, reporter_agent],
            tasks=[sci_doc_sum_task, reporter_task],
            verbose=True,
        )

    def kickoff(self):
        #kick off crew
        
        if not self.crew:
            logging.info(f"No crew found for {self.job_id}")
            append_event(self.job_id, "Crew not set up")
            return
        
        append_event(self.job_id, "SUMMARY CREW STARTED")
        try: 
            logging.info(f"Running crew for job id:  {self.job_id}")
            results = self.crew.kickoff()
            append_event(self.job_id, "SUMMARY CREW TASKS COMPLETED")
            #print("from crewpy file summary path JSON: ", summaries_path_json)
            return results
        
        except Exception as e:
            append_event(self.job_id, f"An error occurred: {e}")
            return str(e)

