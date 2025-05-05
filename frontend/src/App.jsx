// App.jsx - Main application file
import React, { useState } from 'react';
import ChatInterface from './components/ChatInterface';
import Sidebar from './components/Sidebar';
import './App.css';

function App() {
  const [showSidebar, setShowSidebar] = useState(true);
  
  return (
    <div className="flex h-screen bg-[#212121] text-gray-100">
      {/* Sidebar */}
      <Sidebar showSidebar={showSidebar} setShowSidebar={setShowSidebar} />
      
      {/* Main Chat Area */}
      <div className={`flex-1 flex flex-col transition-all ${showSidebar ? 'ml-64' : 'ml-0'}`}>
        <ChatInterface />
      </div>
    </div>
  );
}

export default App;