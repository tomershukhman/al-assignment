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

    useEffect(() => {
        const container = containerRef.current;
        if (!container) {
            return;
        }

        // Reset to raw text so KaTeX auto-render can parse delimiters each time.
        container.textContent = text;
        renderMathInElement(container, {
            delimiters: DEFAULT_DELIMITERS,
            throwOnError: false,
        });
    }, [text]);

    return <div ref={containerRef} className={className} />;
};
