# Math Solving Assistant

A web application where students can upload photos of their handwritten math solutions and receive pedagogical feedback on their reasoning, powered by Mathpix OCR and Claude LLM.

## Features

- **Topic Selection**: Choose from various math topics (e.g., Fractions, Linear Equations).
- **Problem Presentation**: View problems and solve them on paper.
- **Photo Upload**: Upload handwritten solutions via drag-and-drop.
- **AI Feedback**: Get instant feedback on your reasoning process, not just correctness.
- **Submission History**: Track previous attempts and feedback.

## Tech Stack

- **Frontend**: React, TypeScript, Vite
- **Backend**: Python, FastAPI
- **Database**: SQLite
- **AI/ML**: 
  - [Mathpix OCR API](https://mathpix.com/) for handwriting recognition
  - [Claude API](https://www.anthropic.com/) (or OpenAI) for reasoning evaluation

## Prerequisites

- Node.js (v18+)
- Python (v3.11+)
- `uv` package manager for Python (optional but recommended)

## Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd al-assignment
   ```

2. **Backend Setup**

   This project uses `uv` for dependency management.

   ```bash
   # Install dependencies
   uv sync

   # Run the server
   uv run uvicorn backend.main:app --reload
   ```
   
   The backend will start at `http://localhost:8000`.

3. **Frontend Setup**

   ```bash
   cd frontend

   # Install dependencies
   npm install

   # Start the development server
   npm run dev
   ```
   
   The frontend will be available at `http://localhost:5173`.

## Configuration

Create a `.env` file in the root directory with the following keys:

```ini
# Mathpix OCR
MATHPIX_APP_ID=your_app_id
MATHPIX_APP_KEY=your_app_key

# LLM Provider (Claude recommended)
ANTHROPIC_API_KEY=your_anthropic_key
# OR
OPENAI_API_KEY=your_openai_key
```

## Usage

1. Start both backend and frontend servers.
2. Open the application in your browser.
3. Select a topic and a problem.
4. Upload a photo of your handwritten solution (test images are available in `example-imgs/` or linked in guidelines).
5. View the AI-generated feedback.
