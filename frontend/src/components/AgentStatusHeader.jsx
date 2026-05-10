import React from 'react';

export default function AgentStatusHeader({ status = "Idle" }) {
  const color =
    status === "Idle" ? "text-gray-500" :
    status === "Thinking…" ? "text-primary" :
    status.includes("Running") ? "text-blue-600" :
    status === "Error" ? "text-red-600" :
    "text-gray-700";

  return (
    <div className={`w-full text-sm font-medium ${color}`}>
      {status}
    </div>
  );
}
