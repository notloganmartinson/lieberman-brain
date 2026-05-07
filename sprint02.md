# SPRINT 2: The React Frontend

## Objective
Build the "Perplexity-style" chat interface using React, Vite, and Tailwind CSS. 

## Architecture Details
1. **Scaffolding:** Initialize a new React application in a `frontend/` directory using Vite (`npm create vite@latest frontend -- --template react`). Install Tailwind CSS.
2. **UI Layout:** * A clean, centered chat container.
   * A sticky input bar at the bottom.
   * Message bubbles for User and AI.
3. **API Integration:** Connect the chat input to the FastAPI backend running on `localhost:8000/chat`.
4. **State Management:** Use standard React `useState` to maintain the chat history array `[{role: 'user', content: '...'}, {role: 'ai', content: '...', sources: [...]}]`.

## CLI Instructions
* Provide the exact terminal commands to initialize the Vite project and install Tailwind.
* Write the `App.jsx` component encompassing the chat interface and the `fetch` call to the FastAPI backend.
* Ensure loading states (e.g., a pulsing dot or spinner) are present while waiting for the AI response.
* Stop when the frontend can successfully send a message to the backend and display the text response.
