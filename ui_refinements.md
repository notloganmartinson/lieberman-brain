# Objective
Update the UI to attach uploaded files to the user's chat bubble, clear them from the input bar after sending, and style cancelled user prompts in grey to visually indicate they were stopped.

# Key Files & Context
- `frontend/src/App.jsx`: The React component managing state and chat rendering.

# Implementation Steps

1. **Attach File to Message Bubble:**
   - In `handleSubmit`, update the initial message creation: `const userMessage = { role: 'user', content: input, attachment: attachedFile };`
   - After adding the message to state, call `setAttachedFile(null);` so it disappears from the input bar.
   - Update the message rendering logic. Inside the user bubble (`msg.role === 'user'`), conditionally render a styled badge if `msg.attachment` exists (using a small paperclip icon and the filename).

2. **Cancelled Message Styling:**
   - In `handleCancel`, update the messages state to mark the most recent user message as cancelled:
     ```javascript
     setMessages((prev) => {
       const newMessages = [...prev];
       const lastMsg = newMessages[newMessages.length - 1];
       if (lastMsg && lastMsg.role === 'user') {
         lastMsg.isCancelled = true;
       }
       return newMessages;
     });
     ```
   - Update the user bubble CSS classes based on `msg.isCancelled`.
   - If `msg.isCancelled` is true, use a grey theme (e.g., `bg-gray-400 text-white`).
   - If false, retain the standard `bg-blue-600 text-white`.

# Verification & Testing
- Send a prompt with a file. Ensure the file badge jumps into the sent blue bubble and the input bar is cleared.
- While the response is loading, press the Stop button. Ensure the loading animation stops, the AI response is not printed, and the blue user bubble immediately turns grey.