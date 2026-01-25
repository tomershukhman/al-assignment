/**
 * Represents a topic or category of math problems.
 */
export interface Topic {
    /** Unique identifier for the topic */
    id: string;
    /** Display name of the topic */
    name: string;
    /** Detailed description of what the topic covers */
    description: string;
    /** The target grade level for this topic */
    grade_level: number;
}

/**
 * Represents a specific math problem within a topic.
 */
export interface Problem {
    /** Unique identifier for the problem */
    id: string;
    /** ID of the topic this problem belongs to */
    topic_id: string;
    /** The text of the question */
    question: string;
    /** The expected correct answer (hidden from student) */
    correct_answer: string;
}

/**
 * Represents a student's submission for a problem.
 */
export interface Submission {
    /** Unique numerical ID of the submission */
    id: number;
    /** ID of the problem being solved */
    problem_id: string;
    /** URL/path to the uploaded image */
    image_path: string;
    /** Text extracted from the image via OCR */
    ocr_text: string;
    /** Confidence score of the OCR extraction (0-100) */
    ocr_confidence: number;
    /** The final result/answer parsed from the student's work */
    student_result: string;
    /** Whether the submission was evaluated as correct */
    is_correct: boolean;
    /** Raw JSON string containing detailed analysis and feedback */
    feedback_json: string;
    /** Timestamp of when the submission was created */
    created_at: string;
    /** The associated problem object (optional, joined in some queries) */
    problem?: Problem;
}

/**
 * Represents a single step in the feedback analysis.
 */
export interface FeedbackStep {
    /** Description of the step taken by the student */
    step: string;
    /** Evaluation of the step correctness */
    status: 'correct' | 'incorrect';
}

/**
 * Structured feedback parsed from the LLM response.
 */
export interface Feedback {
    /** Whether the submission is relevant to the problem (optional, defaults to true if undefined) */
    is_relevant?: boolean;
    /** Whether the final answer is correct */
    is_correct: boolean;
    /** High-level analysis or explanation of the student's work */
    analysis: string;
    /** Detailed breakdown of steps */
    feedback: FeedbackStep[];
}

/**
 * Response structure returned by the submission API.
 */
export interface SubmissionResponse {
    /** OCR extracted text */
    ocr_text: string;
    /** Parsed feedback object */
    feedback: Feedback;
    /** Path to the uploaded image */
    imagePath?: string;
}
