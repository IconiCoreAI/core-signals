import React, { useState, useEffect } from 'react';
import AgentOutputStream from './AgentOutputStream';
import AgentStatusHeader from './AgentStatusHeader';

export default function Timeline({ onNewMessage, newCommand }) {
  const [messages, setMessages] = useState([]);
  const [status, setStatus] = useState("Idle");

  useEffect(() => {
    setMessages([
      { role: "system", text: "Agent initialized." }
    ]);

    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        { role: "system", text: "Ready for commands." }
      ]);
    }, 300);
  }, []);

  useEffect(() => {
    if (onNewMessage) {
      onNewMessage(messages);
    }
  }, [messages, onNewMessage]);

  useEffect(() => {
    if (newCommand) {
      if (newCommand && newCommand.startsWith("error:")) {
        setMessages((prev) => [
          ...prev,
          { role: "error", text: newCommand.replace("error:", "").trim() }
        ]);
        setStatus("Idle");
        return;
      }

      // Tool simulation
      if (newCommand && newCommand.startsWith("tool:")) {
        const toolText = newCommand.replace("tool:", "").trim();

        // Push tool message
        setMessages((prev) => [
          ...prev,
          { role: "tool", text: `Running tool: ${toolText}` }
        ]);

        setStatus("Thinking…");

        // After a short delay, continue with assistant reply
        setTimeout(() => {
          // System message after tool completes
          setMessages((prev) => [
            ...prev,
            { role: "system", text: "Tool output received. Processing…" }
          ]);

          // Replace with empty assistant message for streaming
          setMessages((prev) => [
            ...prev,
            { role: "assistant", text: "" }
          ]);

          const reply = `Tool completed: ${toolText}`;
          let i = 0;

          const interval = setInterval(() => {
            i++;
            setMessages((prev) => {
              const updated = [...prev];
              const last = updated[updated.length - 1];

              if (last.role === "assistant") {
                last.text = reply.slice(0, i);
              }

              return updated;
            });

            if (i >= reply.length) {
              clearInterval(interval);
              setStatus("Idle");
              setMessages((prev) => [
                ...prev,
                { role: "system", text: "Response complete." }
              ]);
            }
          }, 20);
        }, 400);

        return;
      }

      setStatus("Thinking…");

      // Add user message
      setMessages((prev) => [...prev, { role: "user", text: newCommand }]);

      // Temporary thinking bubble
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "…" }
      ]);

      // System reasoning marker
      setMessages((prev) => [
        ...prev,
        { role: "system", text: "Analyzing command…" }
      ]);

      // System planning marker
      setMessages((prev) => [
        ...prev,
        { role: "system", text: "Planning response…" }
      ]);

      // Create empty assistant message
      setMessages((prev) => {
        const updated = [...prev];
        // Remove the temporary thinking bubble and append the empty assistant message
        updated.splice(updated.length - 3, 1);
        updated.push({ role: "assistant", text: "" });
        return updated;
      });

      // Stream the reply text
      const reply = `Acknowledged: ${newCommand}`;
      let i = 0;

      const interval = setInterval(() => {
        i++;
        setMessages((prev) => {
          const updated = [...prev];
          const last = updated[updated.length - 1];

          if (last.role === "assistant") {
            last.text = reply.slice(0, i);
          }

          return updated;
        });

        if (i >= reply.length) {
          clearInterval(interval);
          setStatus("Idle");
          setMessages((prev) => [
            ...prev,
            { role: "system", text: "Response complete." }
          ]);
        }
      }, 20);
    }
  }, [newCommand]);

  return (
    <div className="text-lg font-medium text-gray-800 flex flex-col gap-lg w-full h-full">
      <div className="flex flex-col gap-md h-full">
        <AgentStatusHeader status={status} />
        <AgentOutputStream messages={messages} />
      </div>
    </div>
  );
}