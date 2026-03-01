export const COMPASS_ORDER = [
  'north', 'northeast', 'east', 'southeast',
  'south', 'southwest', 'west', 'northwest',
  'up', 'down', 'in', 'out',
];

export const COLOR_MAP = {
  body: 'inherit',
  success: '#15FF00',
  info: '#00FFEA',
  warning: '#FF0015',
  error: '#EE4B2B',
};

export const INSTRUCTIONS_MD =
  '**Welcome to Sorque**\n' +
  '- Click **Look** to reveal more detail in a room.\n' +
  '- Use the **compass** to move.\n' +
  '- **Actions** appear contextually under the room panel.\n' +
  '- Jammed doors may need items (try the **hatchet**).\n' +
  '- In the basement, **petting the dog will kill you**.\n' +
  '- The **hatchet** can be found outside.\n' +
  '- Step **outside** to escape.\n\n' +
  'Good luck.';

export const DEATH_TEXT = {
  dog: "The dog erupts from the dark, all heat and teeth. You don't get back up.",
  fall: "Your foot finds nothing. You fall, and fall, and don't stop in time.",
  trap: 'Metal snaps shut around you with terrible finality. You don\'t make it out.',
  thorns: 'You force into the hedge. Thorns drink deep; you never find your way through.',
  poison: 'Your veins burn, breath goes heavy, and the world narrows to a pinprick.',
  generic: 'You collapse. Darkness takes you.',
};
