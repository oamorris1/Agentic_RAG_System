from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime
from crewai import Agent, Task, Crew, Process
#from crewai.agents import CrewAgentExecutor
from crewai.project import CrewBase, agent, crew, task
from langchain_openai import AzureChatOpenAI
from pathlib import Path


from job_manager import append_event, jobs, jobs_lock, Event
from models import FinalResult, FinalSummaryResult
import logging
import logging.config
from logging_config import LOGGING_CONFIG
import os
import json

from crew import DocumentSummaryCrew, DocumentAnalysisCrew

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv('.env'), override=True)


AZURE_API_KEY=os.environ['AZURE_API_KEY']
AZURE_API_BASE=os.environ['AZURE_API_BASE']             
AZURE_API_VERSION=os.environ['AZURE_API_VERSION']
logging.config.dictConfig(LOGGING_CONFIG)
os.makedirs("logs", exist_ok=True)
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Models for request validation
class CrewRequest(BaseModel):
    user_query: str
    crew_type: str = None # only needed for full analysis crew

# Initialize resources


summaries_file = "summaries.json"
home = str(Path.home())
docs_path = os.path.join(home, "Desktop/crew_docs/documents")
os.makedirs(docs_path, exist_ok=True)

summaries_path = os.path.join(home, "Desktop/crew_docs/summaries")
os.makedirs(summaries_path, exist_ok=True)
summaries_path_json = os.path.join(os.getcwd(), summaries_file)
summaries_json = os.path.join(os.getcwd(), summaries_file)
print("summaries path JSOn", summaries_path_json)
print("Summarirs_json", summaries_json)
save_directory = os.path.join(home, "Desktop/crew_docs/summary_reports")
os.makedirs(save_directory, exist_ok=True)

# Background task for crew analysis
def kickoff_analysis_crew(job_id: str, user_query: str):
    logging.info(f"Starting crew for job {job_id}")
    try:
        document_analysis_crew = DocumentAnalysisCrew(job_id)
        document_analysis_crew.setup_crew(user_query, docs_path, summaries_path, summaries_path_json)
        crew_output = document_analysis_crew.kickoff()
        logging.info(f"Crew for job {job_id} is complete")
        if crew_output.json_dict:
            final_result_text = json.dumps(crew_output.json_dict, indent=2)
        elif crew_output.pydantic:
            if hasattr(crew_output.pydantic, "model_dump_json"):
                final_result_text = crew_output.pydantic.model_dump_json()
        
        elif crew_output.raw:
            final_result_text = crew_output.raw
        else:
            final_result_text = "No output available"
        final_result = FinalResult(user_query=user_query, result=final_result_text)
        if hasattr(crew_output, 'token_usage'):
            token_usage = crew_output.token_usage
            # Convert UsageMetrics to a dictionary if needed
            if isinstance(token_usage, dict):
                token_usage_text = json.dumps(token_usage, indent=2)
            else:
                # Attempt to convert UsageMetrics object to a dictionary
                token_usage_text = json.dumps(token_usage.__dict__, indent=2)
        else:
            token_usage_text = "No token usage data"
       
        with jobs_lock:
            jobs[job_id].status = 'COMPLETE'
           
            jobs[job_id].result = final_result.model_dump_json()
            jobs[job_id].events.append(Event(
            timestamp=datetime.now(), 
            data=f"Token Usage: {token_usage_text}"
        ))
            jobs[job_id].events.append(Event(timestamp=datetime.now(), data="Crew tasks complete"))
    except Exception as e:
        logging.error(f"Error in kickoff_crew for job {job_id}: {e}")
        append_event(job_id, f"An error occurred: {e}")
        with jobs_lock:
            jobs[job_id].status = 'ERROR'
            jobs[job_id].result = str(e)
def kickoff_summary_crew(job_id: str):
    logging.info(f"Starting crew for job {job_id}")
    try:
        document_summary_crew = DocumentSummaryCrew(job_id)
        document_summary_crew.setup_crew( docs_path, summaries_path_json, save_directory)
        crew_output = document_summary_crew.kickoff()
        logging.info(f"Crew for job {job_id} is complete")
        if crew_output.json_dict:
            final_result_text = json.dumps(crew_output.json_dict, indent=2)
        elif crew_output.pydantic:
            if hasattr(crew_output.pydantic, "model_dump_json"):
                final_result_text = crew_output.pydantic.model_dump_json()
        
        elif crew_output.raw:
            final_result_text = crew_output.raw
        else:
            final_result_text = "No output available"
        final_result = FinalSummaryResult(result=final_result_text)
        if hasattr(crew_output, 'token_usage'):
            token_usage = crew_output.token_usage
            # Convert UsageMetrics to a dictionary if needed
            if isinstance(token_usage, dict):
                token_usage_text = json.dumps(token_usage, indent=2)
            else:
                # Attempt to convert UsageMetrics object to a dictionary
                token_usage_text = json.dumps(token_usage.__dict__, indent=2)
        else:
            token_usage_text = "No token usage data"
       
        with jobs_lock:
            jobs[job_id].status = 'COMPLETE'
           
            jobs[job_id].result = final_result.model_dump_json()
            jobs[job_id].events.append(Event(
            timestamp=datetime.now(), 
            data=f"Token Usage: {token_usage_text}"
        ))
            jobs[job_id].events.append(Event(timestamp=datetime.now(), data="Crew tasks complete"))
    except Exception as e:
        logging.error(f"Error in kickoff_crew for job {job_id}: {e}")
        append_event(job_id, f"An error occurred: {e}")
        with jobs_lock:
            jobs[job_id].status = 'ERROR'
            jobs[job_id].result = str(e)
# Endpoint to initiate the crew task
@app.post("/api/crew")
async def run_crew(request: CrewRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid4())
    logging.info(f"Received request to run crew for job {job_id}")
   

    if request.crew_type == "analysis":
        if not request.user_query:
            raise HTTPException(status_code=400, detail="user_query is required for analysis crew")
        background_tasks.add_task(kickoff_analysis_crew, job_id=job_id, user_query=request.user_query)
    
    elif request.crew_type == "summary":
        background_tasks.add_task(kickoff_summary_crew, job_id=job_id )

    else:
        raise HTTPException(status_code=400, detail="Invalid crew_type. Must be 'analysis' or 'summary'.")

    
    return {"job_id": job_id}

# Endpoint to check job status
@app.get("/api/crew/{job_id}")
async def get_status(job_id: str):
    with jobs_lock:
        job = jobs.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

    try:
        #result_json = json.loads(job.result)
        result_json = json.loads(job.result) if isinstance(job.result, str) else job.result
    except json.JSONDecodeError:
        result_json = job.result

    return {
        "job_id": job_id,
        "status": job.status,
        "result": result_json,
        "events": [{"timestamp": event.timestamp.isoformat(), "data": event.data} for event in job.events]
    }

# Run the FastAPI app
# use command: uvicorn fast_crew_api:app --host 0.0.0.0 --port 3001

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("fast_crew_api:app", host="0.0.0.0", port=3001)