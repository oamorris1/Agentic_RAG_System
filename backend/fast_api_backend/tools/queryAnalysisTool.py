import json
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain.chains.summarize import load_summarize_chain
from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings
from typing import Type, List, Dict
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv('.env'), override=True)









# Initialize Azure OpenAI models
embeddings_model = AzureOpenAIEmbeddings(deployment="text-embedding-ada-002", model="text-embedding-ada-002")

class QueryAnalysisInput(BaseModel):
    """Input schema for QueryDocumentAnalysisTool."""
    query: str = Field(..., description="User's query for document analysis")
    summaries_path_json: str = Field(..., description="Path to the JSON file containing document summaries")

class QueryDocumentAnalysisTool(BaseTool):
    name: str = "Query_and_Document_Summary_Analysis"
    description: str = "Analyzes user queries against document summaries to determine relevant documents."
    args_schema: Type[BaseModel] = QueryAnalysisInput

    def _run(self, query: str, summaries_path_json: str) -> Dict:
        """Analyzes the given query against document summaries."""
        try:
            with open(summaries_path_json, 'r') as file:
                document_summaries = json.load(file)
        except Exception as e:
            return {"error": str(e)}

        query_embedding = embeddings_model.embed_query(query)

        # Embed each document summary
        document_embeddings = []
        for summary in document_summaries:
            document_embedding = embeddings_model.embed_query(summary['summary'])
            document_embeddings.append({
                "title": summary['title'],
                "path": summary['path'],
                "embedding": document_embedding
            })

        # Calculate cosine similarity
        cosine_similarities = [
            self._cosine_similarity(query_embedding, doc['embedding']) for doc in document_embeddings
        ]

        threshold = self._calculate_threshold(query)
        relevant_documents = []
        document_scores = []

        for idx, score in enumerate(cosine_similarities):
            document = {
                "title": document_embeddings[idx]['title'],
                "path": document_embeddings[idx]['path'],
                "score": score
            }
            document_scores.append(document)
            if score > threshold:
                relevant_documents.append(document)

        return {"documents": relevant_documents, "scores": document_scores}

    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    @staticmethod
    def _calculate_threshold(query: str) -> float:
        base_threshold = 0.76
        if len(query.split()) > 20:
            return base_threshold + 0.03
        return base_threshold

# Initialize the tool
query_document_analysis_tool = QueryDocumentAnalysisTool()