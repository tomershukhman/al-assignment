## Math Solving - Show Your Work, Get Feedback

### Overview

Build a web application where students **photograph their handwritten math solutions** and receive feedback on their reasoning—not just whether the answer is right or wrong.

---

## The Product

### User Stories

> As a student, I want to upload a photo of my handwritten math work and get feedback on my solution process, so that I can understand where my reasoning went right or wrong—not just whether I got the correct answer.
> As a student, I want to be able to see previously solved math work and feedback overtime.

### Core Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   1. SELECT TOPIC          2. VIEW PROBLEM                      │
│   ┌─────────────────┐      ┌─────────────────────────────────┐  │
│   │ Adding Fractions│      │                                 │  │
│   │ Linear Equations│ ──▶  │  Solve: 2/3 + 3/4 = ?           │  │
│   │ Percentages     │      │                                 │  │
│   └─────────────────┘      │  Show your work on paper,       │  │
│                            │  then upload a photo.           │  │
│                            └─────────────────────────────────┘  │
│                                           │                     │
│                                           ▼                     │
│   4. GET FEEDBACK          3. UPLOAD PHOTO                      │
│   ┌─────────────────────┐  ┌─────────────────────────────────┐  │
│   │ ✓ Correct answer!   │  │                                 │  │
│   │                     │  │   📷 Upload photo of your work  │  │
│   │ Your steps:         │◀─│      (drag & drop or click)     │  │
│   │ • Found LCD of 12 ✓ │  │                                 │  │
│   │ • Converted 2/3 ✓   │  └─────────────────────────────────┘  │
│   │ • Added correctly ✓ │                                       │
│   └─────────────────────┘                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Core Features

1. **Topic Selection**: Student chooses a math topic to practice

2. **Problem Presentation**: System displays a problem from the selected topic

3. **Photo Upload**: Student uploads a photo of their handwritten solution
   - Support drag-and-drop and file picker
   - Accept common image formats (JPEG, PNG)

4. **Solution Extraction**: Use Mathpix OCR to extract mathematical content from the image
   - Parse the response into usable data
   - Handle extraction failures gracefully

5. **AI Evaluation**: Use an LLM to evaluate the extracted solution
   - Determine if the final answer is correct
   - Analyze the student's work and reasoning
   - Provide pedagogically appropriate feedback

6. **Progress Tracking**: Display problems previously attempted with their feedback

---

## Technical Requirements

### Stack

| Component | Requirement |
|-----------|-------------|
| **Frontend** | Any framework or plain HTML/JS. Functional over beautiful. |
| **Backend** | Python with FastAPI preferred, but use whatever you're comfortable with |
| **Data Store** | PostgreSQL or SQLite |
| **LLM Integration** | Claude API or OpenAI API |
| **External API** | Mathpix OCR API (for handwriting recognition) |

### External APIs

**Mathpix OCR API**
- Documentation: https://docs.mathpix.com/
- Endpoint: `POST https://api.mathpix.com/v3/text`
- Free tier: 1,000 requests/month
- Sign up: https://mathpix.com/ocr

**Claude API**
- Documentation: https://docs.anthropic.com/
- Sign up: https://console.anthropic.com/

**OpenAI API** (alternative)
- Documentation: https://platform.openai.com/docs
- Sign up: https://platform.openai.com/

---

## Seed Data

You can use this seed data of math problems grouped by topic to bootstrap your database.
You may extend it if you wish—for example, if you think additional metadata would help your system provide better feedback.

```json
{
  "topics": [
    {
      "id": "fractions-addition",
      "name": "Adding Fractions",
      "description": "Adding fractions with like and unlike denominators",
      "grade_level": 5,
      "problems": [
        {
          "id": "frac-add-001",
          "question": "What is 1/4 + 1/2?",
          "correct_answer": "3/4"
        },
        {
          "id": "frac-add-002",
          "question": "What is 2/3 + 3/4?",
          "correct_answer": "17/12"
        },
        {
          "id": "frac-add-003",
          "question": "What is 3/5 + 1/4?",
          "correct_answer": "17/20"
        }
      ]
    },
    {
      "id": "linear-equations",
      "name": "Solving Linear Equations",
      "description": "Solving one-variable linear equations",
      "grade_level": 7,
      "problems": [
        {
          "id": "lin-eq-001",
          "question": "Solve for x: 2x + 5 = 13",
          "correct_answer": "x = 4"
        },
        {
          "id": "lin-eq-002",
          "question": "Solve for x: 3(x - 2) = 15",
          "correct_answer": "x = 7"
        },
        {
          "id": "lin-eq-003",
          "question": "Solve for x: 4x - 7 = 2x + 9",
          "correct_answer": "x = 8"
        }
      ]
    },
    {
      "id": "percentages",
      "name": "Percentage Calculations",
      "description": "Finding percentages of numbers and percentage changes",
      "grade_level": 6,
      "problems": [
        {
          "id": "pct-001",
          "question": "What is 25% of 80?",
          "correct_answer": "20"
        },
        {
          "id": "pct-002",
          "question": "A shirt costs $40 and is on sale for 30% off. What is the sale price?",
          "correct_answer": "$28"
        },
        {
          "id": "pct-003",
          "question": "If 45 is 75% of a number, what is the number?",
          "correct_answer": "60"
        }
      ]
    }
  ]
}
```

