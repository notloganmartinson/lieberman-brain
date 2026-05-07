# Objective
Implement a professional request cancellation feature using `AbortController` to stop in-flight AI generation, and prevent prompt submission while files are uploading.

# Key Files & Context
- `frontend/src/App.jsx`: The React component handling the chat UI and network requests.

# Implementation Steps

1. **State Management:**
   - Add `const [abortController, setAbortController] = useState(null);` to track the active fetch request.

2. **Upload Guard (`handleSubmit`):**
   - At the beginning of `handleSubmit`, add `if (!input.trim() || isUploading) return;` to block submission via Enter key if a file is uploading.

3. **AbortController Integration (`handleSubmit`):**
   - Before `setIsLoading(true)`, create a controller: `const controller = new AbortController(); setAbortController(controller);`
   - Add `signal: controller.signal` to the `fetch` options.
   - In the `catch (error)` block, check if `error.name === 'AbortError'`. If true, log "Request cancelled" and return early so no error message is appended to the chat.

4. **Cancel Handler:**
   - Create `const handleCancel = () => { if (abortController) { abortController.abort(); } setIsLoading(false); };`

5. **UI Updates (Submit/Cancel Button):**
   - Change the button inside the form to conditionally render based on `isLoading`.
   - **If `isLoading`:**
     - Render a `<button type="button" onClick={handleCancel}>` with a Stop (Square/X) icon.
   - **If NOT `isLoading`:**
     - Render the standard `<button type="submit">` with the Send arrow.
     - Add `isUploading` to the `disabled` condition: `disabled={!input.trim() || isUploading}`.

# Verification & Testing
- Ensure the user cannot submit the prompt while the "Uploading [filename]..." badge is present.
- Ensure clicking the stop icon immediately halts the loading animation and prevents the AI message from rendering.