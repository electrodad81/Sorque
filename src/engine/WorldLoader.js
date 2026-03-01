import { Exit } from './Exit.js';
import { Interaction } from './Interaction.js';
import { DescOverride } from './DescOverride.js';
import { Room } from './Room.js';
import { Game } from './Game.js';

function toSet(v) {
  if (!v) return new Set();
  if (Array.isArray(v)) return new Set(v.map(String));
  return new Set([String(v)]);
}

function toInteractions(rawList) {
  return (rawList || []).map(d => new Interaction({
    id: String(d.id),
    label: String(d.label || 'Interact'),
    text: d.text || null,
    once: Boolean(d.once),
    visibleIfFlags: toSet(d.visible_if_flags),
    visibleIfNotFlags: toSet(d.visible_if_not_flags),
    visibleIfItems: toSet(d.visible_if_items),
    visibleIfNotItems: toSet(d.visible_if_not_items),
    effects: Array.isArray(d.effects) ? d.effects : [],
    sort: Number(d.sort || 0),
  }));
}

function toOverrides(rawList) {
  return (rawList || []).map(ov => new DescOverride({
    short: ov.short || null,
    long: ov.long || null,
    visibleIfFlags: toSet(ov.visible_if_flags),
    visibleIfNotFlags: toSet(ov.visible_if_not_flags),
    visibleIfItems: toSet(ov.visible_if_items),
    visibleIfNotItems: toSet(ov.visible_if_not_items),
    priority: Number(ov.priority || 0),
  }));
}

export function loadRooms(world) {
  const rooms = {};
  const rawRooms = world.rooms || {};

  for (const [rid, rdata] of Object.entries(rawRooms)) {
    const exits = {};
    for (const [direction, edata] of Object.entries(rdata.exits || {})) {
      exits[direction] = new Exit({
        direction,
        toRoom: String(edata.to),
        lockedByItem: edata.locked_by_item || null,
        lockedByFlag: edata.locked_by_flag || null,
        lockedText: edata.locked_text || null,
        label: edata.label || null,
      });
    }

    rooms[rdata.id || rid] = new Room({
      id: String(rdata.id || rid),
      name: rdata.name || null,
      descShort: rdata.desc_short || '',
      descLong: rdata.desc_long || '',
      exits,
      interactions: toInteractions(rdata.interactions),
      onLookAddFlags: toSet(rdata.on_look_add_flags),
      descOverrides: toOverrides(rdata.desc_overrides),
    });
  }

  return rooms;
}

function resolveStartRoom(world, rooms) {
  const candidates = [
    world.start_room,
    world.start,
    world.startRoom,
    (world.meta || {}).start_room,
    (world.meta || {}).start_room_id,
  ];
  for (const c of candidates) {
    if (c != null && String(c) in rooms) return String(c);
  }
  const keys = Object.keys(rooms);
  if (keys.length > 0) return keys[0];
  throw new Error('World JSON has no rooms; cannot determine start_room.');
}

export async function newGameFromUrl(url) {
  const resp = await fetch(url);
  if (!resp.ok) throw new Error(`Failed to load world: ${resp.status}`);
  const world = await resp.json();
  return newGameFromData(world);
}

export function newGameFromData(world) {
  const rooms = loadRooms(world);
  const start = resolveStartRoom(world, rooms);
  const globalInteractions = toInteractions(world.global_interactions);
  return new Game(rooms, start, globalInteractions);
}
