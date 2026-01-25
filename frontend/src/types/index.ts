export interface Topic {
    id: string;
    name: string;
    description: string;
    grade_level: number;
}

export interface Problem {
    id: string;
    topic_id: string;
    question: string;
    correct_answer: string;
}

export interface Submission {
    id: number;
    problem_id: string;
    image_path: string;
    ocr_text: string;
    ocr_confidence: number;
    student_result: string;
    is_correct: boolean;
    feedback_json: string;
    created_at: string;
    problem?: Problem;
}

export interface FeedbackStep {
    step: string;
    status: 'correct' | 'incorrect';
}

export interface Feedback {
    is_correct: boolean;
    analysis: string;
    feedback: FeedbackStep[];
}

export interface SubmissionResponse {
    ocr_text: string;
    feedback: Feedback;
}
