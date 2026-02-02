import React from 'react';
import { FeedbackDisplay } from '../../FeedbackDisplay';
import './SubmissionResult.css';

interface SubmissionResultProps {
    result: any; // Raw result from tool
    variant?: 'full' | 'chat';
}

export const SubmissionResult: React.FC<SubmissionResultProps> = ({ result, variant = 'full' }) => {
    // result is the SubmissionAnalysis object from backend/response_models.py
    // It has: is_correct, confidence, extracted_text, analysis, feedback (list)

    // Map to Feedback interface expected by FeedbackDisplay
    // FeedbackDisplay expects: feedback (list), ocrText, imagePath (optional)

    // Check if result is valid
    if (!result || typeof result !== 'object') {
        return <div className="submission-result-error">Invalid result format</div>;
    }

    // Adapt to FeedbackDisplay props
    // We might need to construct a 'Feedback' object wrapper if FeedbackDisplay expects that.
    // Looking at FeedbackDisplay props: { feedback: FeedbackStep[], ocrText: string, imagePath?: string }

    return (
        <div className="submission-result-container">
            <div className="submission-badge">
                {result.is_correct ? '✅ CORRECT' : '❌ NEEDS PRACTICE'}
            </div>
            {/* Reuse existing component for detailed steps */}
            <FeedbackDisplay
                feedback={result}
                ocrText={result.extracted_text || ''}
                variant={variant}
            />
        </div>
    );
};