---

## Test Images

To help you develop and test without writing math by hand, we've provided sample handwritten solution images: [Test Images Folder](https://drive.google.com/drive/folders/1U63zGH8Apw-AkOR0Nhoj5tn9pWbZQWPD?usp=drive_link)

| Image | Topic | Description |
|-------|-------|-------------|
| `correct_clean.png` | Adding Fractions | Correct solution with clear steps |
| `correct_messy.png` | Solving Linear Equations | Correct solution, messier handwriting |
| `wrong_common_error.png` | Adding Fractions | Incorrect answer with work shown |
| `minimal_work.png` | Percentage Calculations | Correct answer but minimal steps shown |
| `blurry.png` | Percentage Calculations | Low quality image |

---

## Deliverables

### 1. GitHub Repository

Your repository should include:

```
/
├── README.md              # Setup instructions
├── DESIGN.md              # Technical design document (see below)
├── backend/
├── frontend/
├── seed_data.json
└── docker-compose.yml     # (Optional) One-command setup
```

### 2. README.md

- How to run the application locally
- Environment variables needed
- Any assumptions or scope decisions you made

### 3. DESIGN.md

Before building, write a brief technical design document covering:

1. **Architecture**: How you plan to structure the system
2. **Data Model**: What you'll store and how
3. **API Design**: Key endpoints and their responsibilities
4. **LLM Strategy**: How you'll approach the evaluation/feedback generation
5. **Error Handling**: How you'll handle OCR failures, unclear images, etc.

This document should represent your thinking *before* implementation. It's fine if the final implementation diverges—just note significant changes in the README.

---

## What We're Looking For

- **Working software**: Does the core flow work end-to-end?
- **Code quality**: Is the code well-organized and understandable?
- **Thoughtful LLM usage**: Does the system produce genuinely useful feedback for students?
- **Resilience**: How does the system handle errors and edge cases?
- **Clear thinking**: Does the design document show good technical judgment?

---

## Expectations

We value working software over perfection. If you're spending a lot of time on this, step back and ship what you have with notes on what you'd improve.

It's completely fine to:
- Use a minimal UI
- Limit scope if you document your reasoning
- Have rough edges if the core flow works well

What matters most is that we can see your thinking and run your code.

---

## Tips

1. **Start with Mathpix**: Get image → extracted text working first. Everything depends on this.
2. **Test with provided images**: Use our test images before trying your own handwriting.
3. **Define your API and data models early**: Clear contracts make implementation smoother.
4. **Think about pedagogy**: What makes feedback actually helpful for a student learning math?
5. **Handle the unhappy paths**: What happens when Mathpix can't read the image? When the student uploads something unexpected?

---

## Questions?

If you have questions about the requirements or expectations (or have issues with the api's or setup), please reach out to **adam.rosenthal@adaptive-learning.ai**.

Good luck!

---

## Appendix: API Quick Reference

### Mathpix

```python
import httpx
import base64

def extract_math(image_path: str) -> dict:
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()
    
    response = httpx.post(
        "https://api.mathpix.com/v3/text",
        headers={
            "app_id": MATHPIX_APP_ID,
            "app_key": MATHPIX_APP_KEY,
        },
        json={
            "src": f"data:image/jpeg;base64,{image_data}",
            "formats": ["text", "latex_styled"],
        },
    )
    return response.json()
```

### Claude

```python
import anthropic

client = anthropic.Anthropic()
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Your prompt here"}],
)
```

### OpenAI

```python
from openai import OpenAI

client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Your prompt here"}],
)
```
