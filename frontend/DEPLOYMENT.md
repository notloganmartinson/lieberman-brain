# Vercel Deployment Instructions

To deploy this Better-Perplexity application to Vercel, follow these steps:

## Prerequisites
1. Ensure your code is pushed to a GitHub repository.
2. Have a Vercel account linked to your GitHub.
3. Have your backend API deployed (e.g., on Render, Railway, or Heroku) so you have a live `VITE_API_URL`.

## Steps
1. Log in to your [Vercel Dashboard](https://vercel.com/dashboard).
2. Click **Add New...** -> **Project**.
3. Import your GitHub repository.
4. In the "Configure Project" screen:
   - **Framework Preset:** Vercel should automatically detect **Vite**.
   - **Root Directory:** Click "Edit" and type `frontend`. Vercel needs to know the React app is inside the `frontend` folder, not the root of the repo.
5. Open the **Environment Variables** section:
   - Add a new variable: 
     - **Name:** `VITE_API_URL`
     - **Value:** `https://your-live-backend-url.com` (Replace this with the actual URL of your deployed FastAPI server).
6. Click **Deploy**.

Vercel will now build your frontend (`npm run build`) and deploy it to a live URL. When users interact with the chat, the frontend will use the `VITE_API_URL` to route requests to your production backend instead of localhost.