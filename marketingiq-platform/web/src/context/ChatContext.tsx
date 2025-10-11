import React, { createContext, useContext, useState, ReactNode } from 'react';

interface ChatContextType {
  isChatOpen: boolean;
  chatPanelWidth: number;
  setChatOpen: (open: boolean) => void;
  setChatPanelWidth: (width: number) => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatPanelWidth, setChatPanelWidth] = useState(450);

  return (
    <ChatContext.Provider
      value={{
        isChatOpen,
        chatPanelWidth,
        setChatOpen: setIsChatOpen,
        setChatPanelWidth,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};
