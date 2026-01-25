import React, { useState, useEffect } from 'react';
import { ImageUploader } from '../components/ImageUploader';
import { FeedbackDisplay } from '../components/FeedbackDisplay';
import { api } from '../services/api';
import { useTopics } from '../hooks/useTopics';
import { useProblems } from '../hooks/useProblems';
import { useSubmissionHistory } from '../hooks/useSubmissionHistory';
import type { Submission, SubmissionResponse } from '../types';
import './HomePage.css';

export const HomePage: React.FC = () => {
    const { topics, isLoading: isLoadingTopics, error: topicsError } = useTopics();
    const [selectedTopicId, setSelectedTopicId] = useState<string>('');
    const { problems, isLoading: isLoadingProblems, error: problemsError } = useProblems(selectedTopicId);
    const { history, isLoading: isLoadingHistory, error: historyError, refreshHistory } = useSubmissionHistory();

    const [selectedProblemId, setSelectedProblemId] = useState<string>('');
    const [isUploading, setIsUploading] = useState(false);
    const [result, setResult] = useState<SubmissionResponse | null>(null);
    const [uploadError, setUploadError] = useState<string | null>(null);

    // Reset selected problem when topic changes
    useEffect(() => {
        setSelectedProblemId('');
    }, [selectedTopicId]);

    const handleUpload = async (file: File) => {
        if (!selectedProblemId) return;

        try {
            setIsUploading(true);
            setUploadError(null);
            const response = await api.submitSolution(selectedProblemId, file);
            setResult(response);
            // Refresh history after submission
            refreshHistory();
        } catch (err: any) {
            setUploadError(err.message || 'Failed to process your solution. Please try again.');
            console.error(err);
        } finally {
            setIsUploading(false);
        }
    };

    // Combine errors for display
    // Note: handling errors individually might be better, but we'll stick to the existing slot for now
    const displayError = uploadError || topicsError || problemsError || historyError;

    const handleResubmit = () => {
        setResult(null);
        setUploadError(null);
    };

    const handleSelectNewProblem = () => {
        setResult(null);
        setUploadError(null);
        setSelectedProblemId('');
    };

    const viewSubmission = (submission: Submission) => {
        try {
            if (submission.problem) {
                // Set context so user can easily resubmit to the same problem
                if (submission.problem.topic_id !== selectedTopicId) {
                    setSelectedTopicId(submission.problem.topic_id);
                }
                setSelectedProblemId(submission.problem.id);
            }

            const feedback = JSON.parse(submission.feedback_json);
            setResult({
                ocr_text: submission.ocr_text,
                feedback: feedback,
                imagePath: submission.image_path
            });
            window.scrollTo({ top: 0, behavior: 'smooth' });
        } catch (err) {
            console.error('Failed to parse historical feedback', err);
        }
    };

    const selectedProblem = problems.find(p => p.id === selectedProblemId);

    return (
        <div className="home-page">
            <div className="container">
                <header className="home-page__header">
                    <h1 className="home-page__title">Math Solving Assistant</h1>
                    <p className="home-page__subtitle">
                        Select a topic and problem, then upload your work to get feedback
                    </p>
                </header>

                {displayError && (
                    <div className="home-page__error card">
                        <span className="home-page__error-icon">⚠️</span>
                        <p>{displayError}</p>
                        <button className="btn btn-secondary" onClick={() => setUploadError(null)}>
                            Dismiss
                        </button>
                    </div>
                )}

                <div className="home-page__main">
                    {/* Selection Panel */}
                    <div className="home-page__selection card">
                        <div className="form-group">
                            <label htmlFor="topic-select">Select Topic</label>
                            {isLoadingTopics ? (
                                <div className="loading-inline">
                                    <div className="loading"></div>
                                    <span>Loading topics...</span>
                                </div>
                            ) : (
                                <select
                                    id="topic-select"
                                    className="select"
                                    value={selectedTopicId}
                                    onChange={(e) => setSelectedTopicId(e.target.value)}
                                >
                                    <option value="">Choose a topic...</option>
                                    {topics.map((topic) => (
                                        <option key={topic.id} value={topic.id}>
                                            {topic.name} (Grade {topic.grade_level})
                                        </option>
                                    ))}
                                </select>
                            )}
                        </div>

                        {selectedTopicId && (
                            <div className="form-group">
                                <label htmlFor="problem-select">Select Problem</label>
                                {isLoadingProblems ? (
                                    <div className="loading-inline">
                                        <div className="loading"></div>
                                        <span>Loading problems...</span>
                                    </div>
                                ) : (
                                    <select
                                        id="problem-select"
                                        className="select"
                                        value={selectedProblemId}
                                        onChange={(e) => setSelectedProblemId(e.target.value)}
                                    >
                                        <option value="">Choose a problem...</option>
                                        {problems.map((problem) => (
                                            <option key={problem.id} value={problem.id}>
                                                {problem.question}
                                            </option>
                                        ))}
                                    </select>
                                )}
                            </div>
                        )}

                        {selectedProblem && (
                            <div className="problem-preview">
                                <h3>Problem: {selectedProblem.question}</h3>
                                <p className="problem-instructions">
                                    📝 Solve this problem on paper showing all your work, then upload a photo below
                                </p>
                            </div>
                        )}
                    </div>

                    {/* Upload and Feedback Section */}
                    {selectedProblemId && !result && (
                        <ImageUploader onUpload={handleUpload} isUploading={isUploading} />
                    )}

                    {result && (
                        <>
                            <FeedbackDisplay
                                feedback={result.feedback}
                                ocrText={result.ocr_text}
                                imagePath={result.imagePath}
                            />
                            <div className="home-page__actions" style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                                <button className="btn btn-secondary" onClick={handleResubmit}>
                                    Try Again
                                </button>
                                <button className="btn btn-primary" onClick={handleSelectNewProblem}>
                                    Select Another Problem
                                </button>
                            </div>
                        </>
                    )}

                    {/* History Section */}
                    <div className="home-page__history card">
                        <h2>Recent Submissions</h2>
                        {isLoadingHistory ? (
                            <div className="loading-inline">
                                <div className="loading"></div>
                                <span>Loading history...</span>
                            </div>
                        ) : history.length === 0 ? (
                            <p className="empty-state">No submissions yet. Upload your first solution above!</p>
                        ) : (
                            <div className="history-list">
                                {history.map((submission) => {
                                    return (
                                        <div
                                            key={submission.id}
                                            className="history-item"
                                            onClick={() => viewSubmission(submission)}
                                            role="button"
                                            tabIndex={0}
                                            onKeyDown={(e) => {
                                                if (e.key === 'Enter' || e.key === ' ') {
                                                    viewSubmission(submission);
                                                }
                                            }}
                                        >
                                            <div className="history-item__status">
                                                {(() => {
                                                    try {
                                                        const feedback = JSON.parse(submission.feedback_json);
                                                        // Check explicitly for false, as undefined (legacy) might mean relevant
                                                        if (feedback.is_relevant === false) {
                                                            return <span className="badge badge-warning">⚠️ Irrelevant</span>;
                                                        }
                                                    } catch (err) {
                                                        // Ignore parse errors
                                                    }

                                                    return submission.is_correct ? (
                                                        <span className="badge badge-success">✓ Correct</span>
                                                    ) : (
                                                        <span className="badge badge-error">✗ Incorrect</span>
                                                    );
                                                })()}
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
                                })}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};
