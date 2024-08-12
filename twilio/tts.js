const { ElevenLabsClient, ElevenLabs } = require('elevenlabs');
const dotenv = require("dotenv");
const { createWriteStream } = require("fs");
const { v4: uuid } = require("uuid");

dotenv.config();

const ELEVENLABS_API_KEY = process.env.ELEVENLABS_API_KEY;
const baseURL = process.env.SERVER_DOMAIN;

if (!ELEVENLABS_API_KEY) {
  throw new Error("Missing ELEVENLABS_API_KEY in environment variables");
}

const client = new ElevenLabsClient({
  apiKey: ELEVENLABS_API_KEY,
});

const createAudioStreamFromText = async (
  text
) => {
  const audioStream = await client.generate({
    voice: "u7bRcYbD7visSINTyAT8",
    model_id: "eleven_turbo_v2_5",
    text,
  });

  const chunks = [];
  for await (const chunk of audioStream) {
    chunks.push(chunk);
  }

  const content = Buffer.concat(chunks);
  return content;
};

export const createAudioFileFromText = async () => {
  return new Promise<string>(async (resolve, reject) => {
    try {
      const audio = await client.generate({
        voice: "Rachel",
        model_id: "eleven_turbo_v2_5",
        text,
      });
      const fileName = `${baseURL}/audio/${uuid()}.mp3`;
      const fileStream = createWriteStream(fileName);

      audio.pipe(fileStream);
      fileStream.on("finish", () => resolve(fileName)); // Resolve with the fileName
      fileStream.on("error", reject);
    } catch (error) {
      reject(error);
    }
  });
};

module.exports = { createAudioStreamFromText, createAudioFileFromText };