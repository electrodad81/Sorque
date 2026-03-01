import React, { useState } from 'react';

const boxStyle = {
  height: '260px',
  border: '1px solid #333',
  padding: '12px',
  overflowY: 'auto',
  background: 'transparent',
  boxSizing: 'border-box',
  color: 'var(--text)',
};

const ruleStyle = {
  border: 'none',
  height: '1px',
  margin: '8px 0 0',
  background: 'linear-gradient(to right, rgba(255,255,255,0.06), rgba(255,255,255,0.22), rgba(255,255,255,0.06))',
};

export default function InventoryPanel({ items }) {
  const [open, setOpen] = useState(true);
  const sorted = [...items].sort();

  return (
    <div>
      <hr style={ruleStyle} />
      <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', margin: '8px 0' }}>
        <input type="checkbox" checked={open} onChange={() => setOpen(o => !o)} />
        Inventory
      </label>
      {open && (
        <div style={boxStyle}>
          {sorted.length === 0 ? (
            <em>Inventory is empty.</em>
          ) : (
            <ul>
              {sorted.map(item => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
