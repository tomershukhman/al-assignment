import React from 'react';
import type { Feedback } from '../types';
import './FeedbackDisplay.css';

import { LatexRenderer } from './LatexRenderer';

interface FeedbackDisplayProps {
    feedback: Feedback;
    ocrText: string;
    imagePath?: string;
    variant?: 'full' | 'chat';
}

export const FeedbackDisplay: React.FC<FeedbackDisplayProps> = ({ feedback, ocrText, imagePath, variant = 'full' }) => {
    return (
        <div className={`feedback-display feedback-display--${variant}`}>
            {/* Header: Only for full mode or if we want a smaller badge for chat */}
            {variant === 'full' ? (
                <div className={`feedback-display__result card ${feedback.is_correct ? 'feedback-display__result--correct' : 'feedback-display__result--incorrect'}`}>
                    <div className="feedback-display__icon">
                        {feedback.is_relevant === false ? '⚠️' : (feedback.is_correct ? '✅' : '❌')}
                    </div>
                    <h2 className="feedback-display__title">
                        {feedback.is_relevant === false
                            ? 'Submission Not Relevant'
                            : (feedback.is_correct ? 'Great job!' : 'Not quite right')}
                    </h2>
                    <span className={`badge ${feedback.is_correct ? 'badge-success' : 'badge-error'}`}>
                        {feedback.is_relevant === false
                            ? 'Invalid Submission'
                            : (feedback.is_correct ? 'Correct Answer' : 'Incorrect Answer')}
                    </span>
                </div>
            ) : (
                /* Chat Variant Header */
                <div className={`feedback-chat-header ${feedback.is_correct ? 'correct' : 'incorrect'}`}>
                    <span className="feedback-chat-icon">
                        {feedback.is_relevant === false ? '⚠️' : (feedback.is_correct ? '✅' : '❌')}
                    </span>
                    <strong>{feedback.is_correct ? 'Correct!' : 'Review Expected'}</strong>
                </div>
            )}

            <div className={`feedback-display__feedback ${variant === 'chat' ? '' : 'card'}`}>
                {variant === 'full' && <h3>Analysis</h3>}
                <div className="feedback-display__analysis">
                    <LatexRenderer text={feedback.analysis} />
                </div>

                {feedback.is_relevant !== false && (
                    <>
                        {variant === 'full' && <h3>Detailed Steps</h3>}
                        <div className="feedback-list">
                            {variant === 'full' && <h4>Your steps:</h4>}
                            {feedback.feedback.map((item, index) => (
                                <div key={index} className={`feedback-step ${item.status}`}>
                                    <div className="feedback-step__content">
                                        <LatexRenderer text={item.step} className="feedback-step__text" />
                                        {item.comment && (
                                            <LatexRenderer text={item.comment} className="feedback-step__comment" />
                                        )}
                                    </div>
                                    <span className="feedback-step__icon">
                                        {item.status === 'correct' ? '✓' : '✗'}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </>
                )}
            </div>

            {/* OCR and Image: Only show in Full mode */}
            {variant === 'full' && (
                <>
                    <div className="feedback-display__ocr card">
                        <h3>What we extracted from your image</h3>
                        <div className="feedback-display__ocr-text">
                            {ocrText ? (
                                <LatexRenderer text={ocrText} />
                            ) : (
                                <p style={{ fontStyle: 'italic', color: 'var(--color-text-muted)' }}>
                                    No text could be extracted from the image.
                                </p>
                            )}
                        </div>
                    </div>

                    {imagePath && (
                        <div className="feedback-display__image card">
                            <h3>Your Uploaded Solution</h3>
                            <img
                                src={imagePath}
                                alt="Your solution"
                                style={{ maxWidth: '100%', borderRadius: '8px', border: '1px solid #e5e7eb' }}
                            />
                        </div>
                    )}
                </>
            )}
        </div>
    );
};
