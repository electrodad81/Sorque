import { useState, useEffect, useCallback, useRef } from 'react';
import { newGameFromUrl } from '../engine/index.js';
import { DEATH_TEXT } from '../constants.js';
import { generateRoomImage } from '../services/imageGen.js';

export function useGame(worldUrl) {
  const gameRef = useRef(null);
  const [messages, setMessages] = useState([]);
  const [tick, setTick] = useState(0);
  const [gameOver, setGameOver] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // AI image generation state
  const [roomImages, setRoomImages] = useState({});
  const [aiImagesEnabled, setAiImagesEnabled] = useState(false);
  const [imageLoading, setImageLoading] = useState(false);
  const generatingRef = useRef(new Set());

  useEffect(() => {
    let cancelled = false;
    newGameFromUrl(worldUrl)
      .then(g => {
        if (cancelled) return;
        gameRef.current = g;
        setMessages([{ text: g.descShort(), kind: 'body' }]);
        setLoading(false);
      })
      .catch(e => {
        if (cancelled) return;
        setError(e.message);
        setLoading(false);
      });
    return () => { cancelled = true; };
  }, [worldUrl]);

  const bump = useCallback(() => setTick(t => t + 1), []);

  const append = useCallback((text, kind = 'body') => {
    setMessages(prev => [...prev, { text, kind }]);
  }, []);

  // Trigger AI image generation for the current room
  const maybeGenerateImage = useCallback((roomId, description) => {
    if (!aiImagesEnabled) return;
    if (roomImages[roomId]) return;
    if (generatingRef.current.has(roomId)) return;

    generatingRef.current.add(roomId);
    setImageLoading(true);

    generateRoomImage(roomId, description)
      .then(url => {
        setRoomImages(prev => ({ ...prev, [roomId]: url }));
      })
      .catch(err => {
        console.error(`Failed to generate image for room ${roomId}:`, err);
      })
      .finally(() => {
        generatingRef.current.delete(roomId);
        setImageLoading(false);
      });
  }, [aiImagesEnabled, roomImages]);

  // Generate image when AI mode is toggled on for the current room
  useEffect(() => {
    const g = gameRef.current;
    if (!g || !aiImagesEnabled) return;
    maybeGenerateImage(g.currentRoomId, g.room.descLong);
  }, [aiImagesEnabled, maybeGenerateImage]);

  const doLook = useCallback(() => {
    const g = gameRef.current;
    if (!g || gameOver) return;
    g.look();
    append(g.descLong(), 'body');
    bump();
  }, [gameOver, append, bump]);

  const doMove = useCallback((direction) => {
    const g = gameRef.current;
    if (!g || gameOver) return;

    const compassEntry = g.compass().find(e => e.direction === direction);

    // Check lock before moving
    if (compassEntry && compassEntry.locked) {
      append(compassEntry.lockedText, 'warning');
      bump();
      return;
    }

    const beforeInv = new Set(g.inventory);
    g.move(direction);

    if (g.room.name) {
      append(g.room.name, 'room');
    }
    append(g.descShort(), 'body');

    // Check for item-gated exits where player had the item
    const exit = g.rooms[g.currentRoomId] ? null : null; // already moved
    // Detect new items
    for (const item of g.inventory) {
      if (!beforeInv.has(item)) {
        append(`**${item.charAt(0).toUpperCase() + item.slice(1)} added to inventory.**`, 'success');
      }
    }

    if (g.dead) {
      const cause = g.deathCause || 'generic';
      const msg = g.deathMessage || DEATH_TEXT[cause] || DEATH_TEXT.generic;
      append(msg, 'error');
      setGameOver(true);
    }

    // Try generating an image for the new room
    maybeGenerateImage(g.currentRoomId, g.room.descLong);

    bump();
  }, [gameOver, append, bump, maybeGenerateImage]);

  const doAction = useCallback((interactionId) => {
    const g = gameRef.current;
    if (!g || gameOver) return;

    const beforeInv = new Set(g.inventory);
    const { message, dead } = g.do(interactionId);

    if (dead || g.dead) {
      const cause = g.deathCause || 'generic';
      const msg = g.deathMessage || message || DEATH_TEXT[cause] || DEATH_TEXT.generic;
      append(msg, 'error');
      setGameOver(true);
      bump();
      return;
    }

    // Refresh description (overrides may have changed)
    append(g.descLong(), 'body');

    // Inventory pickups
    for (const item of [...g.inventory].sort()) {
      if (!beforeInv.has(item)) {
        append(`**${item.charAt(0).toUpperCase() + item.slice(1)} added to inventory.**`, 'success');
      }
    }

    // Authored text last (shows at top in newest-first panel)
    if (message) {
      append(message, 'info');
    }

    bump();
  }, [gameOver, append, bump]);

  const doRestart = useCallback(() => {
    const g = gameRef.current;
    if (!g) return;
    g.restart();
    setMessages([{ text: g.descShort(), kind: 'body' }]);
    setGameOver(false);
    bump();
  }, [bump]);

  const doHelp = useCallback((helpText) => {
    append(helpText, 'info');
    bump();
  }, [append, bump]);

  const toggleAiImages = useCallback(() => {
    setAiImagesEnabled(prev => !prev);
  }, []);

  const g = gameRef.current;

  return {
    loading,
    error,
    tick,
    messages,
    gameOver,
    game: g,
    doLook,
    doMove,
    doAction,
    doRestart,
    doHelp,
    // Image-related
    roomImages,
    aiImagesEnabled,
    imageLoading,
    toggleAiImages,
    currentRoomId: g ? g.currentRoomId : null,
    deathCause: g && g.dead ? (g.deathCause || 'generic') : null,
  };
}
