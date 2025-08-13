import React, { createContext, useEffect, useState } from 'react';
import io, { Socket } from 'socket.io-client';
import { AnalysisProgress, AnalysisComplete } from '@app/types';

interface WebSocketContextType {
  socket: Socket | null;
  progress: Map<string, number>;
}

export const WebSocketContext = createContext<WebSocketContextType | null>(null);

export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [progress, setProgress] = useState(new Map<string, number>());

  useEffect(() => {
    const newSocket = io({ path: '/api/socket.io' }); // Use relative path for proxying
    setSocket(newSocket);

    newSocket.on('analysisProgress', (data: AnalysisProgress) => {
      setProgress((prevProgress) =>
        new Map(prevProgress).set(data.caseId, data.progress),
      );
    });

    newSocket.on('analysisComplete', (data: AnalysisComplete) => {
      setProgress((prevProgress) => {
        const newProgress = new Map(prevProgress);
        newProgress.delete(data.caseId);
        return newProgress;
      });
    });

    return () => {
      newSocket.off('analysisProgress');
      newSocket.off('analysisComplete');
      newSocket.close();
    };
  }, []);

  const value = { socket, progress };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};