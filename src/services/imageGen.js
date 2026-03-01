export async function generateRoomImage(roomId, description) {
  const res = await fetch('/api/generate-image', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ roomId, description }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Image generation failed: ${text}`);
  }

  const { url } = await res.json();
  return url;
}
