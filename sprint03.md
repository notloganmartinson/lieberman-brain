# SPRINT 3: The Perplexity UI Polish & Citations

## Objective
Elevate the React frontend from a "basic chatbot" to a "Better-Perplexity" interface by beautifully displaying the sources (Graph vs. Web) and preparing for cloud deployment.

## Architecture Details
1. **Citation Badges:** Update the UI so that when the AI responds, it renders small, clickable/hoverable badges below the message.
   * 🌐 **Web Sources:** Display the domain name of the links scraped.
   * 🧠 **Graph Sources:** Display the `label` of the Neo4j nodes traversed (e.g., "Mental Model: Trusted Distribution").
2. **Markdown Rendering:** The AI output will likely contain bolding, lists, and line breaks. Integrate `react-markdown` to properly format the AI's text in the UI.
3. **Environment Prep:** Ensure the frontend API call uses a dynamic base URL (`import.meta.env.VITE_API_URL`) so it can seamlessly switch between `localhost:8000` during dev and the live Render/Railway URL in production.

## CLI Instructions
* Provide the updated React components to handle Markdown parsing and the Citation Badges.
* Ensure the styling looks premium, minimalistic, and "agency quality" (lots of whitespace, subtle borders, modern typography).
* Provide final instructions on how to build the frontend for Vercel deployment.
