import React from 'react';
import { formatDistanceToNow } from 'date-fns';
import { motion } from 'framer-motion';
import { MessageSquare, CreditCard, Box, Bot, CheckCircle, Zap } from 'lucide-react';

const sourceIcons = {
  stripe: <CreditCard className="w-5 h-5 text-emerald-400" />,
  typeform: <MessageSquare className="w-5 h-5 text-blue-400" />,
  notion: <Box className="w-5 h-5 text-gray-300" />,
  'ai-agent': <Bot className="w-5 h-5 text-fuchsia-400" />
};

export default function NotificationCard({ notification, onRead }) {
  const Icon = sourceIcons[notification.source] || <Zap className="w-5 h-5 text-amber-400" />;

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: -20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      transition={{ duration: 0.3, type: 'spring', bounce: 0.3 }}
      className={`glass-card p-5 rounded-2xl mb-4 transition-all duration-300 ${notification.read ? 'opacity-50' : ''}`}
    >
      <div className="flex items-start gap-4">
        <div className="p-3 bg-gray-800/50 rounded-xl shadow-inner border border-white/5">
          {Icon}
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex justify-between items-start mb-1">
            <h3 className="font-semibold text-gray-100 truncate text-lg">{notification.title}</h3>
            <span className="text-xs text-gray-400 font-medium tracking-wide whitespace-nowrap ml-3">
              {formatDistanceToNow(new Date(notification.created_at), { addSuffix: true })}
            </span>
          </div>
          
          <p className="text-gray-300 text-sm leading-relaxed mb-3">{notification.body}</p>
          
          {notification.metadata && Object.keys(notification.metadata).length > 0 && (
            <div className="flex flex-wrap gap-2 mb-3">
              {Object.entries(notification.metadata).map(([key, value]) => (
                <span key={key} className="inline-flex items-center px-2 py-1 rounded-md bg-gray-800/60 border border-gray-700/50 text-xs text-gray-400">
                  <span className="text-gray-500 mr-1">{key}:</span> {String(value)}
                </span>
              ))}
            </div>
          )}
          
          <div className="flex justify-between items-center mt-2">
            <span className="text-xs uppercase tracking-wider font-semibold text-brand-500/80">
              {notification.source}
            </span>
            
            {!notification.read ? (
              <button 
                onClick={() => onRead(notification.id)}
                className="flex items-center gap-1.5 text-xs font-medium text-gray-400 hover:text-white transition-colors px-3 py-1.5 rounded-lg hover:bg-gray-800/80 cursor-pointer"
              >
                <CheckCircle className="w-3.5 h-3.5" />
                Mark as read
              </button>
            ) : (
              <span className="text-xs text-gray-500 flex items-center gap-1.5">
                <CheckCircle className="w-3.5 h-3.5" />
                Read
              </span>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
