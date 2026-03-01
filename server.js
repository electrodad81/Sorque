import 'dotenv/config';
import express from 'express';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import OpenAI from 'openai';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PORT = process.env.PORT || 3001;

const STYLE_PREFIX =
  '1-bit black and white pixel art, high contrast, dithered, classic Macintosh adventure game style, no text:';

const app = express();
app.use(express.json());

// Serve built frontend
app.use(express.static(join(__dirname, 'dist')));

// Image generation API
app.post('/api/generate-image', async (req, res) => {
  const { roomId, description } = req.body;
  if (!roomId || !description) {
    return res.status(400).json({ error: 'roomId and description required' });
  }

  if (!process.env.OPENAI_API_KEY) {
    return res.status(500).json({ error: 'OPENAI_API_KEY not configured' });
  }

  try {
    const openai = new OpenAI();
    const prompt = `${STYLE_PREFIX} ${description}`;

    const response = await openai.images.generate({
      model: 'dall-e-3',
      prompt,
      n: 1,
      size: '1024x1024',
      quality: 'standard',
      response_format: 'url',
    });

    res.json({ url: response.data[0].url });
  } catch (err) {
    console.error('Image generation error:', err.message);
    res.status(500).json({ error: err.message });
  }
});

// SPA fallback
app.get('*', (req, res) => {
  res.sendFile(join(__dirname, 'dist', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Server listening on http://localhost:${PORT}`);
});
