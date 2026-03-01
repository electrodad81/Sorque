import React from 'react';
import '../styles/CompassPanel.css';

function prettifyExit(label) {
  let t = label.trim();
  const tl = t.toLowerCase();
  if (tl.startsWith('to the ')) t = t.slice(7);
  else if (tl.startsWith('to ')) t = t.slice(3);
  return t.charAt(0).toUpperCase() + t.slice(1);
}

export default function CompassPanel({ game, onMove }) {
  const moves = game.compass();
  if (!moves.length) return null;

  return (
    <div className="compass-panel">
      <div className="panel-subhed">Directions you can go</div>
      <hr className="panel-rule" />
      {moves.map(ex => {
        const toValid = Boolean(ex.to) && ex.to in game.rooms;
        return (
          <button
            key={ex.direction}
            className="compass-btn"
            disabled={!toValid}
            onClick={() => onMove(ex.direction)}
          >
            {prettifyExit(ex.label)}
          </button>
        );
      })}
    </div>
  );
}
