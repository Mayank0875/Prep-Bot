
// components/ChatInterface.jsx
import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { PaperAirplaneIcon } from '@heroicons/react/24/solid';
import ChatMessage from './ChatMessage';

const API_URL = 'https://prep-bot-backend.onrender.com';

function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  
  // Auto-scroll to bottom of messages
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    
    // Add user message to chat
    const userMessage = { text: input, sender: 'user' };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setInput('');
    setIsLoading(true);
    
    try {
      // Send question to backend
      const formData = new FormData();
      formData.append('question', input);
      
      const response = await axios.post(`${API_URL}/ask`, formData);
      
      // Add bot response to chat
      const botMessage = {
        text: response.data.answer,
        sender: 'bot',
        sources: response.data.sources
      };
      
      setMessages((prevMessages) => [...prevMessages, botMessage]);
    } catch (error) {
      console.error('Error getting answer:', error);
      
      // Add error message
      const errorMessage = {
        text: 'Sorry, I encountered an error while processing your question.',
        sender: 'bot',
        error: true
      };
      
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <>
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col justify-center items-center text-center px-4">
            <h1 className="text-3xl font-bold mb-6">Ace Your End Sem</h1>
            <p className="text-gray-400 max-w-md mb-8">
            Upload your notes, ask questions, and ace your exams with AI-powered learning support
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full max-w-2xl">
              <div className="p-4 rounded-lg border border-[#ffffff26]">
                <h3 className="text-lg font-semibold mb-2">📚 Revise Topics</h3>
                <p className="text-sm text-gray-400">Get summaries and explanations of any concept from your course materials</p>
              </div>
              <div className="p-4 rounded-lg border border-[#ffffff26]">
                <h3 className="text-lg font-semibold mb-2">✍️ Solve Questions</h3>
                <p className="text-sm text-gray-400">Get step-by-step help with problems from your coursework</p>
              </div>
              
            </div>
          </div>
        ) : (
          <div className="max-w-3xl mx-auto">
            {messages.map((message, index) => (
              <ChatMessage key={index} message={message} />
            ))}
            {isLoading && (
              <div className="flex gap-2 items-center text-gray-400 py-4 px-6 rounded-lg bg-[#303030] mb-4 max-w-[85%]">
                <div className="flex space-x-1">
                  <div className="h-2 w-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="h-2 w-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  <div className="h-2 w-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '600ms' }}></div>
                </div>
                <span className="text-sm">Thinking...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>
      
      {/* Input Area */}
      <div className="border-t border-gray-700 p-4">
        <form onSubmit={handleSendMessage} className="max-w-3xl mx-auto">
          <div className="relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question about your documents..."
              className="w-full bg-[#ffffff26] text-white border border-gray-600 rounded-lg py-3 pl-4 pr-12 focus:outline-none focus:border-[#ffffff26]"
              disabled={isLoading}
            />
            <button
              type="submit"
              className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white disabled:opacity-50"
              disabled={!input.trim() || isLoading}
            >
              <PaperAirplaneIcon className="h-5 w-5" />
            </button>
          </div>
          <p className="text-xs text-gray-400 text-center mt-2">
            The AI assistant provides answers based on your uploaded documents.
          </p>
        </form>
      </div>
    </>
  );
}

export default ChatInterface;
