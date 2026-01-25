import React from 'react';
import type { Problem } from '../types';
import './ProblemDisplay.css';

interface ProblemDisplayProps {
    problem: Problem;
}

export const ProblemDisplay: React.FC<ProblemDisplayProps> = ({ problem }) => {
    return (
        <div className="problem-display card">
            <div className="problem-display__header">
                <h2 className="problem-display__title">Problem</h2>
                <span className="problem-display__id">{problem.id}</span>
            </div>

            <div className="problem-display__question">
                {problem.question}
            </div>

            <div className="problem-display__instructions">
                <p>📝 Solve this problem on paper, showing all your work</p>
                <p>📷 Then upload a photo of your solution below</p>
            </div>
        </div>
    );
};
