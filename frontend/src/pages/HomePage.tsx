import React, { useState } from 'react';
import { ImageUploader } from '../components/ImageUploader';
import { FeedbackDisplay } from '../components/FeedbackDisplay';
import { ProblemSelector } from '../components/ProblemSelector';
import { SubmissionHistoryList } from '../components/SubmissionHistoryList';
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
    const handleTopicChange = (topicId: string) => {
        setSelectedTopicId(topicId);
        setSelectedProblemId('');
        setResult(null);
        setUploadError(null);
    };

    const handleProblemChange = (problemId: string) => {
        setSelectedProblemId(problemId);
        setResult(null);
        setUploadError(null);
    };

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
                    <ProblemSelector
                        topics={topics}
                        problems={problems}
                        selectedTopicId={selectedTopicId}
                        selectedProblemId={selectedProblemId}
                        isLoadingTopics={isLoadingTopics}
                        isLoadingProblems={isLoadingProblems}
                        onSelectTopic={handleTopicChange}
                        onSelectProblem={handleProblemChange}
                    />

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
                    <SubmissionHistoryList
                        history={history}
                        isLoading={isLoadingHistory}
                        onSelectSubmission={viewSubmission}
                    />
                </div>
            </div>
        </div>
    );
};
