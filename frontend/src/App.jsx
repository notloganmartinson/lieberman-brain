import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [events, setEvents] = useState([]);
  const [isCalendarOpen, setIsCalendarOpen] = useState(false);
  
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleInputChange = (e) => {
    setInput(e.target.value);
    // Auto-resize logic
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    
    // Reset textarea height after submit
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
    
    setIsLoading(true);

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt: userMessage.content }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      
      if (data.new_event) {
        setEvents((prev) => [...prev, data.new_event]);
      }
      
      const aiMessage = {
        role: 'ai',
        content: data.reply,
        sources: data.sources || [],
      };
      
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error fetching chat response:', error);
      const errorMessage = {
        role: 'ai',
        content: 'Sorry, I encountered an error while processing your request.',
        sources: [],
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-screen w-full bg-white flex flex-col">
      <div className="w-full flex-1 flex flex-col overflow-hidden">
        
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-center z-10 sticky top-0">
          <div className="flex items-center justify-between w-full max-w-4xl relative">
            <div className="flex items-center gap-3">
              <h1 className="text-xl font-semibold text-gray-800 tracking-tight">Better Perplexity</h1>
              <div className="text-xs font-medium bg-purple-100 text-purple-700 px-3 py-1 rounded-full hidden sm:block">
                Persona-Grounded
              </div>
            </div>
            
            {/* Calendar UI */}
            <div className="relative">
              <button 
                onClick={() => setIsCalendarOpen(!isCalendarOpen)}
                className="relative p-2 text-gray-600 hover:bg-gray-100 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                aria-label="View Calendar"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                </svg>
                {events.length > 0 && (
                  <span className="absolute top-1 right-1 w-2.5 h-2.5 bg-red-500 border-2 border-white rounded-full"></span>
                )}
              </button>

              {/* Dropdown Menu */}
              {isCalendarOpen && (
                <div className="absolute right-0 mt-2 w-72 bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden z-50 transform origin-top-right transition-all">
                  <div className="px-4 py-3 bg-gray-50 border-b border-gray-100 flex justify-between items-center">
                    <h3 className="text-sm font-semibold text-gray-800">Scheduled Events</h3>
                    <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-medium">{events.length}</span>
                  </div>
                  <div className="max-h-64 overflow-y-auto p-2">
                    {events.length === 0 ? (
                      <p className="text-sm text-gray-500 text-center py-6">No upcoming events</p>
                    ) : (
                      <ul className="space-y-1">
                        {events.map((evt, idx) => (
                          <li key={idx} className="px-3 py-2 hover:bg-gray-50 rounded-lg transition-colors border border-transparent hover:border-gray-100">
                            <p className="text-sm font-medium text-gray-800 truncate" title={evt.title}>{evt.title}</p>
                            <p className="text-xs text-gray-500 mt-1 font-medium">{evt.date} • {evt.time}</p>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 max-w-4xl mx-auto w-full">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-gray-400 space-y-4">
              <svg className="w-16 h-16 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path></svg>
              <p className="text-lg">Ask me anything. I'll search the web and my graph.</p>
            </div>
          ) : (
            messages.map((msg, index) => (
              <div key={index} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] rounded-2xl px-5 py-4 ${msg.role === 'user' ? 'bg-blue-600 text-white rounded-br-none' : 'bg-gray-100 text-gray-800 rounded-bl-none'}`}>
                  
                  {msg.role === 'user' ? (
                    <div className="whitespace-pre-wrap">{msg.content}</div>
                  ) : (
                    <div className="prose prose-sm md:prose-base max-w-none text-gray-800 prose-p:leading-relaxed prose-pre:bg-gray-800 prose-pre:text-gray-100">
                      {msg.content.startsWith("📅 **[Calendar Agent]**") && (
                        <div className="text-purple-600 font-semibold mb-2 flex items-center gap-2">
                          <span className="text-lg">📅</span>
                          <span>[Calendar Agent]</span>
                        </div>
                      )}
                      <ReactMarkdown>
                        {msg.content.replace("📅 **[Calendar Agent]** ", "").replace("📅 **[Calendar Agent]**", "")}
                      </ReactMarkdown>
                    </div>
                  )}
                  
                  {/* Sources display for AI */}
                  {msg.role === 'ai' && msg.sources && msg.sources.length > 0 && (
                    <div className="mt-6 pt-4 border-t border-gray-200/60">
                      <p className="text-[11px] font-bold text-gray-400 uppercase tracking-widest mb-3 flex items-center gap-2">
                        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
                        Sources Analyzed
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {msg.sources.map((source, idx) => {
                          const isWeb = source.type === 'web';
                          let displayText = source.title || source.label || (isWeb ? 'Web Source' : 'Graph Source');
                          
                          if (isWeb && source.url) {
                            try {
                              const urlObj = new URL(source.url);
                              displayText = urlObj.hostname.replace(/^www\./, '');
                            } catch (e) {
                              // fallback to title
                            }
                          }

                          const badgeContent = (
                            <div className={`group inline-flex items-center gap-1.5 text-xs font-medium rounded-full px-3 py-1.5 transition-all duration-200 border ${
                              isWeb 
                                ? 'bg-blue-50/50 text-blue-700 border-blue-100 hover:bg-blue-100 hover:border-blue-200 cursor-pointer' 
                                : 'bg-purple-50/50 text-purple-700 border-purple-100 hover:bg-purple-100'
                            }`}>
                              <span className="text-[10px] opacity-70">{isWeb ? '🌐' : '🧠'}</span>
                              <span className="truncate max-w-[180px]" title={source.title || source.label}>
                                {displayText}
                              </span>
                            </div>
                          );

                          return isWeb && source.url ? (
                            <a key={idx} href={source.url} target="_blank" rel="noopener noreferrer" className="no-underline">
                              {badgeContent}
                            </a>
                          ) : (
                            <span key={idx}>{badgeContent}</span>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 text-gray-500 rounded-2xl rounded-bl-none px-5 py-4 flex items-center space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse-fast"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse-fast" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse-fast" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="bg-white border-t border-gray-200 p-4">
          <div className="max-w-4xl mx-auto w-full">
            <form onSubmit={handleSubmit} className="flex relative items-end rounded-xl border border-gray-300 bg-gray-50 overflow-hidden focus-within:border-blue-500 focus-within:ring-1 focus-within:ring-blue-500 transition-all">
              <textarea 
                ref={textareaRef}
                className="w-full bg-transparent max-h-32 min-h-[56px] py-3 pl-4 pr-12 outline-none resize-none text-gray-800 placeholder-gray-400 overflow-y-auto"
                placeholder="Ask a question..."
                value={input}
                onChange={handleInputChange}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit(e);
                  }
                }}
                rows={1}
                style={{ height: 'auto' }}
              />
              <button 
                type="submit" 
                disabled={!input.trim() || isLoading}
                className="absolute right-2 bottom-2 p-2 rounded-lg bg-blue-600 text-white disabled:bg-gray-300 disabled:text-gray-500 transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
              </button>
            </form>
            <div className="text-center mt-2">
               <span className="text-[10px] text-gray-400">Powered by FastAPI, Neo4j, and Gemini</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;