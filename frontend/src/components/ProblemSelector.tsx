import React from 'react';
import type { Topic, Problem } from '../types';
import { LatexRenderer } from './LatexRenderer';

interface ProblemSelectorProps {
    topics: Topic[];
    problems: Problem[];
    selectedTopicId: string;
    selectedProblemId: string;
    isLoadingTopics: boolean;
    isLoadingProblems: boolean;
    onSelectTopic: (topicId: string) => void;
    onSelectProblem: (problemId: string) => void;
}

/**
 * Component for selecting a math topic and a specific problem.
 */
export const ProblemSelector: React.FC<ProblemSelectorProps> = ({
    topics,
    problems,
    selectedTopicId,
    selectedProblemId,
    isLoadingTopics,
    isLoadingProblems,
    onSelectTopic,
    onSelectProblem,
}) => {
    const selectedProblem = problems.find(p => p.id === selectedProblemId);

    return (
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
                        onChange={(e) => onSelectTopic(e.target.value)}
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
                            onChange={(e) => onSelectProblem(e.target.value)}
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
                    <h3>Problem: <LatexRenderer text={selectedProblem.question} /></h3>
                    <p className="problem-instructions">
                        📝 Solve this problem on paper showing all your work, then upload a photo below
                    </p>
                </div>
            )}
        </div>
    );
};
