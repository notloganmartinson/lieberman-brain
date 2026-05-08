# Sprint 3: API State & Latency Optimization

We are updating `backend/api.py` and `backend/ghostwriter.py` to remove hardcoded state and speed up the LLM router.

## Instructions:
1. **Dynamic Timezones:**
   - In `backend/api.py`, update the `ChatRequest` Pydantic model to include an optional field: `user_timezone: str = "US/Central"`.
   - Pass `request.user_timezone` into the `generate_content` function call in the `/chat` endpoint.
   - In `backend/ghostwriter.py`, update the `generate_content` signature to accept `user_timezone`.
   - In the `is_schedule_intent` block, replace the hardcoded "US/Central" string with the dynamic `user_timezone` variable.

2. **Semantic Router Speed:**
   - In `backend/api.py`, update the `classify_intent` function.
   - Change the model from `gemini-2.5-flash` to `gemini-1.5-flash-8b` to ensure the fastest possible semantic routing before the parallel retrieval path begins.

Execute these changes across `backend/api.py` and `backend/ghostwriter.py`.
