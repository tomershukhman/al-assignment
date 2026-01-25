import React from 'react';
import type { Feedback } from '../types';
import './FeedbackDisplay.css';

interface FeedbackDisplayProps {
    feedback: Feedback;
    ocrText: string;
}

export const FeedbackDisplay: React.FC<FeedbackDisplayProps> = ({ feedback, ocrText }) => {
    return (
        <div className="feedback-display">
            <div className={`feedback-display__result card ${feedback.is_correct ? 'feedback-display__result--correct' : 'feedback-display__result--incorrect'}`}>
                <div className="feedback-display__icon">
                    {feedback.is_correct ? '✅' : '❌'}
                </div>
                <h2 className="feedback-display__title">
                    {feedback.is_correct ? 'Great job!' : 'Not quite right'}
                </h2>
                <span className={`badge ${feedback.is_correct ? 'badge-success' : 'badge-error'}`}>
                    {feedback.is_correct ? 'Correct Answer' : 'Incorrect Answer'}
                </span>
            </div>

            <div className="feedback-display__analysis card">
                <h3>Analysis</h3>
                <p>{feedback.analysis}</p>
            </div>

            <div className="feedback-display__feedback card">
                <h3>Feedback</h3>
                <p>{feedback.feedback}</p>
            </div>

            <div className="feedback-display__ocr card">
                <h3>What we extracted from your image</h3>
                <pre className="feedback-display__ocr-text">{ocrText}</pre>
            </div>
        </div>
    );
};
