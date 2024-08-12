const express = require('express');
const bodyParser = require('body-parser');
const { OpenAI } = require('openai');
const fs = require('fs');
const path = require('path');
const Twilio = require('twilio');
const { createAudioStreamFromText,createAudioFileFromText } = require('./new.js');
const dotenv = require('dotenv');
dotenv.config();

const app = express();
app.use(bodyParser.urlencoded({ extended: false }));

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

const model = 'gpt-4o-mini-2024-07-18';
const systemMessage = {
  role: 'system',
  content: "You are John, a customer care representative. You give helpful and polite answers to the user's questions. You never reveal that you are an AI. Keep the answers brief and to the point, and respond naturally as a human would.",
};

let conversationHistory = [systemMessage];

conversationHistory.push({
  role: 'assistant',
  content: 'Hello! I am John, at your service. How can I assist you today?',
});

// Set the base URL to your ngrok URL
const baseURL = process.env.SERVER_DOMAIN

let port = process.env.PORT || 3000;

// Function to query OpenAI with the user's input
async function queryOpenAI(userInput) {
  try {
    // Add user's message to the conversation history
    conversationHistory.push({
      role: 'user',
      content: userInput,
    });

    // Query the OpenAI API
    const response = await openai.chat.completions.create({
      model: model,
      messages: conversationHistory,
    });

    // Get the assistant's response
    const assistantResponse = response.choices[0].message.content;

    // Add the assistant's message to the conversation history
    conversationHistory.push({
      role: 'assistant',
      content: assistantResponse,
    });

    console.log('Assistant response:', assistantResponse);
    return assistantResponse;
  } catch (error) {
    console.error('Error querying OpenAI:', error);
    return "I'm sorry, I couldn't understand that. Could you try asking in a different way?";
  }
}

// Serve static files from the "public" directory
app.use('/audio', express.static(path.join(__dirname, 'public')));

// Initial greeting endpoint
app.post('/voice/greeting', (req, res) => {
  const twiml = new Twilio.twiml.VoiceResponse();
  
  // Play the pre-generated greeting
  twiml.play({ url: `${baseURL}/audio/greeting.mp3` });

  // Gather user input after greeting
  const gather = twiml.gather({
    input: 'speech',
    speechTimeout: 'auto',
    action: '/voice',
  });

  res.writeHead(200, { 'Content-Type': 'text/xml' });
  res.end(twiml.toString());
});

app.post('/voice', async (req, res) => {
  const twiml = new Twilio.twiml.VoiceResponse();
  const speechResult = req.body.SpeechResult;

  console.log('Received SpeechResult:', speechResult);

  // const publicDir = path.resolve(__dirname, 'public');
  // const speechFile = path.join(publicDir, 'output.mp3');
  // await fs.promises.mkdir(publicDir, { recursive: true });

  if (speechResult) {
    try {
      // Check if the user wants to end the conversation
      if (speechResult.toLowerCase().includes('bye')) {
        twiml.play({ url: `${baseURL}/audio/greeting2.mp3` });
        twiml.hangup();
      } else {
        // Process the speech result with OpenAI
        const openAIResponse = await queryOpenAI(speechResult);
        
        // const content = await createAudioStreamFromText(openAIResponse);
        // await fs.promises.writeFile(speechFile, content);
        // console.log('Audio content written to file: output.mp3');

        // Create an audio file from the OpenAI response
        const fileName = await createAudioFileFromText(openAIResponse);
        console.log('Audio file created:', fileName);

        // Play the TTS audio file
        const audioUrl = `${baseURL}/audio/${fileName}`;
        console.log('Playing audio from URL:', audioUrl);
        twiml.play(audioUrl);

        // Gather for the next user input
        const gather = twiml.gather({
          input: 'speech',
          speechTimeout: 'auto',
          action: '/voice',
        });
        gather.say({ voice: 'alice' }, ''); // Keeping gather active for next input
      }
    } catch (error) {
      console.error('Error processing request:', error);
      twiml.say({ voice: 'alice' }, 'We encountered an error processing your request. Please try again. ');
      const gather = twiml.gather({
        input: 'speech',
        speechTimeout: 'auto',
        action: '/voice',
      });
      gather.say({ voice: 'alice' }, ''); // Keeping gather active for retry
    }
  } else {

    console.log('No SpeechResult received');
    // Prompt the user to ask another question or end the conversation
    const gather = twiml.gather({
      input: 'speech',
      speechTimeout: 'auto',
      timeout:15,
      action: '/voice',
    });
    gather.say({ voice: 'alice' }, '');
  }

  res.writeHead(200, { 'Content-Type': 'text/xml' });
  res.end(twiml.toString());
});

// Start the server
app.listen(port, () => {
  console.log(`App listening at http://localhost:${port}`);
});