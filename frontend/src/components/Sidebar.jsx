// components/Sidebar.jsx
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { PlusIcon, FolderIcon, XMarkIcon, Bars3Icon } from '@heroicons/react/24/outline';

const API_URL = 'https://prep-bot-backend.onrender.com';

function Sidebar({ showSidebar, setShowSidebar }) {
  const [documents, setDocuments] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  
  useEffect(() => {
    fetchDocuments();
  }, []);
  
  const fetchDocuments = async () => {
    try {
      const response = await axios.get(`${API_URL}/documents`);
      setDocuments(response.data.documents || []);
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  };
  
  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setIsUploading(true);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      await axios.post(`${API_URL}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      // Refresh document list
      fetchDocuments();
    } catch (error) {
      console.error('Error uploading document:', error);
      alert('Failed to upload document');
    } finally {
      setIsUploading(false);
    }
  };
  
  // If sidebar is hidden, show only the toggle button
  if (!showSidebar) {
    return (
      <button 
        onClick={() => setShowSidebar(true)}
        className="fixed top-3 left-3 p-2 rounded-md bg-gray-800 hover:bg-gray-700 z-10"
      >
        <Bars3Icon className="h-6 w-6" />
      </button>
    );
  }
  
  return (
    <div className="fixed h-screen w-64 bg-[#181818] p-4 flex flex-col shadow-lg">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold">Prep Bot</h2>
        <button 
          onClick={() => setShowSidebar(false)}
          className="p-1 rounded-md hover:bg-gray-700"
        >
          <XMarkIcon className="h-5 w-5" />
        </button>
      </div>
      
      {/* New Chat Button */}
      {/* <button className="flex items-center justify-center gap-2 py-3 px-4 rounded-md border border-gray-600 hover:bg-gray-700 transition mb-6">
        <PlusIcon className="h-5 w-5" />
        <span>New chat</span>
      </button> */}
      
      {/* Upload Document Button */}
      {/* <div className="mb-6">
        <label className="flex items-center justify-center gap-2 py-3 px-4 rounded-md bg-indigo-600 hover:bg-indigo-700 transition cursor-pointer">
          <input
            type="file"
            onChange={handleFileUpload}
            className="hidden"
            accept=".pdf,.txt,.docx"
            disabled={isUploading}
          />
          {isUploading ? 'Uploading...' : 'Upload Document'}
        </label>
      </div> */}
      
      {/* Documents List */}
      <div className="flex-1 overflow-y-auto">
        <h3 className="text-sm uppercase text-gray-400 mb-2 px-2">Documents</h3>
        <ul className="space-y-1">
          {documents.length > 0 ? (
            documents.map((doc, index) => (
              <li key={index} className="px-2 py-2 rounded-md hover:bg-gray-700 flex items-center gap-2">
                <FolderIcon className="h-4 w-4 text-gray-400" />
                <span className="text-sm truncate">{doc.name}</span>
              </li>
            ))
          ) : (
            <li className="px-2 py-2 text-sm text-gray-400">No documents yet</li>
          )}
        </ul>
      </div>
      
      {/* Footer */}
      <div className="pt-4 border-t border-gray-700 mt-4">
        <div className="text-sm text-gray-400">University Knowledge Base</div>
      </div>
    </div>
  );
}

export default Sidebar;
