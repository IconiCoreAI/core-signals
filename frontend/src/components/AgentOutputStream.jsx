import React, { useEffect, useRef } from 'react';

export default function AgentOutputStream({ messages }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="w-full h-full overflow-y-auto flex flex-col gap-md p-lg bg-white rounded-xl shadow-sm border border-neutral/40">
      {messages.length === 0 && (
        <div className="text-sm text-gray-500 bg-neutral/10 p-md rounded-lg">
          Waiting for commands…
        </div>
      )}

      {messages.map((msg, index) => {
        const isUser = msg.role === "user";
        const bubbleClass = isUser
          ? 'self-end bg-primary text-white shadow-sm'
          : msg.role === 'system'
            ? 'self-center bg-neutral/5 text-gray-600 border border-neutral/20 text-xs px-md py-sm rounded-md'
            : msg.role === 'error'
              ? 'self-center bg-red-50 text-red-700 border border-red-300 shadow-sm px-md py-sm rounded-md'
            : msg.role === 'tool'
              ? 'self-center bg-blue-50 text-blue-700 border border-blue-300 shadow-sm px-md py-sm rounded-md text-xs'
              : 'self-start bg-white text-gray-900 border border-neutral/30 shadow-sm pl-lg border-l-4 border-l-primary/60';

        return (
          <div
            key={index}
            className={`max-w-[80%] p-md rounded-lg text-sm ${bubbleClass}`}
          >
            <div className="flex flex-col">
              <span>{msg.text}</span>
              <span className="text-[10px] text-gray-400 mt-1">
                {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
          </div>
        );
      })}
      <div ref={bottomRef} />
    </div>
  );
}
