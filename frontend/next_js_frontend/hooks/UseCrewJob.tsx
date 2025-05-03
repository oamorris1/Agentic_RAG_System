import { useEffect, useState } from "react";
import axios from "axios";
import toast from "react-hot-toast";

export type EventType = {
    data: string;
    timestamp: string;
};

export type FinalResult = {
    user_query: string;
    result: string;
};

export const useCrewJob = () => {
    // State
    const [running, setRunning] = useState(false);
    const [user_query, setQuery] = useState<string>("");
    const [crew_type, setCrewType] = useState<string>("analysis");  // NEW State for crew selection
    const [finalResult, setFinalResult] = useState<FinalResult | null>(null);
    const [events, setEvents] = useState<EventType[]>([]);
    const [currentJobId, setCurrentJobId] = useState<string>("");

    // Poll job status
    useEffect(() => {
        let intervalID: number;

        const fetchJobStatus = async () => {
            try {
                const response = await axios.get<{
                    status: string;
                    result: FinalResult;
                    events: EventType[];
                }>(`http://localhost:3001/api/crew/${currentJobId}`);

                const { events: fetchedEvents, result, status } = response.data;
                setEvents(fetchedEvents || []);

                if (result) {
                    setFinalResult(result);
                    console.log("Final result:", result);
                }

                if (status === "COMPLETE" || status === "ERROR") {
                    clearInterval(intervalID);
                    setRunning(false);
                    toast.success(`Job ${status.toLowerCase()}.`);
                }
            } catch (error) {
                clearInterval(intervalID);
                setRunning(false);
                setCurrentJobId("");
                toast.error("Failed to get job status.");
                console.error(error);
            }
        };

        if (currentJobId) {
            intervalID = setInterval(fetchJobStatus, 10000) as unknown as number;
        }

        return () => {
            if (intervalID) {
                clearInterval(intervalID);
            }
        };
    }, [currentJobId]);

    // Start the job and pass `crew_type`
    const startJob = async () => {
        setEvents([]);
        setFinalResult(null);
        setRunning(true);

        try {
            const response = await axios.post<{ job_id: string }>(
                "http://localhost:3001/api/crew",
                {
                    crew_type,  // ✅ Send selected crew type
                    user_query, // ✅ Send query (if applicable)
                }
            );

            toast.success("Job started");
            setCurrentJobId(response.data.job_id);
            console.log("Job ID:", response.data.job_id);
        } catch (error) {
            toast.error("Failed to start job");
            console.error(error);
            setCurrentJobId("");
        }
    };

    return {
        running,
        events,
        finalResult,
        currentJobId,
        user_query,
        setQuery,
        crew_type, // ✅ Expose crew_type state
        setCrewType, // ✅ Expose setCrewType function
        startJob,
    };
};
