const COMPASS_ORDER = [
  'north', 'northeast', 'east', 'southeast',
  'south', 'southwest', 'west', 'northwest',
  'up', 'down', 'in', 'out',
];

export class Game {
  constructor(rooms, startRoomId, globalInteractions = []) {
    if (!(startRoomId in rooms)) {
      throw new Error(`start_room '${startRoomId}' not in rooms`);
    }
    this.rooms = rooms;
    this.startRoomId = startRoomId;
    this.currentRoomId = startRoomId;
    this.flags = new Set();
    this.inventory = new Set();
    this.dead = false;
    this.lastMessage = '';
    this.deathCause = 'generic';
    this.deathMessage = '';
    this.globalInteractions = [...globalInteractions];
  }

  get room() {
    return this.rooms[this.currentRoomId];
  }

  compass() {
    const data = [];
    for (const [direction, ex] of Object.entries(this.room.exits)) {
      const locked = ex.isLocked(this.inventory, this.flags);
      data.push({
        direction,
        label: ex.displayLabel(),
        to: ex.toRoom,
        locked,
        lockedText: ex.lockedText || "It's stuck. You'll need something to pry it open.",
      });
    }
    const orderMap = {};
    COMPASS_ORDER.forEach((k, i) => { orderMap[k] = i; });
    data.sort((a, b) => (orderMap[a.direction] ?? 999) - (orderMap[b.direction] ?? 999));
    return data;
  }

  visibleInteractions() {
    const vis = this.room.interactions.filter(it => it.isVisible(this));
    const globalVis = this.globalInteractions.filter(it => it.isVisible(this));
    const all = [...vis, ...globalVis];
    all.sort((a, b) => {
      if (a.sort !== b.sort) return a.sort - b.sort;
      return a.label.localeCompare(b.label);
    });
    return all;
  }

  look() {
    for (const f of this.room.onLookAddFlags) {
      this.flags.add(f);
    }
    this.lastMessage = this.descLong();
    return this.lastMessage;
  }

  move(direction) {
    const ex = this.room.exits[direction];
    if (!ex) {
      this.lastMessage = "You can't go that way.";
      return this.lastMessage;
    }
    if (ex.isLocked(this.inventory, this.flags)) {
      this.lastMessage = ex.lockedText || "It's stuck. You can't force it.";
      return this.lastMessage;
    }
    this.currentRoomId = ex.toRoom;
    this.lastMessage = this.descShort();
    return this.lastMessage;
  }

  do(interactionId) {
    let it = this.room.interactions.find(i => i.id === interactionId) || null;
    if (!it) {
      it = this.globalInteractions.find(i => i.id === interactionId) || null;
    }
    if (!it || !it.isVisible(this)) {
      this.lastMessage = 'Nothing happens.';
      return { message: this.lastMessage, dead: false };
    }

    const { message, dead } = it.perform(this);
    this.dead = dead;
    const msg = message || this.descShort();
    this.lastMessage = msg;
    return { message: msg, dead };
  }

  restart() {
    this.currentRoomId = this.startRoomId;
    this.flags.clear();
    this.inventory.clear();
    this.dead = false;
    this.lastMessage = this.room.descShort;
    this.deathCause = 'generic';
    this.deathMessage = '';
  }

  toDict() {
    return {
      startRoomId: this.startRoomId,
      currentRoomId: this.currentRoomId,
      flags: [...this.flags].sort(),
      inventory: [...this.inventory].sort(),
      dead: this.dead,
    };
  }

  loadDict(data) {
    this.currentRoomId = data.currentRoomId || this.startRoomId;
    this.flags = new Set(data.flags || []);
    this.inventory = new Set(data.inventory || []);
    this.dead = Boolean(data.dead);
  }

  descShort() {
    return this.room.renderDesc(this, false);
  }

  descLong() {
    return this.room.renderDesc(this, true);
  }
}
