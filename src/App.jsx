import React from 'react';
import { useGame } from './hooks/useGame.js';
import GameLayout from './components/GameLayout.jsx';

export default function App() {
  const game = useGame('/worlds/escape_house_01.json');

  if (game.loading) {
    return <div style={{ padding: '2rem', color: 'var(--text-muted)' }}>Loading world...</div>;
  }
  if (game.error) {
    return <div style={{ padding: '2rem', color: 'var(--color-error)' }}>Failed to load world: {game.error}</div>;
  }

  return <GameLayout game={game} />;
}
