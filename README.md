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
  - [Claude API](https://www.anthropic.com/) for reasoning evaluation

## Prerequisites

- Node.js (v18+)
- Python (v3.11+)
- `uv` package manager for Python (optional but recommended)



## Docker Deployment (Recommended)

The easiest way to run the entire application is using Docker:

1. **Clone the repository**
   ```bash
   git clone git@github.com:tomershukhman/al-assignment.git
   cd al-assignment
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

3. **Start the application**
   ```bash
   ./start-docker.sh
   ```
   
   Or manually:
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - Backend API: [http://localhost:8000](http://localhost:8000)
   - API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)


---

## Local Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- `uv` package manager ([installation guide](https://github.com/astral-sh/uv))

### Step-by-Step Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/tomershukhman/al-assignment
   cd al-assignment
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys (see Configuration section below)
   ```

3. **Backend Setup**

   Install dependencies using `uv`:
   ```bash
   uv sync
   ```

   Initialize the database and load seed data:
   ```bash
   uv run python -m backend.init_db
   ```

   Start the backend server:
   ```bash
   uv run uvicorn backend.main:app --reload
   ```
   
   The backend will start at `http://localhost:8000`.
   - API Documentation: `http://localhost:8000/docs`

4. **Frontend Setup**

   Open a new terminal window and navigate to the frontend directory:
   ```bash
   cd frontend
   ```

   Install dependencies:
   ```bash
   npm install
   ```

   Start the development server:
   ```bash
   npm run dev
   ```
   
   The frontend will be available at `http://localhost:5173`.

## Configuration

Create a `.env` file in the root directory with the following keys:

```ini
# Mathpix OCR
MATHPIX_APP_KEY=your_app_key

# LLM Provider (Claude recommended)
ANTHROPIC_API_KEY=your_anthropic_key
```

## Usage

1. Start both backend and frontend servers.
2. Open the application in your browser.
3. Select a topic and a problem.
4. Upload a photo of your handwritten solution (test images are available in `example-imgs/` or linked in guidelines).
5. View the AI-generated feedback.

## Enhancements & Design Changes

We've implemented several features beyond the original [project guidelines](project-guidelines.md) to improve robustness and user experience:

### 1. Robustness & Relevance Checking
The original requirements didn't specify how to handle uploaded images that aren't math solutions. We added an `is_relevant` check in the LLM analysis. If a user uploads an unrelated image (e.g., a grocery list), the system detects this and tags the submission as "Irrelevant" instead of attempting to grade it. This prevents confusing feedback on invalid inputs.

### 2. Enhanced LLM Response Structure
The original design specified a simple feedback structure. We enhanced this to track validation status per step:

**Original Plan:**
```json
{
  "result": boolean,
  "steps": ["step1", "step2"],
  "feedback": "text feedback"
}
```

**Implementation:**
```json
{
  "is_relevant": boolean,     // NEW: Checks if submission is valid
  "is_correct": boolean,
  "analysis": "brief explanation",
  "feedback": [
    {"step": "Identified LCD", "status": "correct"},
    {"step": "multiplication error line 2", "status": "incorrect"}
  ]
}
```

**Benefits**: 
- **Step-by-step Validation**: UI displays visual indicators (✓/✗) for each step.
- **Structured Analysis**: Helps students pinpoint exactly where they went wrong.

### 3. User Experience Improvements.
- **Submission History**: Enhanced with "Irrelevant" tagging to clearly distinguish between incorrect answers and non-math submissions.
- **Modern UI**: While "Functional over beautiful" was the baseline, we implemented a responsive interface using CSS variables and modern React patterns for a cleaner, professional look.

