
# 🤖 JARVIS AI Assistant

A powerful, voice-activated AI assistant inspired by Iron Man's JARVIS. Built with Python, featuring wake word detection, Google Gemini AI integration, and comprehensive system control capabilities.


## ✨ Features
🎤 Voice Control

Wake Word Detection - Just say "Jarvis" to activate
Continuous Listening - Always ready to help
Offline Speech Recognition - Using Vosk (no internet required for commands)

🤖 AI Intelligence

Google Gemini Integration - Ask any question and get intelligent responses
Natural Conversations - Powered by advanced AI
Context Awareness - Understands follow-up questions

🌐 Web & Search

Open Websites - YouTube, Google, Gmail, Facebook, Twitter, Reddit, GitHub, and more
Google Search - Voice-activated web searches
Wikipedia Integration - Get quick summaries of any topic

🎵 Media Control

Music Player - Play random songs from your music folder
Volume Control - Increase, decrease, mute, or set specific volume levels
Smart Audio Management - Full system audio control

📁 File Management

Create Files - Voice command file creation
Create Folders - Organize with voice commands
Desktop Integration - Files saved directly to desktop

📰 Information & Updates

Latest News - Get top headlines on demand
Weather Reports - Current weather for any city
Time & Date - Quick access to current time and date

⏲️ Productivity

Reminders - Set voice-activated reminders
Timers - Quick countdown timers
System Information - Check CPU, memory, and battery status

📸 System Control

Screenshots - Capture screen on command
Application Launcher - Open Notepad, Calculator, Paint, and more
System Monitoring - Real-time performance metrics
## 🚀 Quick Start

Prerequisites

Python 3.11 or higher
Windows 10/11 (for Windows-specific features)
Microphone
Internet connection (for AI features)
## Installation
1- Clone the repository

git clone https://github.com/abdessamed01/jarvis-ai-assistant.git

2- Install dependencies

pip install -r requirements.txt

3- Download speech recognition model (first time only)

- Small model (40MB) - Downloads automatically on first run

4- Set up Google Gemini API (for AI conversations)

- Get free API key: Google AI Studio
- Set environment variable:
Windows CMD

     set GEMINI_API_KEY=your_api_key_here
     
PowerShell

     $env:GEMINI_API_KEY="your_api_key_here"
     
Or add to system environment variables permanently.

5- Run JARVIS

python jarvis.py
## 📖 Usage

Basic Commands
Time & Date:

"Jarvis, what time is it?"
"Jarvis, what's the date?"

Weather:

"Jarvis, what's the weather?"

Web Browsing:

"Jarvis, open YouTube"
"Jarvis, open Google"

Search:

"Jarvis, search Google for Python tutorials"
"Jarvis, Wikipedia artificial intelligence"

Music:

"Jarvis, play music"

Volume Control:

"Jarvis, increase volume"
"Jarvis, decrease volume"
"Jarvis, set volume to 50"
"Jarvis, mute"

File Management:

"Jarvis, create file report"
"Jarvis, create folder projects"

News:

"Jarvis, what's the latest news?"

System:

"Jarvis, take a screenshot"
"Jarvis, system information"
"Jarvis, open calculator"

Reminders:

"Jarvis, remind me in 5 minutes"
"Jarvis, set timer for 30 seconds"

AI Conversations:

"Jarvis, what is quantum physics?"
"Jarvis, explain machine learning"
"Jarvis, how do computers work?"

Exit:

"Jarvis, shutdown"
"Jarvis, goodbye"
##  ⚙️ Configuration

Optional Features
- Email Integration
Set these environment variables to enable email sending:

set JARVIS_EMAIL=your_email@gmail.com
set JARVIS_EMAIL_PASSWORD=your_app_password

- News API (Optional)

For detailed news, get a free API key from NewsAPI.org:

set NEWS_API_KEY=your_news_api_key
## 🎯 Tips for Better Recognition

Speaking Tips:

- Pause between "Jarvis" and your command:

- "Jarvis... what time is it"

- Speak clearly at a moderate pace

- Use simple, direct phrases

- Wait for confirmation before speaking again

- Environment Tips:

- Reduce background noise (TV, fans, music)

- Position microphone 6-12 inches from mouth

- Use a quiet room for best results

- Check microphone quality in Windows settings

For Best Accuracy:

- Download the larger speech model (1.8GB) for 10x 

better recognition:

- vosk-model-en-us-0.22.zip
##  📦 Dependencies

- vosk - Offline speech recognition

- sounddevice - Audio input

- google-generativeai - Google Gemini AI

- pyttsx3 - Text-to-speech (fallback)

- pywin32 - Windows TTS and system integration

- requests - HTTP requests

- wikipedia - Wikipedia API

- psutil - System information

- pyautogui - Screenshots

- pycaw - Volume control

- Pillow - Image processing
## 🛠️ Troubleshooting

"Microphone error" or "PyAudio not found"

- The assistant uses sounddevice which works with Python 3.14+

- Make sure your microphone is enabled in Windows settings

- Grant microphone permissions to Python

Speech recognition not working

- Download the larger model for better accuracy

- Reduce background noise

- Check microphone input levels in Windows

- Speak clearly and pause between wake word and command

Gemini API errors

- Verify your API key is set correctly

- Check internet connection

- Ensure you're using a valid Gemini API key from Google AI Studio

Volume control not working

- Install pycaw: pip install pycaw

- Run as administrator if issues persist
## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

- Fork the repository

- Create your feature branch (git checkout -b feature/

- AmazingFeature)

- Commit your changes (git commit -m 'Add some AmazingFeature')

- Push to the branch (git push origin feature/AmazingFeature)

- Open a Pull Request
## License



This project is licensed under the [MIT](https://choosealicense.com/licenses/mit/) License - see the LICENSE file for details.
## 🙏 Acknowledgments

- Inspired by JARVIS from Iron Man

- Built with Vosk for speech recognition

- Powered by Google Gemini AI

- Uses pycaw for volume control
## 📧 Contact

For questions or suggestions, please open an issue on GitHub.

## Made with ❤️
# by Abdessamed Yousfi

⭐ Star this repository if you find it helpful!

