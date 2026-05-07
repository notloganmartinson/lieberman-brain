# SPRINT 4: React UI & Multipart Upload

We need to add the UI for file uploads and manage the session state.

## Tasks
1. **Session Management (`frontend/src/App.jsx`):**
   - On initial mount, generate a random `sessionId` (e.g., using `crypto.randomUUID()` or a random string) and store it in React state.
   - Add `session_id: sessionId` to the JSON body of the `/chat` POST request.

2. **File Upload UI:**
   - Next to the textarea in the chat bar, add a simple "Paperclip" icon button (`<input type="file" hidden />`).
   - Supported accepts: `.pdf,.docx,.csv,.txt`.

3. **Upload Logic:**
   - Create a `handleFileUpload(event)` function.
   - When a user selects a file, immediately show a loading state (e.g., "Uploading [filename]...").
   - Construct a `FormData` object containing the `file` and the `session_id`.
   - Send a `POST` request to `${apiUrl}/upload` (ensure headers DO NOT enforce `application/json` so the browser sets the multipart boundary).
   - Once successful, display a small badge above the chat input showing the attached filename with an "X" to visually remove it (for UI purposes; backend handles session wiping if needed, but for now just show it's active).

Output the updated `frontend/src/App.jsx`.
