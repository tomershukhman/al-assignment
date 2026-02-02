import { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { Problem } from '../types';

export function useProblems(topicId: string) {
    const [problems, setProblems] = useState<Problem[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const loadProblems = async () => {
        if (!topicId) {
            setProblems([]);
            return;
        }

        try {
            setIsLoading(true);
            const data = await api.getTopicProblems(topicId);
            setProblems(data);
            setError(null);
        } catch (err) {
            setError('Failed to load problems for this topic.');
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        loadProblems();
    }, [topicId]);

    return { problems, isLoading, error, refreshProblems: loadProblems };
}
