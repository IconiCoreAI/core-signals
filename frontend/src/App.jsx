import React, { useState } from 'react';
import MissionList from './components/MissionList';
import Timeline from './components/Timeline';
import ContextPanel from './components/ContextPanel';
import CommandBar from './components/Controls/CommandBar';

function App() {
  const [lastCommand, setLastCommand] = useState(null);

  return (
    <div className="flex h-screen">
      <div className="w-[250px] bg-primary-light p-xl border-r border-primary/20 rounded-none shadow-sm">
        <MissionList />
      </div>
      <div className="flex-1 bg-neutral p-2xl rounded-none shadow-inner flex flex-col">
        <CommandBar onRunCommand={(cmd) => setLastCommand(cmd)} />
        <Timeline onNewMessage={() => {}} newCommand={lastCommand} />
      </div>
      <div className="w-[300px] bg-secondary-light p-xl border-l border-secondary/20 rounded-none shadow-sm">
        <ContextPanel />
      </div>
    </div>
  );
}

export default App;
