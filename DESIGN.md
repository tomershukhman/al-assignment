# Technical Design Document - Math Solving Assistant

## 1. Architecture

The system will follow a classic Client-Server architecture utilizing a REST API.

### High-Level Components

*   **Frontend**: Single Page Application (SPA) built with **React** (Vite).
    *   Focus on a simple, functional UI.
    *   Handles image capture/upload and displaying feedback.
*   **Backend**: **FastAPI** (Python).
    *   Handles business logic, database interactions, and orchestrates external API calls.
*   **Database**: **SQLite**.
    *   Chosen for simplicity and ease of local setup (filesystem based).
    *   Can be easily migrated to PostgreSQL if needed.
*   **External Services**:
    *   **Mathpix API**: For Optical Character Recognition (OCR) of handwritten math.
    *   **LLM Provider**: **Claude 3.5 Sonnet** (or newer). specifically `claude-sonnet-4-20250514` as per guidelines.

## 2. Data Model

We will use **SQLModel** (built on Pydantic & SQLAlchemy) for ORM definition.

### Entities

#### Topic
Represents a math subject category.
*   `id`: String (PK) - e.g., "fractions-addition"
*   `name`: String
*   `description`: String
*   `grade_level`: Integer

#### Problem
Specific math problems belonging to a topic.
*   `id`: String (PK) - e.g., "frac-add-001"
*   `topic_id`: String (FK -> Topic.id)
*   `question`: String (The problem text/LaTeX)
*   `correct_answer`: String (The ground truth answer)

#### Submission
A student's attempt at solving a problem.
*   `id`: Integer (PK, Auto-increment)
*   `problem_id`: String (FK -> Problem.id)
*   `image_path`: String (Path to stored image locally)
*   `ocr_text`: String (Raw text extracted from Mathpix)
*   `ocr_confidence`: Float
*   `student_result`: String (Parsed final answer from student)
*   `is_correct`: Boolean (LLM determined correctness)
*   `feedback_json`: JSON (Structured analysis from LLM)
*   `created_at`: DateTime

## 3. API Design

RESTful endpoints adhering to OpenAPI standards.

### Endpoints

#### Topics & Problems
*   `GET /api/topics`
    *   Returns list of all available topics.
*   `GET /api/topics/{topic_id}/problems`
    *   Returns list of problems for a specific topic.
*   `GET /api/problems/{problem_id}`
    *   Returns details of a single problem.

#### Submissions
*   `POST /api/submissions`
    *   **Body**: `Multipart/form-data`
        *   `file`: Image file
        *   `problem_id`: String
    *   **Process**:
        1.  Save image to local disk.
        2.  Call Mathpix API to extract LaTex/Text.
        3.  Call LLM API with Context (Problem, Correct Info, OCR Text).
        4.  Save Submission to DB.
    *   **Response**: `Submission` object with feedback.
*   `GET /api/submissions`
    *   Returns history of submissions (latest first).
*   `GET /api/submissions/{submission_id}`
    *   Returns full details including image URL and feedback.

#### Static Files
*   `GET /api/uploads/{filename}`
    *   Serves the uploaded images.

## 4. LLM Strategy

We will use **Claude Sonnet 4** (`claude-sonnet-4-20250514`) to act as a "Pedagogical Validator".

### Workflow
1.  **Input Construction**:
    *   **System Prompt**: "You are a helpful math tutor. You analyze student work steps, identify errors in reasoning, and provide encouraging feedback. Do not just give the answer."
    *   **User Content**:
        *   Problem: `{question}`
        *   Expected Answer: `{correct_answer}`
        *   Student Work (OCR): `{ocr_text}`
2.  **Evaluation Logic**:
    *   Compare `Student Work` against `Expected Answer`.
    *   Check intermediate steps for logical flow.
    *   Determine `is_correct`.
3.  **Structured Output**:
    *   We will require a JSON response from the LLM to ensure UI consistency.
    *   `result`: boolean
    *   `steps`: list of strings (e.g., ["Identified LCD", "multiplication error line 2"])
    *   `feedback`: string (human readable note)

### Prompt Example
```text
Analyze the following student submission for the problem: "{question}".
The correct answer is: "{correct_answer}".
The student's handwritten work was interpreted as:
"{ocr_text}"

Return a JSON object with:
- is_correct: boolean
- analysis: string (brief explanation of their method)
- feedback: string (constructive feedback for the student)
```

## 5. Error Handling

### OCR Failures
*   **Scenario**: Image is blurry, blank, or non-math.
*   **Detection**: Mathpix returns low confidence or empty text.
*   **Action**: Return 400 Bad Request to client with "Could not read handwriting. Please upload a specific clear photo."

### LLM Hallucinations / parse errors
*   **Scenario**: LLM returns invalid JSON or hallucinates steps not in OCR.
*   **Action**:
    *   Use Pydantic for output parsing validation.
    *   Retry logic (max 1 retry).
    *   Fallback: "Analysis unavailable, but here is the raw extracted text."

### System/API Limits
*   **Scenario**: API Rate limits (Mathpix/OpenAI).
*   **Action**: Implement exponential backoff for internal retries. Return 503 Service Unavailable if downstream APIs are down.
