import React from 'react';

const MissionList = () => {
  const missions = [
    { id: 1, title: 'Plan a trip', subtitle: 'Create an itinerary for a weekend getaway including destinations, activities, and budget.' },
    { id: 2, title: 'Research vendors', subtitle: 'Evaluate potential suppliers for office supplies and compare pricing and quality.' },
    { id: 3, title: 'Organize tasks', subtitle: 'Prioritize and schedule upcoming work items to improve productivity.' },
  ];

  return (
    <div className="text-lg font-medium text-gray-800 flex flex-col gap-lg w-full">
      {missions.map((mission) => (
        <div key={mission.id} className="bg-white p-lg rounded-xl shadow-sm border border-primary/20 cursor-pointer transition-all duration-200 hover:shadow-md hover:border-primary">
          <h3 className="text-lg font-semibold text-gray-900">{mission.title}</h3>
          <p className="text-sm text-gray-600 leading-relaxed">{mission.subtitle}</p>
        </div>
      ))}
    </div>
  );
};

export default MissionList;