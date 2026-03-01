export class Interaction {
  constructor({
    id,
    label,
    text = null,
    once = false,
    visibleIfFlags = new Set(),
    visibleIfNotFlags = new Set(),
    visibleIfItems = new Set(),
    visibleIfNotItems = new Set(),
    effects = [],
    sort = 0,
  }) {
    this.id = id;
    this.label = label;
    this.text = text;
    this.once = once;
    this.visibleIfFlags = visibleIfFlags instanceof Set ? visibleIfFlags : new Set(visibleIfFlags);
    this.visibleIfNotFlags = visibleIfNotFlags instanceof Set ? visibleIfNotFlags : new Set(visibleIfNotFlags);
    this.visibleIfItems = visibleIfItems instanceof Set ? visibleIfItems : new Set(visibleIfItems);
    this.visibleIfNotItems = visibleIfNotItems instanceof Set ? visibleIfNotItems : new Set(visibleIfNotItems);
    this.effects = effects;
    this.sort = sort;
  }

  _doneFlag() {
    return `done:${this.id}`;
  }

  isVisible(game) {
    if (this.once && game.flags.has(this._doneFlag())) return false;
    for (const f of this.visibleIfFlags) { if (!game.flags.has(f)) return false; }
    for (const f of this.visibleIfNotFlags) { if (game.flags.has(f)) return false; }
    for (const i of this.visibleIfItems) { if (!game.inventory.has(i)) return false; }
    for (const i of this.visibleIfNotItems) { if (game.inventory.has(i)) return false; }
    return true;
  }

  perform(game) {
    const outLines = [];
    if (this.text) outLines.push(this.text);
    let dead = false;

    for (const eff of this.effects) {
      if ('add_flag' in eff) game.flags.add(eff.add_flag);
      if ('remove_flag' in eff) game.flags.delete(eff.remove_flag);
      if ('add_item' in eff) game.inventory.add(eff.add_item);
      if ('remove_item' in eff) game.inventory.delete(eff.remove_item);
      if ('set_room' in eff) {
        const target = eff.set_room;
        if (target in game.rooms) game.currentRoomId = target;
      }
      if ('kill_player' in eff) {
        const payload = eff.kill_player;
        let cause = eff.cause || 'generic';
        let msg = eff.message || eff.msg || null;

        if (typeof payload === 'boolean') {
          if (!payload) continue;
        } else if (typeof payload === 'string') {
          cause = payload || cause;
        } else if (typeof payload === 'object' && payload !== null) {
          cause = payload.cause || cause;
          msg = msg || payload.message || payload.msg || payload.text || null;
        }

        dead = true;
        game.dead = true;
        game.deathCause = cause;
        if (msg) {
          game.deathMessage = msg;
          outLines.push(msg);
        }
      }
    }

    if (this.once) game.flags.add(this._doneFlag());
    return { message: outLines.join('\n').trim(), dead };
  }
}
