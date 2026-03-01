export class Room {
  constructor({
    id,
    name = null,
    descShort = '',
    descLong = '',
    exits = {},
    interactions = [],
    onLookAddFlags = new Set(),
    descOverrides = [],
  }) {
    this.id = id;
    this.name = name;
    this.descShort = descShort;
    this.descLong = descLong;
    this.exits = exits;
    this.interactions = interactions;
    this.onLookAddFlags = onLookAddFlags instanceof Set ? onLookAddFlags : new Set(onLookAddFlags);
    this.descOverrides = descOverrides;
  }

  renderDesc(game, long) {
    const candidates = [];

    for (const ov of this.descOverrides) {
      // must-pass gating
      if (ov.visibleIfFlags.size > 0 && !isSubset(ov.visibleIfFlags, game.flags)) continue;
      if (setsIntersect(ov.visibleIfNotFlags, game.flags)) continue;
      if (ov.visibleIfItems.size > 0 && !isSubset(ov.visibleIfItems, game.inventory)) continue;
      if (setsIntersect(ov.visibleIfNotItems, game.inventory)) continue;

      // specificity score
      let score = 0;
      score += 10 * (ov.visibleIfItems.size > 0 ? 1 : 0) + ov.visibleIfItems.size;
      score += 10 * (ov.visibleIfFlags.size > 0 ? 1 : 0) + ov.visibleIfFlags.size;
      score += 5 * (ov.visibleIfNotItems.size > 0 ? 1 : 0);
      score += 5 * (ov.visibleIfNotFlags.size > 0 ? 1 : 0);
      candidates.push({ priority: ov.priority, score, ov });
    }

    if (candidates.length > 0) {
      candidates.sort((a, b) => {
        if (b.priority !== a.priority) return b.priority - a.priority;
        return b.score - a.score;
      });
      const best = candidates[0].ov;
      return long ? (best.long || this.descLong) : (best.short || this.descShort);
    }

    return long ? this.descLong : this.descShort;
  }
}

function isSubset(setA, setB) {
  for (const item of setA) {
    if (!setB.has(item)) return false;
  }
  return true;
}

function setsIntersect(setA, setB) {
  for (const item of setA) {
    if (setB.has(item)) return true;
  }
  return false;
}
