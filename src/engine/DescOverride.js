export class DescOverride {
  constructor({
    short = null,
    long = null,
    visibleIfFlags = new Set(),
    visibleIfNotFlags = new Set(),
    visibleIfItems = new Set(),
    visibleIfNotItems = new Set(),
    priority = 0,
  } = {}) {
    this.short = short;
    this.long = long;
    this.visibleIfFlags = visibleIfFlags instanceof Set ? visibleIfFlags : new Set(visibleIfFlags);
    this.visibleIfNotFlags = visibleIfNotFlags instanceof Set ? visibleIfNotFlags : new Set(visibleIfNotFlags);
    this.visibleIfItems = visibleIfItems instanceof Set ? visibleIfItems : new Set(visibleIfItems);
    this.visibleIfNotItems = visibleIfNotItems instanceof Set ? visibleIfNotItems : new Set(visibleIfNotItems);
    this.priority = priority;
  }

  isVisible(game) {
    for (const f of this.visibleIfFlags) { if (!game.flags.has(f)) return false; }
    for (const f of this.visibleIfNotFlags) { if (game.flags.has(f)) return false; }
    for (const i of this.visibleIfItems) { if (!game.inventory.has(i)) return false; }
    for (const i of this.visibleIfNotItems) { if (game.inventory.has(i)) return false; }
    return true;
  }
}
