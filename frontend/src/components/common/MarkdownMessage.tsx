import React from 'react';

interface MarkdownMessageProps {
  content: string;
  className?: string;
}

export const MarkdownMessage: React.FC<MarkdownMessageProps> = ({ content, className = '' }) => {
  if (!content) return null;

  // Split content into lines to handle blocks (headings, lists, paragraphs)
  const lines = content.split('\n');

  // Helper to parse inline markdown: **bold**, *italic*, `code`
  const renderInline = (text: string): React.ReactNode[] => {
    // Regex splits by: **bold**, *italic*, or `code`
    const regex = /(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g;
    const parts = text.split(regex);

    return parts.map((part, index) => {
      if (!part) return null;

      // Bold: **text**
      if (part.startsWith('**') && part.endsWith('**') && part.length >= 4) {
        return (
          <strong key={index} className="font-bold text-slate-900">
            {part.slice(2, -2)}
          </strong>
        );
      }

      // Italic: *text*
      if (part.startsWith('*') && part.endsWith('*') && part.length >= 2) {
        return (
          <em key={index} className="italic text-slate-700">
            {part.slice(1, -1)}
          </em>
        );
      }

      // Code: `code`
      if (part.startsWith('`') && part.endsWith('`') && part.length >= 2) {
        return (
          <code
            key={index}
            className="font-mono bg-slate-200/80 text-blue-700 px-1.5 py-0.5 rounded text-[11px] font-semibold"
          >
            {part.slice(1, -1)}
          </code>
        );
      }

      // Plain text
      return <React.Fragment key={index}>{part}</React.Fragment>;
    });
  };

  return (
    <div className={`space-y-1.5 text-xs leading-relaxed text-slate-700 ${className}`}>
      {lines.map((line, idx) => {
        const trimmed = line.trim();

        if (!trimmed) {
          // Empty line / spacer
          return <div key={idx} className="h-1.5" />;
        }

        // Numbered list item: e.g. "1. ..."
        const numberedMatch = trimmed.match(/^(\d+)\.\s+(.*)$/);
        if (numberedMatch) {
          return (
            <div key={idx} className="flex items-start gap-2 pl-2">
              <span className="font-bold text-slate-900 min-w-[1.2rem] text-right font-mono">
                {numberedMatch[1]}.
              </span>
              <div className="flex-1">{renderInline(numberedMatch[2])}</div>
            </div>
          );
        }

        // Bullet list item: e.g. "- ..." or "* ..." or "• ..."
        const bulletMatch = trimmed.match(/^[-*•]\s+(.*)$/);
        if (bulletMatch) {
          return (
            <div key={idx} className="flex items-start gap-2 pl-2">
              <span className="text-blue-500 font-bold leading-none mt-1">•</span>
              <div className="flex-1">{renderInline(bulletMatch[1])}</div>
            </div>
          );
        }

        // Regular paragraph / line
        return <p key={idx}>{renderInline(line)}</p>;
      })}
    </div>
  );
};
