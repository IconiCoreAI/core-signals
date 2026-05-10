import React from 'react';
import ModeToggle from './Controls/ModeToggle';
import CapacityIndicator from './Controls/CapacityIndicator';

export default function ContextPanel() {
  return (
    <div className="w-full h-full flex flex-col gap-xl p-lg bg-neutral/5 rounded-xl border border-neutral/40 shadow-sm">

      {/* Mode Section */}
      <div className="bg-white p-lg rounded-xl shadow-sm border border-neutral/40 flex flex-col gap-md">
        <h2 className="text-lg font-semibold text-gray-900">Mode</h2>
        <ModeToggle />
      </div>

      {/* Capacity Section */}
      <div className="bg-white p-lg rounded-xl shadow-sm border border-neutral/40 flex flex-col gap-md">
        <h2 className="text-lg font-semibold text-gray-900">Capacity</h2>
        <CapacityIndicator />
      </div>

      {/* Notes Section */}
      <div className="bg-white p-lg rounded-xl shadow-sm border border-neutral/40 flex flex-col gap-md flex-1">
        <h2 className="text-lg font-semibold text-gray-900">Notes</h2>
        <textarea
          placeholder="Write notes here..."
          className="w-full h-full p-md rounded-lg border border-neutral/40 focus:border-primary focus:ring-0 outline-none text-sm text-gray-800 resize-none"
        />
      </div>

    </div>
  );
}