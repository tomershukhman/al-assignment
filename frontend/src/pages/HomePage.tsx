import React, { useState } from 'react';
import { ImageUploader } from '../components/ImageUploader';
import { FeedbackDisplay } from '../components/FeedbackDisplay';
import { ProblemSelector } from '../components/ProblemSelector';
import { SubmissionHistoryList } from '../components/SubmissionHistoryList';
import { LatexRenderer } from '../components/LatexRenderer';
import { api } from '../services/api';
import { useTopics } from '../hooks/useTopics';
import { useProblems } from '../hooks/useProblems';
import { useSubmissionHistory } from '../hooks/useSubmissionHistory';
import type { Submission, SubmissionResponse, Problem } from '../types';
import './HomePage.css';

export const HomePage: React.FC = () => {
    const { topics, isLoading: isLoadingTopics, error: topicsError, refreshTopics } = useTopics();
    const [selectedTopicId, setSelectedTopicId] = useState<string>('');
    const { problems, isLoading: isLoadingProblems, error: problemsError, refreshProblems } = useProblems(selectedTopicId);
    const { history, isLoading: isLoadingHistory, error: historyError, refreshHistory } = useSubmissionHistory();


    const [selectedProblemId, setSelectedProblemId] = useState<string>('');
    // Store the just-extracted problem locally in case it hasn't propagated to the list yet
    const [extractedProblem, setExtractedProblem] = useState<Problem | null>(null);
    const [isUploading, setIsUploading] = useState(false);
    const [isExtracting, setIsExtracting] = useState(false); // For problem extraction
    const [showTopicSelection, setShowTopicSelection] = useState(false);
    const [result, setResult] = useState<SubmissionResponse | null>(null);
    const [uploadError, setUploadError] = useState<string | null>(null);

    // Reset selected problem when topic changes
    const handleTopicChange = (topicId: string) => {
        setSelectedTopicId(topicId);
        setSelectedProblemId('');
        setExtractedProblem(null);
        setResult(null);
        setUploadError(null);
    };

    const handleProblemChange = (problemId: string) => {
        setSelectedProblemId(problemId);
        setExtractedProblem(null);
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

    const handleProblemUpload = async (file: File) => {
        try {
            setIsExtracting(true);
            setUploadError(null);
            const problem = await api.extractProblem(file);

            // Refresh topics to get any new topics
            await refreshTopics();

            if (selectedTopicId === problem.topic_id) {
                // If staying on the same topic, we must manually refresh problems
                await refreshProblems();
            }

            setSelectedTopicId(problem.topic_id);
            setSelectedProblemId(problem.id);
            setExtractedProblem(problem);

            // Once extracted, we can switch to "Solving" mode? 
            // The user flow is: Upload Problem -> (System sets topic/problem) -> User sees "Success" or moves to solution upload?
            // Let's assume after upload, we just want to show the problem is selected and let them solve it.
            // But now "Home" default is problem upload.
            // If we have a selected problem, we should show the solution uploader.

            setShowTopicSelection(false);
        } catch (err: any) {
            setUploadError(err.message || 'Failed to extract problem. Please try again.');
            console.error(err);
        } finally {
            setIsExtracting(false);
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
        setExtractedProblem(null);
        setShowTopicSelection(false);
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
                    {/* Main Content Area */}

                    {/* 1. If we have a result (Result Mode) */}
                    {result ? (
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
                                    Upload New Problem
                                </button>
                            </div>
                        </>
                    ) : (
                        /* 2. If we have a selected problem (Solution Upload Mode) */
                        selectedProblemId ? (
                            <div className="card">
                                <h2>Upload Your Solution</h2>

                                {/* Display Selected Problem Details */}
                                {/* We check both the list and the locally extracted problem to ensure immediate display */}
                                {(() => {
                                    const displayProblem = problems.find(p => p.id === selectedProblemId) ||
                                        (extractedProblem?.id === selectedProblemId ? extractedProblem : undefined);

                                    return displayProblem ? (
                                        <div style={{ margin: '1rem 0', padding: '1rem', backgroundColor: '#f8f9fa', borderRadius: '8px', color: '#333' }}>
                                            <h3 style={{ fontSize: '1.1rem', marginBottom: '0.5rem', color: '#333' }}>Problem:</h3>
                                            <LatexRenderer
                                                text={displayProblem.question || ''}
                                            />
                                        </div>
                                    ) : null;
                                })()}

                                <p>Great! Now upload your handwritten solution to the selected problem.</p>
                                <ImageUploader onUpload={handleUpload} isUploading={isUploading} />
                                <div style={{ textAlign: 'center', marginTop: '1rem' }}>
                                    <button className="btn btn-secondary" onClick={() => setSelectedProblemId('')}>
                                        Cancel / Select Different Problem
                                    </button>
                                </div>
                            </div>
                        ) : (
                            /* 3. Default: Problem Upload/Selection Mode */
                            !showTopicSelection ? (
                                <div className="card">
                                    <h2>Start by Uploading a Problem</h2>
                                    <p>Take a picture of a math problem. We'll identify the topic and question for you.</p>
                                    <ImageUploader
                                        onUpload={handleProblemUpload}
                                        isUploading={isExtracting}
                                        title="Upload Problem Image"
                                        description="Drag and drop the problem image here"
                                        uploadText="Extracting problem info..."
                                    />

                                    <div style={{ textAlign: 'center', marginTop: '1rem', borderTop: '1px solid #eee', paddingTop: '1rem' }}>
                                        <p style={{ fontSize: '0.9rem', color: '#666' }}>or select from existing problems</p>
                                        <button className="btn btn-secondary" onClick={() => setShowTopicSelection(true)}>
                                            Browse Existing Problems
                                        </button>
                                    </div>
                                </div>
                            ) : (
                                <>
                                    <div style={{ marginBottom: '1rem' }}>
                                        <button className="btn btn-secondary" onClick={() => setShowTopicSelection(false)}>
                                            ← Back to Problem Upload
                                        </button>
                                    </div>
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
                                </>
                            )
                        )
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
