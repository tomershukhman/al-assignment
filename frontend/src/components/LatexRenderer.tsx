import React, { useEffect, useRef } from 'react';
import renderMathInElement from 'katex/contrib/auto-render';
import 'katex/dist/katex.min.css';

const DEFAULT_DELIMITERS = [
    { left: '$$', right: '$$', display: true },
    { left: '$', right: '$', display: false },
    { left: '\\(', right: '\\)', display: false },
    { left: '\\[', right: '\\]', display: true },
];

interface LatexRendererProps {
    text: string;
    className?: string;
}

export const LatexRenderer: React.FC<LatexRendererProps> = ({ text, className }) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const isRendering = useRef(false);

    useEffect(() => {
        const container = containerRef.current;
        if (!container || isRendering.current) {
            return;
        }

        isRendering.current = true;

        // Use requestAnimationFrame to ensure DOM is ready and avoid race conditions
        const rafId = requestAnimationFrame(() => {
            if (!container) {
                isRendering.current = false;
                return;
            }

            try {
                // Reset to raw text so KaTeX auto-render can parse delimiters each time.
                container.textContent = text;
                renderMathInElement(container, {
                    delimiters: DEFAULT_DELIMITERS,
                    throwOnError: false,
                });
            } catch (error) {
                console.error('KaTeX rendering error:', error);
                // Fallback: just show the raw text if rendering fails
                container.textContent = text;
            } finally {
                isRendering.current = false;
            }
        });

        return () => {
            cancelAnimationFrame(rafId);
            isRendering.current = false;
        };
    }, [text]);

    return <div ref={containerRef} className={className} />;
};
