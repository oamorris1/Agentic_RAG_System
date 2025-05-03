import json
import os
import logging
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from datetime import datetime

class SummaryReportInput(BaseModel):
    """Input schema for SummaryReportTool."""
    summaries_path_json: str = Field(
        ..., description="Path to the JSON file containing structured research summaries."
    )
    file_format: str = Field(
        default="md",
        description="The format to save the report in. Options: 'txt', 'md'. Default is 'md'."
    )
    save_path: str = Field(
        default="summary_report.md",
        description="The file path to save the formatted summary report."
    )


class SummaryReportTool(BaseTool):
    """
    A tool for generating a formatted research summary report from structured JSON summaries.
    """
    name: str = "Summary_Report_Generator"
    description: str = "Generates a formatted research summary report from structured JSON summaries."
    args_schema: Type[BaseModel] = SummaryReportInput

    def _run(self, summaries_path_json: str,save_path: str, file_format: str = "md" ) -> str:
        """
        Reads structured research summaries from JSON, formats them, and saves them as a report.
        """
        # Check if JSON file exists
        print("Summary JSON from Tool: ", summaries_path_json)
        print("Save path from tool: ", save_path)
        if not os.path.exists(summaries_path_json):
            logging.error(f"Summaries JSON file not found: {summaries_path_json}")
            return f"Error: Summaries file not found at {summaries_path_json}."

        # Read the summaries from the JSON file
        try:
            with open(summaries_path_json, "r", encoding="utf-8") as file:
                summaries = json.load(file)
        except Exception as e:
            logging.error(f"Error reading summaries JSON file: {e}")
            return "Error reading summaries file."

        if not summaries:
            logging.warning("No summaries found in JSON file.")
            return "No summaries available to generate a report."

        logging.info(f"Generating summary report from {summaries_path_json} in {file_format} format...")

        # Format the report
        formatted_report = self._format_summaries(summaries)
        # Save the report
        # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # save_path = os.path.join(save_directory, f"summary_report_{timestamp}.{file_format}")
        # Save the report to a file
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(formatted_report)
            logging.info(f"Summary report saved to {save_path}")
            return {
                "report_text": formatted_report,
                "file_path":save_path
            }
        except Exception as e:
            logging.error(f"Error saving summary report: {e}")
            return "Error saving the summary report."

    def _format_summaries(self, summaries: list) -> str:
        """
        Converts a list of structured summaries into a human-readable formatted report.
        """
        report = "# Research Summary Report\n\n"

        for summary in summaries:
            if not summary.get("title"):
                logging.warning(f"Skipping summary without a title: {summary}")
                continue

            report += f"## {summary.get('title', 'Untitled Document')}\n\n"
            report += f"**Authors:** {summary.get('authors', 'Unknown')}\n\n"
            report += f"### Abstract\n{summary.get('abstract', 'Not provided')}\n\n"
            report += f"### Research Problem\n{summary.get('research_problem', 'Not provided')}\n\n"
            report += f"### Objectives\n{summary.get('objectives', 'Not provided')}\n\n"
            report += f"### Methodology\n{summary.get('methodology', 'Not provided')}\n\n"
            report += f"### Findings\n{summary.get('findings', 'Not provided')}\n\n"
            report += f"### Limitations\n{summary.get('limitations', 'Not provided')}\n\n"
            report += f"### Gaps in Literature\n{summary.get('gaps', 'Not provided')}\n\n"
            report += f"### Future Research Directions\n{summary.get('future_work', 'Not provided')}\n\n"
            report += f"### Key Terms\n{', '.join(summary.get('keywords', []))}\n\n"

            # 
            if "summary" in summary:
                report += f"### Full Summary\n{summary.get('summary')}\n\n"

            report += "---\n\n"

        return report


# Instantiate the tool
summary_report_tool = SummaryReportTool()

