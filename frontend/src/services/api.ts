import type { Topic, Problem, Submission, SubmissionResponse } from '../types';

const API_BASE = '/api';

class ApiError extends Error {
    status: number;

    constructor(status: number, message: string) {
        super(message);
        this.name = 'ApiError';
        this.status = status;
    }
}

async function handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new ApiError(response.status, error.detail || response.statusText);
    }
    return response.json();
}

export const api = {
    async getTopics(): Promise<Topic[]> {
        const response = await fetch(`${API_BASE}/topics`);
        return handleResponse<Topic[]>(response);
    },

    async getTopicProblems(topicId: string): Promise<Problem[]> {
        const response = await fetch(`${API_BASE}/topics/${topicId}/problems`);
        return handleResponse<Problem[]>(response);
    },

    async getProblem(problemId: string): Promise<Problem> {
        const response = await fetch(`${API_BASE}/problems/${problemId}`);
        return handleResponse<Problem>(response);
    },

    async submitSolution(problemId: string, imageFile: File): Promise<SubmissionResponse> {
        const formData = new FormData();
        formData.append('file', imageFile);
        formData.append('problem_id', problemId);

        const response = await fetch(`${API_BASE}/submissions`, {
            method: 'POST',
            body: formData,
        });
        return handleResponse<SubmissionResponse>(response);
    },

    async getSubmissions(limit = 50, offset = 0): Promise<Submission[]> {
        const response = await fetch(`${API_BASE}/submissions?limit=${limit}&offset=${offset}`);
        return handleResponse<Submission[]>(response);
    },

    async getSubmission(submissionId: number): Promise<Submission> {
        const response = await fetch(`${API_BASE}/submissions/${submissionId}`);
        return handleResponse<Submission>(response);
    },
};

export { ApiError };
