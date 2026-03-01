import React, { useState } from 'react';

const panelStyle = {
  aspectRatio: '4 / 3',
  background: 'var(--bg-panel)',
  border: '1px solid var(--border)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  overflow: 'hidden',
  position: 'relative',
};

const roomNameStyle = {
  fontFamily: 'var(--font-heading)',
  fontSize: '2.4rem',
  fontWeight: 700,
  color: 'var(--text-muted)',
  letterSpacing: '0.04em',
  textAlign: 'center',
  padding: '1rem',
};

const loadingStyle = {
  position: 'absolute',
  bottom: '0.5rem',
  right: '0.5rem',
  fontSize: '0.75rem',
  color: 'var(--text-muted)',
  background: 'rgba(0,0,0,0.5)',
  padding: '0.25rem 0.5rem',
  borderRadius: '3px',
};

export default function ScenePanel({ roomName, roomId, imageSrc, imageLoading, deathCause }) {
  const [staticFailed, setStaticFailed] = useState(false);
  const [deathFailed, setDeathFailed] = useState(false);
  const [staticKey, setStaticKey] = useState(roomId);
  const [deathKey, setDeathKey] = useState(deathCause);

  // Reset static image error state when room changes
  if (roomId !== staticKey) {
    setStaticFailed(false);
    setStaticKey(roomId);
  }

  // Reset death image error state when death cause changes
  if (deathCause !== deathKey) {
    setDeathFailed(false);
    setDeathKey(deathCause);
  }

  // Death image takes priority when the player is dead
  const deathSrc = deathCause ? `/images/deaths/${deathCause}.png` : null;
  const showDeath = deathSrc && !deathFailed;

  const staticSrc = roomId ? `/images/rooms/${roomId}.png` : null;
  const showStatic = !showDeath && staticSrc && !staticFailed;
  const showGenerated = !showDeath && !showStatic && imageSrc;

  return (
    <div style={panelStyle}>
      {showDeath ? (
        <img
          src={deathSrc}
          alt="Death"
          style={{ width: '100%', height: '100%', objectFit: 'cover' }}
          onError={() => setDeathFailed(true)}
        />
      ) : showStatic ? (
        <img
          src={staticSrc}
          alt={roomName || 'Scene'}
          style={{ width: '100%', height: '100%', objectFit: 'cover' }}
          onError={() => setStaticFailed(true)}
        />
      ) : showGenerated ? (
        <img
          src={imageSrc}
          alt={roomName || 'Scene'}
          style={{ width: '100%', height: '100%', objectFit: 'cover' }}
        />
      ) : (
        <div style={roomNameStyle}>{roomName || ''}</div>
      )}
      {imageLoading && <div style={loadingStyle}>Generating image...</div>}
    </div>
  );
}
