import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

function imageApiPlugin() {
  return {
    name: 'image-api',
    configureServer(server) {
      server.middlewares.use('/api/generate-image', async (req, res) => {
        if (req.method !== 'POST') {
          res.statusCode = 405;
          res.end('Method not allowed');
          return;
        }

        let body = '';
        for await (const chunk of req) body += chunk;
        const { roomId, description } = JSON.parse(body);

        if (!roomId || !description) {
          res.statusCode = 400;
          res.end(JSON.stringify({ error: 'roomId and description required' }));
          return;
        }

        const apiKey = process.env.OPENAI_API_KEY;
        if (!apiKey) {
          res.statusCode = 500;
          res.end(JSON.stringify({ error: 'OPENAI_API_KEY not configured' }));
          return;
        }

        try {
          // Dynamic import so openai isn't bundled into the client
          const { default: OpenAI } = await import('openai');
          const openai = new OpenAI({ apiKey });

          const STYLE_PREFIX =
            '1-bit black and white pixel art, high contrast, dithered, classic Macintosh adventure game style, no text:';

          const response = await openai.images.generate({
            model: 'dall-e-3',
            prompt: `${STYLE_PREFIX} ${description}`,
            n: 1,
            size: '1024x1024',
            quality: 'standard',
            response_format: 'url',
          });

          res.setHeader('Content-Type', 'application/json');
          res.end(JSON.stringify({ url: response.data[0].url }));
        } catch (err) {
          console.error('Image generation error:', err.message);
          res.statusCode = 500;
          res.end(JSON.stringify({ error: err.message }));
        }
      });
    },
  };
}

export default defineConfig({
  plugins: [react(), imageApiPlugin()],
  test: {
    environment: 'node',
  },
});
