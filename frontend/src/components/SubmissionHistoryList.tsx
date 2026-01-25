import React from 'react';
import type { Submission } from '../types';
import { SubmissionHistoryItem } from './SubmissionHistoryItem';

interface SubmissionHistoryListProps {
    history: Submission[];
    isLoading: boolean;
    onSelectSubmission: (submission: Submission) => void;
}

/**
 * Component to display the list of recent submissions.
 */
export const SubmissionHistoryList: React.FC<SubmissionHistoryListProps> = ({
    history,
    isLoading,
    onSelectSubmission,
}) => {
    return (
        <div className="home-page__history card">
            <h2>Recent Submissions</h2>
            {isLoading ? (
                <div className="loading-inline">
                    <div className="loading"></div>
                    <span>Loading history...</span>
                </div>
            ) : history.length === 0 ? (
                <p className="empty-state">No submissions yet. Upload your first solution above!</p>
            ) : (
                <div className="history-list">
                    {history.map((submission) => (
                        <SubmissionHistoryItem
                            key={submission.id}
                            submission={submission}
                            onClick={onSelectSubmission}
                        />
                    ))}
                </div>
            )}
        </div>
    );
};
