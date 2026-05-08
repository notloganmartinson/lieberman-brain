# Sprint 4: Production-Readiness (Paths & CORS)

We are preparing the backend for production deployment by fixing relative paths and security headers.

## Instructions:
1. **Production CORS Configuration:**
   - In `backend/api.py`, update the `CORSMiddleware` configuration.
   - Keep the existing localhost URLs, but add a wildcard or placeholder production URL (e.g., `"https://*.vercel.app"`, or keep it broad temporarily while in development but ensure it supports external frontends).

2. **Deployment-Safe Path Resolution:**
   - In `backend/ghostwriter.py`, check the `get_tone_context()` function.
   - Ensure the path to `tone_and_replies.txt` is robust regardless of where the script is executed from (e.g., using `Path(__file__).parent.parent.resolve() / "etl" / "data" / "tweets" / "tone_and_replies.txt"` using the `pathlib` library).
   - If `pathlib` is missing, import it. Add a fallback to return a default string if the file is completely missing in the production container.

Execute these changes across `backend/api.py` and `backend/ghostwriter.py`.
