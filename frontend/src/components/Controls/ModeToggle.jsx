import React, { useState } from 'react';

export default function ModeToggle() {
  const [mode, setMode] = useState('Executive');

  return (
    <div className="flex items-center gap-md">
      <button
        onClick={() => setMode('Executive')}
        className={`px-lg py-sm rounded-lg text-sm font-medium border transition-all duration-200 ${
          mode === 'Executive'
            ? 'bg-primary text-white border-primary shadow-sm'
            : 'bg-white text-gray-800 border-neutral/40'
        }`}
      >
        Executive
      </button>

      <button
        onClick={() => setMode('Creative')}
        className={`px-lg py-sm rounded-lg text-sm font-medium border transition-all duration-200 ${
          mode === 'Creative'
            ? 'bg-primary text-white border-primary shadow-sm'
            : 'bg-white text-gray-800 border-neutral/40'
        }`}
      >
        Creative
      </button>
    </div>
  );
}