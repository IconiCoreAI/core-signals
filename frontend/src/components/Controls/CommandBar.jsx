import React, { useState } from 'react';
import CommandSuggestions from './CommandSuggestions';

export default function CommandBar({ onRunCommand }) {
  const [command, setCommand] = useState('');

  const handleRun = async () => {
    await fetch("https://iconicore.app.n8n.cloud/webhook/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: command })
    });
    onRunCommand && onRunCommand(command);
    setCommand('');
  };

  return (
    <div className="flex flex-col gap-md w-full bg-white p-4 rounded-xl shadow-sm border border-secondary/20 mb-4">
      <div className="flex items-center gap-3 w-full">
        <input
          type="text"
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          placeholder="Enter a command..."
          className="flex-1 px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-800 font-medium"
        />
        <button
          onClick={handleRun}
          className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors shadow-sm"
        >
          Run
        </button>
      </div>
      <CommandSuggestions />
    </div>
  );
}