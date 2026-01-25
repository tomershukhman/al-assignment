import React from 'react';
import type { Topic } from '../types';
import './TopicSelector.css';

interface TopicSelectorProps {
    topics: Topic[];
    onSelectTopic: (topicId: string) => void;
}

export const TopicSelector: React.FC<TopicSelectorProps> = ({ topics, onSelectTopic }) => {
    return (
        <div className="topic-selector">
            <h2 className="topic-selector__title">Choose a Math Topic</h2>
            <p className="topic-selector__subtitle">Select a topic to practice and improve your skills</p>

            <div className="topic-grid">
                {topics.map((topic) => (
                    <button
                        key={topic.id}
                        className="topic-card"
                        onClick={() => onSelectTopic(topic.id)}
                    >
                        <div className="topic-card__header">
                            <h3 className="topic-card__name">{topic.name}</h3>
                            <span className="topic-card__badge">Grade {topic.grade_level}</span>
                        </div>
                        <p className="topic-card__description">{topic.description}</p>
                        <div className="topic-card__arrow">→</div>
                    </button>
                ))}
            </div>
        </div>
    );
};
