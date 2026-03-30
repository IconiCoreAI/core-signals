import { useEffect, useState, useRef } from 'react'
import Dashboard from './components/Dashboard'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';

function App() {
  const [notifications, setNotifications] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const ws = useRef(null);

  // Initial fetch
  useEffect(() => {
    fetch(`${API_URL}/notifications`)
      .then(res => res.json())
      .then(data => {
        setNotifications(data || []);
      })
      .catch(err => console.error("Failed to fetch history", err));
  }, []);

  // WebSocket Connection
  useEffect(() => {
    let reconnectTimeout = null;

    const connect = () => {
      ws.current = new WebSocket(WS_URL);
      
      ws.current.onopen = () => setIsConnected(true);
      
      ws.current.onmessage = (event) => {
        try {
          const newNotif = JSON.parse(event.data);
          setNotifications(prev => [newNotif, ...prev]);
        } catch (e) {
          console.error("Failed to parse websocket message", e);
        }
      };
      
      ws.current.onclose = () => {
        setIsConnected(false);
        // Attempt to reconnect after 3 seconds
        reconnectTimeout = setTimeout(connect, 3000);
      };
      
      ws.current.onerror = (error) => {
        console.error("WebSocket error:", error);
      };
    };

    connect();

    return () => {
      clearTimeout(reconnectTimeout);
      if (ws.current) {
        // Prevent onclose handle from triggering reconnect when unmounting
        ws.current.onclose = null; 
        ws.current.close();
      }
    };
  }, []);

  // Handle Mark as Read
  const handleRead = async (id) => {
    try {
      const res = await fetch(`${API_URL}/notifications/${id}/read`, {
        method: 'PATCH'
      });
      if (res.ok) {
        setNotifications(prev => 
          prev.map(n => n.id === id ? { ...n, read: true } : n)
        );
      }
    } catch (err) {
      console.error("Failed to mark as read:", err);
    }
  };

  return (
    <Dashboard 
      notifications={notifications} 
      onRead={handleRead} 
      isConnected={isConnected} 
    />
  )
}

export default App
