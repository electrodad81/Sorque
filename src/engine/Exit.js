export class Exit {
  constructor({ direction, toRoom, lockedByItem = null, lockedByFlag = null, lockedText = null, label = null }) {
    this.direction = direction;
    this.toRoom = toRoom;
    this.lockedByItem = lockedByItem;
    this.lockedByFlag = lockedByFlag;
    this.lockedText = lockedText;
    this.label = label;
  }

  isLocked(inventory, flags) {
    if (this.lockedByItem && !inventory.has(this.lockedByItem)) return true;
    if (this.lockedByFlag && !flags.has(this.lockedByFlag)) return true;
    return false;
  }

  displayLabel() {
    return this.label || this.direction.charAt(0).toUpperCase() + this.direction.slice(1);
  }
}
