import { useEffect, useState } from 'react';
import supabase from './supabaseClient';

export default function RLSTest() {
  const [status, setStatus] = useState('checking');
  const [lastPing, setLastPing] = useState(null);
  const [profiles, setProfiles] = useState([]);

  const pingSupabase = async () => {
    try {
      const { data, error } = await supabase
        .from('profiles')
        .select('*')
        .limit(1);

      if (error) {
        setStatus('error');
        return;
      }

      setStatus('ok');
      setLastPing(new Date().toLocaleTimeString());
      setProfiles(data || []);
    } catch (e) {
      setStatus('error');
    }
  };

  useEffect(() => {
    pingSupabase();
    const interval = setInterval(pingSupabase, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        padding: '12px 18px',
        background: status === 'ok' ? '#c8f7c5' : '#f7c5c5',
        borderRadius: '10px',
        marginBottom: '25px',
        fontSize: '20px',
        fontWeight: '600',
        width: 'fit-content',
        boxShadow: '0 2px 6px rgba(0,0,0,0.15)'
      }}>
        <span style={{ fontSize: '26px' }}>
          {status === 'ok' ? '🟢' : '🔴'}
        </span>
        {status === 'ok' ? 'ONLINE — App & Supabase Connected' : 'OFFLINE — Connection Error'}
      </div>

      <h2>Supabase Heartbeat Monitor</h2>

      <div
        style={{
          padding: '15px',
          borderRadius: '8px',
          background:
            status === 'ok'
              ? '#d4ffd4'
              : status === 'error'
              ? '#ffd4d4'
              : '#fff3cd',
          border: '1px solid #ccc',
          marginBottom: '20px',
          display: 'inline-block',
        }}
      >
        <strong>Status:</strong>{' '}
        {status === 'ok'
          ? 'Connected to Supabase'
          : status === 'error'
          ? 'Connection Error'
          : 'Checking...'}
        <br />
        <strong>Last Ping:</strong> {lastPing || '—'}
      </div>

      <h3>Profiles Table (RLS Test)</h3>
      {profiles.length === 0 ? (
        <p>No profiles visible (RLS is working)</p>
      ) : (
        <ul>
          {profiles.map((p) => (
            <li key={p.id}>{JSON.stringify(p)}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
