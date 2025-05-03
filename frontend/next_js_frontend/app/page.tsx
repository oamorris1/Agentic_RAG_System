"use client";
import { useCrewJob } from "@/hooks/UseCrewJob";
import InputSection from "@/components/InputSection";
import EventLog from "@/components/EventLog";
import FinalOutput from "@/components/FinalOutput";

export default function Home() {
  // Hooks
  const crewJob = useCrewJob();

  return (
    <div className="bg-white min-h-screen text-black">
      <div className="flex">
        {/* LEFT COLUMN */}
        <div className="w-1/2 p-4">
          <InputSection 
            title="Query"
            placeholder="Please enter a query" 
            data={crewJob.user_query}
            setData={crewJob.setQuery}
            crewType={crewJob.crew_type}  // ✅ Pass crewType state
            setCrewType={crewJob.setCrewType}  // ✅ Pass setCrewType function
          />
        </div>

        {/* RIGHT COLUMN */}
        <div className="w-1/2 p-4 flex flex-col">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold">Output</h2>
            <button 
              onClick={() => crewJob.startJob()}
              disabled={crewJob.running}
              className="bg-green-600 hover:bg-green-800 text-white font-bold py-2 px-4 rounded"
            >
              {crewJob.running ? "Crew Running..." : "Start Crew"}
            </button>
          </div>
          <FinalOutput finalResult={crewJob.finalResult} />
          <EventLog events={crewJob.events} />
        </div>
      </div>
    </div>
  );
}
