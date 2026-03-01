import React from 'react';
import ScenePanel from './ScenePanel.jsx';
import StoryPanel from './StoryPanel.jsx';
import ActionBar from './ActionBar.jsx';
import DeathOverlay from './DeathOverlay.jsx';
import CompassPanel from './CompassPanel.jsx';
import InventoryPanel from './InventoryPanel.jsx';

const topGridStyle = {
  display: 'grid',
  gridTemplateColumns: '3fr 1fr',
  gap: '1rem',
  marginBottom: '1rem',
};

const toggleStyle = {
  display: 'flex',
  alignItems: 'center',
  gap: '0.4rem',
  fontSize: '0.75rem',
  color: 'var(--text-muted)',
  marginTop: '0.5rem',
  cursor: 'pointer',
  userSelect: 'none',
};

export default function GameLayout({ game }) {
  const {
    game: g,
    messages,
    gameOver,
    doLook,
    doMove,
    doAction,
    doRestart,
    doHelp,
    roomImages,
    aiImagesEnabled,
    imageLoading,
    toggleAiImages,
    currentRoomId,
    deathCause,
  } = game;

  return (
    <div>
      {/* TOP TIER: Scene + Actions (left) | Compass + Inventory (right) */}
      <div style={topGridStyle}>
        <div>
          <ScenePanel
            roomName={g.room.name}
            roomId={currentRoomId}
            imageSrc={roomImages[currentRoomId] || null}
            imageLoading={imageLoading}
            deathCause={deathCause}
          />
          {gameOver ? (
            <DeathOverlay onRestart={doRestart} />
          ) : (
            <ActionBar game={g} onLook={doLook} onAction={doAction} onHelp={doHelp} />
          )}
        </div>
        <div>
          {!gameOver && (
            <>
              <CompassPanel game={g} onMove={doMove} />
              <InventoryPanel items={g.inventory} />
              <label style={toggleStyle}>
                <input
                  type="checkbox"
                  checked={aiImagesEnabled}
                  onChange={toggleAiImages}
                />
                AI Images (experimental)
              </label>
            </>
          )}
        </div>
      </div>

      {/* BOTTOM TIER: Terminal (full width) */}
      <StoryPanel messages={messages} />
    </div>
  );
}
