import { useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';
import type { Submission } from '../types';

export function useSubmissionHistory() {
    const [history, setHistory] = useState<Submission[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const loadHistory = useCallback(async () => {
        try {
            setIsLoading(true);
            const data = await api.getSubmissions(10, 0);
            setHistory(data);
            setError(null);
        } catch (err) {
            console.error('Failed to load history:', err);
            setError('Failed to load submission history.');
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        loadHistory();
    }, [loadHistory]);

    return { history, isLoading, error, refreshHistory: loadHistory };
}
