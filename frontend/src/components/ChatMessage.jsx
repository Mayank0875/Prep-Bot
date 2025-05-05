// components/ChatMessage.jsx
import React, { useState } from 'react';
import { UserIcon } from '@heroicons/react/24/solid';
import { ClipboardIcon, CheckIcon } from '@heroicons/react/24/outline';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import SyntaxHighlighter from 'react-syntax-highlighter';
import { atomOneDark } from 'react-syntax-highlighter/dist/esm/styles/hljs';
import 'katex/dist/katex.min.css';

function ChatMessage(props) {
  const message = props.message || {};
  const [copiedIndex, setCopiedIndex] = useState(null);
  
  // Clean message text function
  const cleanMessageText = (text) => {
    if (!text) return "";
    
    // Remove "Copy code" text
    let cleanedText = text.replace(/Copy code\s*/g, '');
    
    // Convert small code blocks to inline code
    // Pattern matches any code block that's just a single line or single word
    const smallCodeBlockRegex = /```(\w*)\s*([^\n`]{1,40})\s*```/g;
    cleanedText = cleanedText.replace(smallCodeBlockRegex, (match, language, code) => {
      return `\`${code.trim()}\``;
    });
    
    return cleanedText;
  };
  
  const copyToClipboard = (text, index) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  // Custom theme based on provided color schema
  const customTheme = {
    ...atomOneDark,
    hljs: {
      ...atomOneDark.hljs,
      background: '#212121', // --bg-primary
      color: '#fff', // --text-primary
    },
    'hljs-keyword': {
      ...atomOneDark['hljs-keyword'],
      color: '#66b5ff', // --text-accent
    },
    'hljs-string': {
      ...atomOneDark['hljs-string'],
      color: '#ff9e6c', // --text-status-warning
    },
    'hljs-comment': {
      ...atomOneDark['hljs-comment'],
      color: '#afafaf', // --text-tertiary equivalent
    },
    'hljs-function': {
      ...atomOneDark['hljs-function'],
      color: '#e8e8e8', // --icon-primary
    },
  };

  // Custom components for markdown rendering
  const components = {
    code({ node, inline, className, children, ...props }) {
      const match = /language-(\w+)/.exec(className || '');
      const language = match ? match[1] : '';
      const codeText = String(children).replace(/\n$/, '');
      
      // Enhanced inline code styling
      if (inline) {
        return (
          <code className="bg-[#303030] text-[#66b5ff] px-1 py-0.5 rounded text-sm font-mono font-medium" {...props}>
            {children}
          </code>
        );
      }
      
      // Only use code blocks for multi-line code or specific languages
      const hasMultipleLines = codeText.includes('\n');
      const isShortCode = codeText.length < 40 && !hasMultipleLines;
      
      // If it's short code and not explicitly asking for a language, treat as inline
      if (isShortCode && !language) {
        return (
          <code className="bg-[#303030] text-[#66b5ff] px-1 py-0.5 rounded text-sm font-mono font-medium">
            {codeText}
          </code>
        );
      }
      
      // Full code block with syntax highlighting for longer code segments
      return (
        <div className="rounded-md my-4 overflow-hidden border border-[#ffffff26]">
          <div className="flex justify-between items-center px-4 py-2 bg-[#303030] border-b border-[#ffffff26]">
            {language && <span className="text-xs text-[#cdcdcd]">{language}</span>}
            <button
              onClick={() => copyToClipboard(codeText, language)}
              className="flex items-center text-xs text-[#cdcdcd] hover:text-[#fff]"
            >
              {copiedIndex === language ? (
                <>
                  <CheckIcon className="h-4 w-4 mr-1" />
                  <span>Copied!</span>
                </>
              ) : (
                <>
                  <ClipboardIcon className="h-4 w-4 mr-1" />
                  <span>Copy code</span>
                </>
              )}
            </button>
          </div>
          <div className="overflow-x-auto">
            <SyntaxHighlighter 
              language={language} 
              style={customTheme}
              customStyle={{
                margin: 0,
                padding: '1rem',
                backgroundColor: '#212121', // --bg-primary
                borderRadius: 0,
              }}
            >
              {codeText}
            </SyntaxHighlighter>
          </div>
        </div>
      );
    },
    
    p({ children }) {
      return <p className="mb-4 whitespace-pre-wrap break-words text-[#f3f3f3]">{children}</p>;
    },
    
    ul({ children }) {
      return <ul className="list-disc ml-6 mb-4 text-[#f3f3f3]">{children}</ul>;
    },
    
    ol({ children }) {
      return <ol className="list-decimal ml-6 mb-4 text-[#f3f3f3]">{children}</ol>;
    },
    
    li({ children }) {
      return <li className="mb-1 text-[#f3f3f3]">{children}</li>;
    },
    
    blockquote({ children }) {
      return (
        <blockquote className="pl-4 border-l-4 border-[#ffffff26] text-[#cdcdcd] my-4">
          {children}
        </blockquote>
      );
    },

    h1({ children }) {
      return <h1 className="text-2xl font-bold mb-4 text-[#fff]">{children}</h1>;
    },

    h2({ children }) {
      return <h2 className="text-xl font-bold mb-3 text-[#fff]">{children}</h2>;
    },

    h3({ children }) {
      return <h3 className="text-lg font-bold mb-2 text-[#fff]">{children}</h3>;
    },

    table({ children }) {
      return (
        <div className="overflow-x-auto my-4">
          <table className="min-w-full border border-[#ffffff26] text-[#f3f3f3]">
            {children}
          </table>
        </div>
      );
    },

    thead({ children }) {
      return <thead className="bg-[#303030]">{children}</thead>;
    },

    th({ children }) {
      return <th className="py-2 px-4 border-b border-[#ffffff26] text-left font-medium">{children}</th>;
    },

    td({ children }) {
      return <td className="py-2 px-4 border-b border-[#ffffff26]">{children}</td>;
    },

    a({ children, href }) {
      return <a href={href} className="text-[#66b5ff] hover:underline">{children}</a>;
    },
  };

  // Process the message text to clean it
  const cleanedText = cleanMessageText(message.text);

  return (
    <div className={`py-6 ${message.sender === 'bot' ? 'bg-[#0d0d0d80] rounded-lg' : ''}`}>
      <div className="max-w-3xl mx-auto px-4 sm:px-6 flex gap-4">
        {/* Avatar */}
        <div className="flex-shrink-0 mt-0.5">
          {message.sender === 'bot' ? (
            <div className="w-8 h-8 rounded-full bg-gradient-to-r from-[#013566] to-[#004f99] flex items-center justify-center">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-5 h-5 text-[#fff]">
                <path d="M10 8V16L16 12L10 8Z" fill="currentColor" />
                <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>
          ) : (
            <div className="w-8 h-8 rounded-full bg-[#303030] flex items-center justify-center">
              <UserIcon className="w-5 h-5 text-[#e8e8e8]" />
            </div>
          )}
        </div>
        
        {/* Message content */}
        <div className="flex-1 overflow-hidden">
          <div className={`prose max-w-none ${message.error ? 'text-[#ff8583]' : 'text-[#fff]'}`}>
            {cleanedText ? (
              <ReactMarkdown 
                remarkPlugins={[remarkGfm, remarkMath]} 
                rehypePlugins={[rehypeKatex]} 
                components={components}
              >
                {cleanedText}
              </ReactMarkdown>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ChatMessage;