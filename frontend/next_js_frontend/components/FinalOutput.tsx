import React from "react";
import { FinalResult } from "@/hooks/UseCrewJob";
import ReactMarkdown from "react-markdown";

interface FinalOutputProps {
  finalResult: FinalResult | null;
}

const FinalOutput: React.FC<FinalOutputProps> = ({ finalResult }) => {
  // Extract the user_query and result from the finalResult object
  const userQuery = finalResult?.user_query || "";
  const resultText = finalResult?.result || "No job result yet.";

  return (
    <div className="flex flex-col h-full">
      <h2 className="text-lg font-semibold my-2">Final Output</h2>
      <div className="flex-grow overflow-auto border-2 border-gray-300 p-4 rounded-md bg-gray-50">
        {/* Display the user query */}
        <h3 className="text-xl font-bold mb-4">User Query:</h3>
        <p className="mb-4 text-blue-600">{userQuery}</p>

        {/* Display the formatted result using Markdown */}
        <h3 className="text-xl font-bold mb-4">Result:</h3>
        <ReactMarkdown>{resultText}</ReactMarkdown>
      </div>
    </div>
  );
};

export default FinalOutput;




