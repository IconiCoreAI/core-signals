import React from 'react';
import { AnimatePresence } from 'framer-motion';
import { Activity, BellRing, Wifi, WifiOff } from 'lucide-react';
import NotificationCard from './NotificationCard';

export default function Dashboard({ notifications, onRead, isConnected }) {
  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <div className="min-h-screen bg-[#08060d] text-gray-100 flex justify-center p-4 sm:p-8 font-sans bg-[radial-gradient(ellipse_at_top_right,_rgba(170,59,255,0.15)_0%,_transparent_50%)] opacity-95">
      <div className="w-full max-w-3xl glass-panel rounded-3xl overflow-hidden shadow-2xl flex flex-col h-[90vh]">
        
        {/* Header */}
        <header className="px-8 py-6 border-b border-white/5 flex justify-between items-center bg-black/20 backdrop-blur-md z-10 sticky top-0">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="p-2 bg-brand-500/20 rounded-xl rounded-tl-sm text-brand-500">
                <Activity className="w-6 h-6" />
              </div>
              {unreadCount > 0 && (
                <span className="absolute -top-1 -right-1 flex h-3 w-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-500 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-brand-500"></span>
                </span>
              )}
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-white">Core Signals</h1>
              <p className="text-xs text-gray-400 font-medium">Real-time Notification Hub</p>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold ${isConnected ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'}`}>
              {isConnected ? (
                <><Wifi className="w-3.5 h-3.5" /> Live</>
              ) : (
                <><WifiOff className="w-3.5 h-3.5" /> Offline</>
              )}
            </div>
            
            <div className="flex items-center gap-2 text-sm text-gray-400 bg-gray-800/50 px-3 py-1.5 rounded-full border border-white/5">
              <BellRing className="w-4 h-4" />
              <span>{unreadCount} unread</span>
            </div>
          </div>
        </header>

        {/* Feed */}
        <div className="flex-1 overflow-y-auto p-6 sm:p-8 relative">
          {notifications.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-gray-500">
              <BellRing className="w-12 h-12 mb-4 opacity-20" />
              <p>No signals yet. Waiting for activity...</p>
            </div>
          ) : (
            <AnimatePresence>
              {notifications.map(notif => (
                <NotificationCard 
                  key={notif.id} 
                  notification={notif} 
                  onRead={onRead} 
                />
              ))}
            </AnimatePresence>
          )}
        </div>
      </div>
    </div>
  );
}
