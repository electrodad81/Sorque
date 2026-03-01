import React, { useRef, useEffect } from 'react';
import '../styles/StoryPanel.css';

const FADE_SPAN = 16;
const FADE_MIN = 0.05;

function mdMin(s) {
  // Escape HTML
  s = s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  // **bold**
  s = s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  // __bold__
  s = s.replace(/__(.+?)__/g, '<strong>$1</strong>');
  // *italic* (not inside **)
  s = s.replace(/(?<!\*)\*(.+?)\*(?!\*)/g, '<em>$1</em>');
  // _italic_
  s = s.replace(/_(.+?)_/g, '<em>$1</em>');
  // line breaks
  s = s.replace(/\n/g, '<br/>');
  return s;
}

export default function StoryPanel({ messages }) {
  const panelRef = useRef(null);

  // New text appears at the bottom — auto-scroll down
  useEffect(() => {
    if (panelRef.current) {
      panelRef.current.scrollTop = panelRef.current.scrollHeight;
    }
  }, [messages]);

  // Render in natural order; fade oldest (top) toward transparent
  const len = messages.length;

  return (
    <div className="story-panel" ref={panelRef}>
      {messages.map((msg, idx) => {
        const kind = msg.kind || 'body';
        // age = distance from the end (newest = 0)
        const age = len - 1 - idx;
        const t = Math.min(age / FADE_SPAN, 1.0);
        const opacity = (1.0 - t) * (1.0 - FADE_MIN) + FADE_MIN;

        return (
          <div
            key={idx}
            className={`story-block story-block--${kind}`}
            style={{ opacity }}
            dangerouslySetInnerHTML={{ __html: mdMin(msg.text) }}
          />
        );
      })}
    </div>
  );
}
