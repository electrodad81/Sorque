import React from 'react';

const overlayStyle = {
  marginTop: '16px',
  textAlign: 'center',
};

const restartBtn = {
  width: '100%',
  minHeight: '60px',
  padding: '10px 14px',
  borderRadius: '8px',
  border: '2px solid var(--accent-blue)',
  background: 'transparent',
  color: 'var(--accent-blue)',
  fontSize: '1rem',
  cursor: 'pointer',
  fontFamily: 'inherit',
};

export default function DeathOverlay({ onRestart }) {
  return (
    <div style={overlayStyle}>
      <hr style={{
        border: 'none',
        height: '1px',
        margin: '8px 0 16px',
        background: 'linear-gradient(to right, rgba(255,255,255,0.06), rgba(255,255,255,0.22), rgba(255,255,255,0.06))',
      }} />
      <button style={restartBtn} onClick={onRestart}>
        Play again
      </button>
    </div>
  );
}
