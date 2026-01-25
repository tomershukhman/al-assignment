import React from 'react';
import type { Submission } from '../types';

interface SubmissionHistoryItemProps {
    submission: Submission;
    onClick: (submission: Submission) => void;
}

/**
 * Component to render a single submission in the history list.
 */
export const SubmissionHistoryItem: React.FC<SubmissionHistoryItemProps> = ({ submission, onClick }) => {
    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' || e.key === ' ') {
            onClick(submission);
        }
    };

    const renderStatusBadge = () => {
        try {
            const feedback = JSON.parse(submission.feedback_json);
            // Check explicitly for false, as undefined (legacy) might mean relevant
            if (feedback.is_relevant === false) {
                return <span className="badge badge-warning">⚠️ Irrelevant</span>;
            }
        } catch (err) {
            // Ignore parse errors, proceed to correct/incorrect check
        }

        return submission.is_correct ? (
            <span className="badge badge-success">✓ Correct</span>
        ) : (
            <span className="badge badge-error">✗ Incorrect</span>
        );
    };

    return (
        <div
            className="history-item"
            onClick={() => onClick(submission)}
            role="button"
            tabIndex={0}
            onKeyDown={handleKeyDown}
        >
            <div className="history-item__status">
                {renderStatusBadge()}
            </div>
            <div className="history-item__content">
                <p className="history-item__problem">
                    {submission.problem?.question || submission.problem_id}
                </p>
                <p className="history-item__date">
                    {new Date(submission.created_at).toLocaleDateString()} at{' '}
                    {new Date(submission.created_at).toLocaleTimeString()}
                </p>
            </div>
        </div>
    );
};
