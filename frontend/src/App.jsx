import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { useGoogleLogin } from '@react-oauth/google';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [events, setEvents] = useState([]);
  const [isCalendarOpen, setIsCalendarOpen] = useState(false);
  const [accessToken, setAccessToken] = useState(null);
  
  // Sprint 4: Session and Upload State
  const [sessionId] = useState(() => crypto.randomUUID());
  const [isUploading, setIsUploading] = useState(false);
  const [attachedFile, setAttachedFile] = useState(null);
  
  // Feature: Cancellation
  const [abortController, setAbortController] = useState(null);
  
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);
  const calendarRef = useRef(null);
  const fileInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleCancel = () => {
    if (abortController) {
      abortController.abort();
    }
    setMessages((prev) => {
      const newMessages = [...prev];
      const lastMsg = newMessages[newMessages.length - 1];
      if (lastMsg && lastMsg.role === 'user') {
        lastMsg.isCancelled = true;
      }
      return newMessages;
    });
    setIsLoading(false);
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (calendarRef.current && !calendarRef.current.contains(event.target)) {
        setIsCalendarOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const login = useGoogleLogin({
    onSuccess: (tokenResponse) => setAccessToken(tokenResponse.access_token),
    scope: 'https://www.googleapis.com/auth/calendar.readonly https://www.googleapis.com/auth/calendar.events',
  });

  const handleInputChange = (e) => {
    setInput(e.target.value);
    // Auto-resize logic
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    
    setIsUploading(true);
    setAttachedFile(file.name);
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_id', sessionId);
    
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    try {
      const response = await fetch(`${apiUrl}/upload`, {
        method: 'POST',
        body: formData, // the browser will automatically set the correct Content-Type with boundary
      });
      
      if (!response.ok) {
        throw new Error('Upload failed');
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      setAttachedFile(null);
    } finally {
      setIsUploading(false);
      if (event.target) {
        event.target.value = null; // reset input so the same file can be uploaded again if needed
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isUploading) return;

    const userMessage = { role: 'user', content: input, attachment: attachedFile, isCancelled: false };
    
    // Capture conversation history before state update
    const history = messages.map(m => ({
      role: m.role === 'user' ? 'user' : 'model',
      content: m.content
    }));

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setAttachedFile(null); // Clear from input bar
    
    // Reset textarea height after submit
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
    
    const controller = new AbortController();
    setAbortController(controller);
    setIsLoading(true);

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          prompt: userMessage.content, 
          session_id: sessionId, 
          access_token: accessToken,
          history: history 
        }),
        signal: controller.signal,
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
      if (error.name === 'AbortError') {
        console.log('Request cancelled by user');
        return;
      }
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
            <div className="flex items-center gap-4 relative" ref={calendarRef}>
              {!accessToken ? (
                <button
                  onClick={() => login()}
                  className="text-sm font-medium bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors whitespace-nowrap"
                >
                  Sign in with Google
                </button>
              ) : (
                <div className="text-sm font-medium bg-green-100 text-green-700 px-3 py-1 rounded-full whitespace-nowrap border border-green-200">Calendar Connected</div>
              )}
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
                <div className="absolute top-full right-0 mt-2 w-72 max-w-[calc(100vw-2rem)] bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden z-50 transform origin-top-right transition-all">
                  <div className="px-4 py-3 bg-gray-50 border-b border-gray-100 flex justify-between items-center">
                    <h3 className="text-sm font-semibold text-gray-800 whitespace-nowrap">Scheduled Events</h3>
                    <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-medium ml-2">{events.length}</span>
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
                <div className={`max-w-[85%] rounded-2xl px-5 py-4 ${msg.role === 'user' ? (msg.isCancelled ? 'bg-gray-400 text-white rounded-br-none opacity-80' : 'bg-blue-600 text-white rounded-br-none') : 'bg-gray-100 text-gray-800 rounded-bl-none'}`}>
                  
                  {msg.role === 'user' ? (
                    <div className="flex flex-col items-end">
                      {msg.attachment && (
                        <div className={`mb-2 inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border ${msg.isCancelled ? 'bg-gray-300 text-gray-600 border-gray-400' : 'bg-blue-500 text-white border-blue-400'}`}>
                          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path></svg>
                          {msg.attachment}
                        </div>
                      )}
                      <div className="whitespace-pre-wrap text-right">{msg.content}</div>
                    </div>
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
            {(attachedFile || isUploading) && (
              <div className="mb-2 flex items-center">
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-100">
                  <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path></svg>
                  {isUploading ? `Uploading ${attachedFile}...` : attachedFile}
                  {!isUploading && (
                    <button 
                      onClick={() => setAttachedFile(null)}
                      className="ml-1 hover:text-blue-900 focus:outline-none"
                    >
                      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                    </button>
                  )}
                </span>
              </div>
            )}
            <form onSubmit={handleSubmit} className="flex relative items-end rounded-xl border border-gray-300 bg-gray-50 overflow-hidden focus-within:border-blue-500 focus-within:ring-1 focus-within:ring-blue-500 transition-all">
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="p-3 text-gray-400 hover:text-blue-600 transition-colors focus:outline-none flex-shrink-0"
                title="Attach Document"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path></svg>
              </button>
              <input 
                type="file" 
                ref={fileInputRef} 
                hidden 
                accept=".pdf,.docx,.csv,.txt" 
                onChange={handleFileUpload} 
              />
              <textarea 
                ref={textareaRef}
                className="w-full bg-transparent max-h-32 min-h-[56px] py-3 pl-2 pr-12 outline-none resize-none text-gray-800 placeholder-gray-400 overflow-y-auto"
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
              {isLoading ? (
                <button 
                  type="button" 
                  onClick={handleCancel}
                  className="absolute right-2 bottom-2 p-2 rounded-lg bg-gray-600 hover:bg-gray-700 text-white transition-colors flex items-center justify-center"
                  title="Stop generating"
                >
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><rect x="6" y="6" width="12" height="12" rx="2" ry="2"></rect></svg>
                </button>
              ) : (
                <button 
                  type="submit" 
                  disabled={!input.trim() || isUploading}
                  className="absolute right-2 bottom-2 p-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white disabled:bg-gray-300 disabled:text-gray-500 transition-colors flex items-center justify-center"
                  title="Send message"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
                </button>
              )}
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