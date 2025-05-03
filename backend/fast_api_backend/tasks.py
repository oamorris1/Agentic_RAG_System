from crewai import Task, Agent
import logging
from job_manager import append_event
from crewai.tasks.task_output import TaskOutput
from models import FinalResult
import json

class AnalyzeDocumentsTasks():
    def __init__(self, job_id: str):
       self.job_id = job_id

    def append_event_callback(self, task_output: TaskOutput):
       logging.info(f"Appending event for {self.job_id} with output {task_output}")
       # Convert TaskOutput to a string before passing it to append_event

       # Initialize the event data
       event_data = {}
       if isinstance(task_output, TaskOutput):
            # Extract JSON dictionary if available
            if hasattr(task_output, 'json_dict') and task_output.json_dict:
                event_data['json_dict'] = task_output.json_dict

            # Extract Pydantic output if available
            if hasattr(task_output, 'pydantic') and task_output.pydantic:
                event_data['pydantic'] = task_output.pydantic.dict() if hasattr(task_output.pydantic, 'dict') else task_output.pydantic.json()
            
            # Extract raw output if available
            if hasattr(task_output, 'raw') and task_output.raw:
                event_data['Output'] = task_output.raw

            # Extract token usage if available
            if hasattr(task_output, 'token_usage'):
                event_data['token_usage'] = task_output.token_usage

            # Extract task output metadata if available
            if hasattr(task_output, 'tasks_output') and task_output.tasks_output:
                event_data['tasks_output'] = task_output.tasks_output

        # Convert the event data dictionary to a JSON string for logging
       try:
          event_data_json = json.dumps(event_data, indent=2)
       except Exception as e:
          logging.error(f"Error serializing event data for job {self.job_id}: {e}")
          event_data_json = str(event_data)
        
       #append_event(self.job_id, event_data)
       append_event(self.job_id, event_data_json)
       
          
       
    def summarize_document(self, agent: Agent, docs_path):
       try:
        return Task(
            description=f"""
            Obtain a document from the docsummary tool. Conduct a thorough analysis of a document using the Document_Summary tool.
            The documents for summarization are here: {docs_path} 
            Throughly read, digest and anaylze the content of the document. 
            Produce a thorough, comprehensive  summary that encapsulates the entire document's main findings, methodology,
            results, and implications of the study. Ensure that the summary is written in a manner that is accessible to a general audience
            while retaining the core insights and nuances of the original paper. Include ALL key terms, definitions, descriptions, points of interest
              statements of facts and concepts, and provide any and all necessary context
            or background information. Exclude information that is not of techincal relevance such as dedications.
              The summary should serve as a standalone piece that gives readers a comprehensive understanding
            of the paper's significance without needing to read the entire document. Be as THOROUGH and DETAILED as possible.  You MUST
            include all concepts, techniques, variables, studies, research, main findings,  and conclusions. The summary should have 
            each of the aforemenntioned paramters bolded and followed by the cooresponding information that pertains to each respective parameter or concept or finding. Please ensure that each summary ONLY contains information
            contained within the document being summarized. If there is an abstract and methodology list them clearly. You MUST Include and label an introductory statement
            and a conclusion statement that encompasses all findings. 
            The summary MUST be long enough to capture ALL information in the document
            Show the entire summary in your final answer and let the user know the summaries are complete and that you will proceed with the rest of your tasks
            - The input SHOULD NOT be enclosed in triple backticks
            - The input SHOULD NOT have a JSON label.
            - The input SHOULD NOT have a python label 
            """,
            agent=agent,
            async_execution=False,
            expected_output="""
            
            Provide a list of dictionaries. Each dictionary should contain:
            - 'title': The title of the document.
            - 'summary' : A through and detailed summary that captures all of the points in the original document
            - 'path': The file path to the document.
              The list format will facilitate the subsequent processing tasks without needing further parsing. DO NOT create your output as a JSON Object
              The output must be structured as a Python Dictionary.
            """,
            
            callback=self.append_event_callback,

            )
       except Exception as e:
        logging.error(f"Error creating summarize_document task for job {self.job_id}: {e}")
        raise e  # Optional: re-raise the exception if needed
    def analyze_document_query(self, agent, summaries_path_json, query):
     try:
      return Task(
          description=f"""
          Wait until the document_summary_agent has completed their task. Then, using the queryAnalysisTool analyze
          the given user query: {query}
          to ascertain the specific information required from the document summaries found here: {summaries_path_json}.
          - Use the provided summaries_path to access and review document summaries.
          - The input format for the action should be a Python dictionary
          - The input should be a Python dictionary, but it MUST NOT be enclosed in triple backticks or have a JSON label.
          - The output will be a list of dictionaries detailing relevant documents, including titles and paths.
          - Extract key words, phrases, and underlying questions from the user's query using advanced NLP techniques.
          - Match these extracted elements with the information in the document summaries from the summaries loacted in the summaries_path to
            determine which document(s) could potentially answer the query. 
          - The process should be meticulous to ensure that all possible documents that could answer the query are considered,
          - Once the necessary documents have been determined present the final answer as a formatted bulleted list with the name and path of each document in bold and explain
          in detail why these documents were chosen to answer the query. Present the list of documents to the user as a Bulleted list with the name of the document, a
          descrition of its contents and relevancy to the query.  
          - Very Important : You must ensure that the "title" and "path" keys are in lower case when you provide the dictionary to the next agent 
          """,
          agent=agent,
          async_execution=False,  
          expected_output="""
          - Provide a list of dictionaries. Each dictionary should contain:
            - "title": The title of the document.
            - "path": The file path to the document.
            -  Very important that you ensure that "title" and "path" keys are in lower case
            - You MUST structure your output in the form of a list of dictionaries.
            - The input SHOULD NOT be enclosed in triple backticks
            - The input SHOULD NOT have a JSON label.
            - The input SHOULD NOT have a python label
          The list format will facilitate the subsequent processing tasks without needing further parsing.   
          """,
          callback=self.append_event_callback,
        )
     except Exception as e:
        logging.error(f"Error creating analyze_document_query task for job {self.job_id}: {e}")
        raise e


    def document_sythesis(self, agent, query):
        try:
          return Task(
              description=f"""
              Wait until the query_analysis_agent has completed their task. Take the information recived from the query_analysis_agent
              to perform your task.  If it is a single document  use the single document to answer the query: {query}.  If it is multiple documents use all
              of the documents to answer the query.  Do not attempt to verify if the documents are sufficient or if the provided document is comprehensive for the task,
              take the document and path you are given and proceed with the task of using the proivided document or documents to 
              answer the query: '{query}'. 
              This task involves:
              - You must give your output to the document_analysis_agent as a LIST of DICTIONARIES.
              - DO NOT PASS the input as JSON 
              - The input should not be enclosed in triple backticks
              - The input should not have a JSON label.
              - The input should not have a python label
              - Receiving the necessary document paths and titles from the query_analysis_agent to answer the query
              - Analyzing each document  to extract key information, themes, and data points that are directly relevant to the query.
              - Comparing and contrasting the findings across different documents to identify commonalities, discrepancies, and unique insights.
              - Integrating these insights into a coherent narrative that addresses the query's requirements, highlighting how each piece of information contributes to understanding the broader topic.
              - Utilizing advanced NLP techniques to ensure that the synthesis is not only comprehensive but also presents the information in an easily digestible format for the end-user.
              """,
              agent=agent,
              
              
              async_execution=False,
              expected_output=f"""
              Produce a detailed synthesis report that addresses the query comprehensively. The report should:
              - Clearly articulate how each document contributes to the answer.
              - Provide a unified analysis that combines insights from all relevant documents.
              - Highlight key themes, conflicts, or consensus found in the literature regarding the query.
              - Include a summary section that distills the most critical findings into actionable insights or conclusions.
              - Be formatted to allow easy navigation between sections corresponding to each document's contribution to the narrative,
                ensuring that users can trace the origins of each piece of information.
              - DO NOT give your final answer in JSON or dictionary format.  It MUST be in the form of a well written formated human readable report. 
              - The report must include: Clearly labeled  bold sections. 
              - The sections should include: an Introduction section that restates the query. The names in Bold of all documents used in the report. The
              key concepts, findings or specific requested factors, variables or datapoints in bold followed by their explanations. A synthesis of the various documents' information and contribution and a final 
              conclusion summary section  that
              eloquently ties all the relevant data together into a conclusion section.  
              """,
              callback=self.append_event_callback,
              
            )
        except Exception as e:
          logging.error(f"Error creating document_synthesis task for job {self.job_id}: {e}")
          raise e

    # def sci_summarize_document(self, agent: Agent, docs_path):
    #    try:
    #         return Task(
    #             description=f"""
    #             Obtain a research document from the docsummary tool. 
    #             Conduct a **structured, expert-level analysis** of the document.

    #             **Documents for summarization are located at:** {docs_path}  
    #             Read, digest, and analyze the document carefully.  

    #             ### **Summary Structure**
    #             Produce a **detailed and structured** summary containing:
    #             - **Title**: Full title of the document.
    #             - **Authors and Year**: List the main authors and publication date.
    #             - **Research Problem**: Clearly state the key question the study addresses.
    #             - **Objectives**: Describe the specific goals of the study.
    #             - **Methodology**: Identify the study type, sample size, experimental setup, statistical methods, and any technical aspects.
    #             - **Findings**: Present key results, including any numerical data or statistical insights.
    #             - **Limitations**: Identify any study weaknesses, biases, or constraints.
    #             - **Gaps in Literature**: Highlight areas that need further research.
    #             - **Future Research Directions**: Suggest next steps based on the study's conclusions.
    #             - **Key Terminology & Concepts**: Extract and define relevant technical terms.

    #             ### **Formatting Rules**
    #             - Each section **must be clearly labeled** for easy identification.
    #             - **Bold section headers** to improve readability.
    #             - **Summaries should be standalone**, providing complete insight without needing the original document.
    #             - **Exclude non-technical content** such as acknowledgments or dedications.
    #             - If the document contains an **abstract or methodology section, explicitly label them**.
    #             - Provide **an introductory statement** summarizing the paper's significance.
    #             - Include **a conclusion summarizing the main takeaways**.

    #             **Final Output Requirements:**
    #             - The structured summary should be **long enough** to capture all relevant details.
    #             - The agent should clearly state when the summary is complete.
    #             - DO NOT enclose the input in triple backticks (` ``` `).
    #             - DO NOT add unnecessary JSON or Python labels.

    #             """,
    #             agent=agent,
    #             async_execution=False,
    #             expected_output="""
    #             Provide a list of dictionaries. Each dictionary must contain:
    #             - 'title': The title of the document.
    #             - 'summary': A structured, **comprehensive summary** capturing all key points.
    #             - 'path': The file path to the document.
    #             - 'keywords': A list of key terms and technical concepts extracted from the paper.

    #             **Output Format:**
    #             The result should be **structured as a Python dictionary** to ensure smooth downstream processing.
    #             DO NOT return the output as a JSON object.
    #             """,
    #             callback=self.append_event_callback,
    #         )
    #    except Exception as e:
    #       logging.error(f"Error creating sci_summarize_document task for job {self.job_id}: {e}")
    #       raise e  


    def sci_summarize_document(self, agent: Agent, docs_path):
      try:
          return Task(
              description=f"""
              STAGE 1: INITIAL SUMMARIZATION
              - Obtain a research document from the document folder.
              - Conduct a **thorough** and **expert-level** analysis.
              - Generate a **comprehensive** research summary.
              - Ensure that all **key insights, concepts, and findings** are captured.

              Documents for summarization are located at: {docs_path}
              Read, digest, and analyze the document carefully.

              STAGE 2: STRUCTURED EXTRACTION
              - Extract **specific structured fields** from the summary.
              - Format the output into a structured research dictionary.

              STRUCTURED SUMMARY FORMAT:
              - **Title**: Full title of the document.
              - **Authors and Year**: Extract author names and publication year.
              - **Abstract**: Extract the abstract section if available.
              - **Research Problem**: Define the main research question being addressed.
              - **Objectives**: Describe the study's goals.
              - **Methodology**: Identify study type, sample size, experimental setup, statistical methods, and technical aspects.
              - **Findings**: Present key results, including any numerical data or statistical insights.
              - **Limitations**: Identify study weaknesses, biases, or constraints.
              - **Gaps in Literature**: Highlight areas that need further research.
              - **Future Research Directions**: Suggest next steps based on study conclusions.
              - **Key Terminology & Concepts**: Extract relevant technical terms and definitions.

              FORMATTING RULES:
              - Each section **must be clearly labeled** for structured processing.
              - Use **bold section headers** for readability.
              - Summaries should be **standalone** and provide all necessary insights without requiring the original paper.
              - If the document contains an **abstract or methodology section, explicitly label and extract them**.
              - Include a **brief introduction** summarizing the paper’s significance.
              - Provide a **conclusion** summarizing key takeaways.

              EXPECTED OUTPUT:
              - The structured summary should be **formatted as a Python dictionary** for seamless integration into research tools.
              - The final summary must be **detailed enough** to capture all critical aspects of the paper.
              - Ensure the output is **properly formatted and structured** for downstream processing.

              OUTPUT FORMAT (Python Dictionary):
              {{
                  "title": "Extracted Title",
                  "authors": "Extracted Authors",
                  "abstract": "Extracted Abstract",
                  "research_problem": "Extracted Research Problem",
                  "objectives": "Extracted Objectives",
                  "methodology": "Extracted Methodology",
                  "findings": "Extracted Findings",
                  "limitations": "Extracted Limitations",
                  "gaps": "Extracted Gaps in Literature",
                  "future_work": "Extracted Future Research Directions",
                  "keywords": ["Extracted", "Key", "Terms"],
                  "summary": "Full detailed textual summary",
                  "path": "File path to the original document"
              }}

              IMPORTANT:
              - The output **MUST** contain both the **full textual summary** and the **structured dictionary**.
              - DO NOT enclose the input in triple backticks (` ``` `).
              - DO NOT return JSON or Python labels explicitly.
              - Ensure the output is properly formatted for further research processing.
              """,
              agent=agent,
              async_execution=False,
              expected_output="""
              The final output should be a **structured Python dictionary** containing:
              - 'title': Extracted document title.
              - 'summary': A **comprehensive** full-text summary.
              - 'authors': Extracted author names.
              - 'abstract': Extracted abstract.
              - 'research_problem': Extracted research problem.
              - 'objectives': Extracted research objectives.
              - 'methodology': Extracted methodology details.
              - 'findings': Extracted findings.
              - 'limitations': Extracted study limitations.
              - 'gaps': Extracted knowledge gaps.
              - 'future_work': Suggested future research directions.
              - 'keywords': List of extracted key terms.
              - 'path': Path to the original document.

              The result must be returned as a **Python dictionary**, NOT as a JSON string.
              """,
              callback=self.append_event_callback,
          )
      except Exception as e:
        logging.error(f"Error creating sci_summarize_document task for job {self.job_id}: {e}")
        raise e
    def generate_report(self, agent: Agent, summaries_path_json, save_directory):
        try:
            return Task(
                description=f"""
                Generate a **professional, expert-level research report** summarizing multiple scientific papers.
                
                **Input Data:**  
                - The agent receives a **list of structured research summaries**, Obatin summaries from here: {summaries_path_json} each containing:
                  - **Title**
                  - **Authors and Year**
                  - **Research Problem**
                  - **Objectives**
                  - **Methodology** (study type, sample size, experimental setup, statistical methods)
                  - **Findings** (core results, including key statistics)
                  - **Limitations** (study weaknesses, biases, constraints)
                  - **Gaps in Literature** (unanswered research questions)
                  - **Future Research Directions**
                  - **Key Terminology & Concepts**
                
                **Task Execution:**  
                - The agent **processes and refines** the structured summaries.
                - It **formats the summaries into a clear, well-organized, and readable document**.
                - The report must be structured in a way that makes it:
                  - **Easy to navigate** for researchers.
                  - **Comprehensive** but still readable.
                  - **Scientifically rigorous** with all key information preserved.
                
                **Formatting Rules:**  
                - The report **must include bold headers** for each section.
                - The **sections must be labeled** properly:
                  - **Title**  
                  - **Authors & Year**  
                  - **Research Problem**  
                  - **Objectives**  
                  - **Methodology**  
                  - **Findings**  
                  - **Limitations**  
                  - **Gaps in Literature**  
                  - **Future Research Directions**  
                  - **Key Terms**  
                - **Summaries should be complete and independent** of the original paper.
                - The report must contain **a final conclusion section summarizing all key findings**.

                **Final Output:**  
                - The report will be generated using the **sci_summaryTool**.
                - It will be saved as a **Markdown (.md) or plain text (.txt) file**.
                - The output file must be formatted and ready for **direct human reading** or further processing.
                - Save a copy in the follwing location: {save_directory}
                """,
                agent=agent,
                async_execution=False,
                expected_output="""
                The agent must generate a **scientific summary report** and save it as a **well-formatted document**.

                **Output Format:**  
                - A **human-readable, structured scientific report** in Markdown (`.md`) or text (`.txt`) format.
                - The report must contain **clear headers and well-organized content**.
                - Each section (title, authors, methodology, findings, etc.) must be properly labeled.
                - The report should be **fully standalone**, meaning a researcher can read it and understand the study without needing the original paper.

                **File Output:**  
                - The summary report will be **saved to a designated location**.
                - The agent should return the file path of the generated report.
                """,
               
                callback=self.append_event_callback
            )
        except Exception as e:
           logging.error(f"Error creating generate_report task for job {self.job_id}: {e}")
           raise e   
                   