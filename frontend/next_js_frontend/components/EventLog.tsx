import React from "react";
import ReactMarkdown from "react-markdown";
import { EventType } from "@/hooks/UseCrewJob";

interface EventLogProps {
  events: EventType[];
}

const EventLog: React.FC<EventLogProps> = ({ events }) => {
  // Function to render the content of each event
  const renderEventContent = (data: any) => {
    // If the event data is a list of dictionaries
    if (Array.isArray(data)) {
      return data.map((item, index) => (
        <div key={index} className="border p-4 mb-4 rounded bg-white">
          {item.title && <h3 className="text-xl font-bold mb-2">{item.title}</h3>}
          {item.summary && (
            <ReactMarkdown className="text-gray-700">
              {item.summary.replace(/\*\*(.*?)\*\*/g, "**$1**")}
            </ReactMarkdown>
          )}
          {item.path && (
            <p className="text-blue-600 mt-2">
              <strong>Document Path:</strong> {item.path}
            </p>
          )}
        </div>
      ));
    }

    // If the event data is a plain string
    if (typeof data === "string") {
      return <ReactMarkdown>{data.replace(/\*\*(.*?)\*\*/g, "**$1**")}</ReactMarkdown>;
    }

    return <p>Invalid event data format.</p>;
  };

  return (
    <div className="flex flex-col h-full">
      <h2 className="text-lg font-semibold my-4">Event Details</h2>
      <div className="flex-grow overflow-auto border-2 border-gray-300 p-4 rounded-md bg-gray-50">
        {events.length === 0 ? (
          <p>No events yet.</p>
        ) : (
          events.map((event, index) => (
            <div key={index} className="mb-6">
              <p className="text-gray-500 text-sm">
                {new Date(event.timestamp).toLocaleString()}
              </p>
              <div className="mt-2">{renderEventContent(event.data)}</div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default EventLog;

