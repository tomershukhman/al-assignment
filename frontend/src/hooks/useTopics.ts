import { useState, useEffect } from 'react';
import { api } from '../services/api';
import type { Topic } from '../types';

export function useTopics() {
    const [topics, setTopics] = useState<Topic[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const loadTopics = async () => {
            try {
                setIsLoading(true);
                const data = await api.getTopics();
                setTopics(data);
                setError(null);
            } catch (err) {
                setError('Failed to load topics. Please refresh the page.');
                console.error(err);
            } finally {
                setIsLoading(false);
            }
        };

        loadTopics();
    }, []);

    return { topics, isLoading, error };
}
