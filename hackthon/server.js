import express from 'express';
import multer from 'multer';
import fs from 'fs';
import path from 'path';
import dotenv from 'dotenv';
import OpenAI from 'openai';

dotenv.config();

const app = express();
const upload = multer({ dest: 'uploads/' });
const port = process.env.PORT || 4000;
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

app.use(express.json());
app.use(express.static('public'));

app.post('/api/convert', upload.single('audio'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'Audio file is required.' });
    }

    const audioPath = path.resolve(req.file.path);
    const transcription = await openai.audio.transcriptions.create({
      file: fs.createReadStream(audioPath),
      model: 'gpt-4o-mini-transcribe'
    });

    const transcript = transcription.text;
    const prompt = `Convert the following transcript into a slide deck outline with up to 8 slides. Provide slide titles and bullet points:\n\n${transcript}`;

    const completion = await openai.responses.create({
      model: 'gpt-4.1-mini',
      input: prompt,
      max_output_tokens: 400
    });

    const slides = completion.output_text || completion.output?.[0]?.content?.[0]?.text || 'No slide content generated.';

    fs.unlinkSync(audioPath);

    res.json({ transcript, slides });
  } catch (error) {
    console.error('Conversion error:', error);
    res.status(500).json({ error: 'Failed to convert audio to slide deck.' });
  }
});

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.listen(port, () => {
  console.log(`Voice to Slide Deck server running on http://localhost:${port}`);
});
