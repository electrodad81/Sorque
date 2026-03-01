import React from 'react';
import { INSTRUCTIONS_MD } from '../constants.js';
import '../styles/ActionBar.css';

export default function ActionBar({ game, onLook, onAction, onHelp }) {
  const vis = game.visibleInteractions();
  const helpAvailable = game.flags.has('read_note');

  return (
    <div className="action-bar">
      <div className="panel-subhed">Actions you can take:</div>
      <hr className="panel-rule" />
      <div className="action-grid">
        <button className="action-btn action-btn--look" onClick={onLook}>
          Look
        </button>
        {vis.map(it => (
          <button
            key={it.id}
            className="action-btn"
            onClick={() => onAction(it.id)}
          >
            {it.label}
          </button>
        ))}
        <button
          className="action-btn action-btn--help"
          disabled={!helpAvailable}
          onClick={() => helpAvailable && onHelp(INSTRUCTIONS_MD)}
          style={!helpAvailable ? {} : {}}
        >
          Help
        </button>
      </div>
    </div>
  );
}
