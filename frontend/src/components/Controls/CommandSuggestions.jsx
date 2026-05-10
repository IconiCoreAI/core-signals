import React from 'react';

export default function CommandSuggestions() {
  const suggestions = [
    'Summarize',
    'Plan next step',
    'Explain this',
    'Generate options',
    'Create checklist'
  ];

  return (
    <div className="w-full flex flex-wrap gap-sm">
      {suggestions.map((item, index) => (
        <button
          key={index}
          className="px-md py-sm bg-white border border-neutral/40 rounded-full text-sm text-gray-800 shadow-sm hover:shadow-md transition-all duration-200"
        >
          {item}
        </button>
      ))}
    </div>
  );
}
