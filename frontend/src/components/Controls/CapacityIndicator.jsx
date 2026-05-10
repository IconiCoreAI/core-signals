import React, { useState } from 'react';

export default function CapacityIndicator() {
  const [level, setLevel] = useState('Green');

  const colors = {
    Green: 'bg-green-500',
    Yellow: 'bg-yellow-400',
    Red: 'bg-red-500'
  };

  return (
    <div className="flex items-center gap-md">
      {['Green', 'Yellow', 'Red'].map((state) => (
        <button
          key={state}
          onClick={() => setLevel(state)}
          className={`w-8 h-8 rounded-full border border-neutral/40 shadow-sm transition-all duration-200 ${
            level === state ? colors[state] : 'bg-white'
          }`}
        />
      ))}
    </div>
  );
}