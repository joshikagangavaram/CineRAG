# Tollywood RAG Chatbot

A small Retrieval-Augmented Generation chatbot about the Tollywood, or Telugu-language, film industry.

The app uses a local knowledge base in `data/tollywood_kb.json`, retrieves the most relevant passages with a pure-Python TF-IDF style retriever, and returns a grounded answer with source snippets.

## Project Structure

```text
.
├── backend/
│   ├── app.py
│   └── rag_engine.py
├── data/
│   └── tollywood_kb.json
└── frontend/
    ├── index.html
    ├── script.js
    └── styles.css
```

## Run With Streamlit

Start the Streamlit app:

```powershell
streamlit run streamlit_app.py
```

Or run it with `uv`:

```powershell
uv run streamlit run streamlit_app.py
```

Then open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

## Run Backend and HTML Frontend

Start the backend:

```powershell
python backend/app.py
```

Then open:

```text
frontend/index.html
```

Ask questions like:

- `What is Tollywood known for?`
- `Tell me about Baahubali and RRR`
- `Who are important directors in Telugu cinema?`
- `How did Telugu cinema become pan-Indian?`

## Add More Knowledge

Edit `data/tollywood_kb.json` and add more entries with:

```json
{
  "id": "unique-id",
  "title": "Short title",
  "category": "topic",
  "text": "Knowledge passage..."
}
```

Restart the backend after changing the knowledge base.

## Put This Project on GitHub

Create a new empty repository on GitHub first. Do not add a README, `.gitignore`, or license there because this project already has local files.

Then run these commands from this project folder:

```powershell
git init
git add .
git commit -m "Create Tollywood RAG chatbot"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
git push -u origin main
```

Replace `YOUR_USERNAME` and `YOUR_REPOSITORY_NAME` with your real GitHub account and repo name.

## Deployment Note

GitHub Pages can host only the static frontend files. This chatbot also needs the Python backend in `backend/app.py`, so the full app should be hosted on a Python-friendly service such as Render, Railway, Fly.io, or a VPS.

If you use GitHub Pages for only the frontend, update `API_URL` in `frontend/script.js` to point to your hosted backend URL.
