import React, { useState, useRef, useEffect } from 'react';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
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
          <div className="flex items-center justify-between w-full max-w-4xl">
            <h1 className="text-xl font-semibold text-gray-800 tracking-tight">Better Perplexity</h1>
            <div className="text-xs font-medium bg-purple-100 text-purple-700 px-3 py-1 rounded-full">
              Persona-Grounded
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
                  
                  <div className="prose prose-sm md:prose-base max-w-none break-words whitespace-pre-wrap" dangerouslySetInnerHTML={{ __html: msg.content.replace(/\n/g, '<br />') }} />
                  
                  {/* Sources display for AI */}
                  {msg.role === 'ai' && msg.sources && msg.sources.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-gray-300">
                      <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Sources</p>
                      <div className="flex flex-wrap gap-2">
                        {msg.sources.map((source, idx) => (
                          <div key={idx} className="inline-flex items-center text-xs bg-white border border-gray-200 rounded px-2 py-1 shadow-sm">
                            <span className="mr-1">{source.type === 'web' ? '🌐' : '🧠'}</span>
                            <span className="font-medium text-gray-700 truncate max-w-[150px]" title={source.title || source.label}>
                              {source.title || source.label || (source.type === 'web' ? 'Web Source' : 'Graph Source')}
                            </span>
                            {source.type === 'web' && source.url && (
                               <a href={source.url} target="_blank" rel="noopener noreferrer" className="ml-1 text-blue-500 hover:underline">
                                 ↗
                               </a>
                            )}
                          </div>
                        ))}
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
                className="w-full bg-transparent max-h-32 min-h-[56px] py-3 pl-4 pr-12 outline-none resize-none text-gray-800 placeholder-gray-400"
                placeholder="Ask a question..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit(e);
                  }
                }}
                rows={1}
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