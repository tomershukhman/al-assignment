import React from 'react';
import type { Feedback } from '../types';
import './FeedbackDisplay.css';

import { LatexRenderer } from './LatexRenderer';

interface FeedbackDisplayProps {
    feedback: Feedback;
    ocrText: string;
    imagePath?: string;
}

export const FeedbackDisplay: React.FC<FeedbackDisplayProps> = ({ feedback, ocrText, imagePath }) => {
    return (
        <div className="feedback-display">
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



            <div className="feedback-display__feedback card">
                <h3>Analysis</h3>
                <p className="feedback-display__analysis">{feedback.analysis}</p>

                {feedback.is_relevant !== false && (
                    <>
                        <h3>Detailed Steps</h3>
                        <div className="feedback-list">
                            <h4>Your steps:</h4>
                            {feedback.feedback.map((item, index) => (
                                <div key={index} className={`feedback-step ${item.status}`}>
                                    <div className="feedback-step__content">
                                        <span className="feedback-step__text">{item.step}</span>
                                        {item.comment && (
                                            <div className="feedback-step__comment">
                                                {item.comment}
                                            </div>
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

            <div className="feedback-display__ocr card">
                <h3>What we extracted from your image</h3>
                <div className="feedback-display__ocr-text">
                    <LatexRenderer text={ocrText} />
                </div>
            </div>

            {/* Display Uploaded Image if available */}
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
        </div>
    );
};
