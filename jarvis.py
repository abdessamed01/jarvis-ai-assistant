"""
JARVIS AI ASSISTANT - 
CREATED BY ABDESSAMED YOUSFI
"""

import datetime
import requests
import pyautogui
import sounddevice as sd
import queue
import json
import sys
import threading
import webbrowser
import os
import psutil
import time
from pathlib import Path
import random
import shutil
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER

# Use Windows native TTS
try:
    import win32com.client
except ImportError:
    print("Installing pywin32...")
    os.system("pip install pywin32")
    import win32com.client

try:
    from vosk import Model, KaldiRecognizer
except ImportError:
    print("Installing Vosk...")
    os.system("pip install vosk sounddevice")
    from vosk import Model, KaldiRecognizer

try:
    import wikipedia
except ImportError:
    print("Installing wikipedia...")
    os.system("pip install wikipedia")
    import wikipedia

try:
    import google.generativeai as genai
except ImportError:
    print("Installing Google Gemini...")
    os.system("pip install google-generativeai")
    import google.generativeai as genai

try:
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
except ImportError:
    pass

try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    VOLUME_CONTROL_AVAILABLE = True
except ImportError:
    print("Installing pycaw for volume control...")
    os.system("pip install pycaw")
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        VOLUME_CONTROL_AVAILABLE = True
    except:
        VOLUME_CONTROL_AVAILABLE = False

class JarvisAssistant:
    def __init__(self):
        self.audio_queue = queue.Queue()
        self.setup_voice()
        self.setup_speech_recognition()
        self.reminders = []
        self.music_folder = self.find_music_folder()
        self.wake_word = "jarvis"
        self.is_listening = False
        self.setup_gemini()
        self.setup_volume_control()
        self.email_config = self.load_email_config()
        
    def setup_voice(self):
        """Configure voice properties using Windows SAPI"""
        try:
            self.speaker = win32com.client.Dispatch("SAPI.SpVoice")
            self.speaker.Rate = 1
            self.speaker.Volume = 100
            print("✓ Voice engine initialized (Windows SAPI)")
        except Exception as e:
            print(f"❌ Error initializing speech: {e}")
            sys.exit(1)
    
    def setup_volume_control(self):
        """Setup Windows volume control"""
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume = cast(interface, POINTER(IAudioEndpointVolume))
            print("✓ Volume control initialized")
        except Exception as e:
            print(f"⚠️  Volume control unavailable: {e}")
            self.volume = None
    
    def load_email_config(self):
        """Load email configuration"""
        config = {
            'email': os.environ.get('JARVIS_EMAIL'),
            'password': os.environ.get('JARVIS_EMAIL_PASSWORD'),
            'smtp_server': os.environ.get('JARVIS_SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.environ.get('JARVIS_SMTP_PORT', '587'))
        }
        
        if not config['email'] or not config['password']:
            print("\n⚠️  Email not configured. Set these environment variables:")
            print("   JARVIS_EMAIL=your_email@gmail.com")
            print("   JARVIS_EMAIL_PASSWORD=your_app_password")
            print("   (For Gmail, use App Password: https://myaccount.google.com/apppasswords)\n")
        else:
            print(f"✓ Email configured: {config['email']}")
        
        return config
    
    def setup_gemini(self):
        """Setup Google Gemini AI"""
        print("\n🤖 Setting up Google Gemini AI...")
        
        api_key = os.environ.get("GEMINI_API_KEY")
        
        if not api_key:
            print("\n⚠️  GEMINI API KEY NOT FOUND!")
            print("To enable AI conversations:")
            print("1. Get free API key from: https://makersuite.google.com/app/apikey")
            print("2. Set environment variable: set GEMINI_API_KEY=your_key_here\n")
            self.gemini_model = None
        else:
            try:
                genai.configure(api_key=api_key)
                print("   Checking available models...")
                available_models = genai.list_models()
                
                working_model = None
                for model in available_models:
                    if 'generateContent' in model.supported_generation_methods:
                        working_model = model.name
                        break
                
                if working_model:
                    self.gemini_model = genai.GenerativeModel(working_model)
                    print(f"✓ Google Gemini AI ready! (using {working_model})")
                else:
                    print("❌ No compatible Gemini model found")
                    self.gemini_model = None
                    
            except Exception as e:
                print(f"❌ Gemini setup error: {e}")
                self.gemini_model = None
                
    def setup_speech_recognition(self):
        """Setup Vosk speech recognition"""
        print("\n🔧 Setting up speech recognition...")
        
        # Try to use the larger, more accurate model
        model_path = "vosk-model-en-us-0.22"
        fallback_model = "vosk-model-small-en-us-0.15"
        
        # Check for larger model first
        if not os.path.exists(model_path):
            print(f"\n💡 TIP: For better accuracy, download the larger model:")
            print(f"   https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip")
            print(f"   Extract to script folder for improved recognition\n")
            
            # Fall back to small model
            model_path = fallback_model
            
            if not os.path.exists(model_path):
                print("\n📥 Downloading speech recognition model (first time only)...")
                print("   Manual download: https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip")
                
                try:
                    import urllib.request
                    import zipfile
                    
                    url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
                    zip_path = "vosk-model.zip"
                    
                    print("   Downloading...")
                    urllib.request.urlretrieve(url, zip_path)
                    print("   Extracting...")
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(".")
                    os.remove(zip_path)
                    print("   ✓ Model downloaded!")
                except Exception as e:
                    print(f"\n   ❌ Auto-download failed: {e}")
                    sys.exit(1)
        
        try:
            self.model = Model(model_path)
            # Increase sample rate for better quality
            self.recognizer = KaldiRecognizer(self.model, 16000)
            # Enable partial results for real-time feedback
            self.recognizer.SetWords(True)
            print(f"✓ Speech recognition ready! (using {model_path})")
            print("💡 TIPS FOR BETTER RECOGNITION:")
            print("   • Speak clearly and at a moderate pace")
            print("   • Reduce background noise")
            print("   • Position microphone 6-12 inches from mouth")
            print("   • Pause briefly between 'Jarvis' and your command\n")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            sys.exit(1)
        
    def speak(self, text):
        """Convert text to speech"""
        print(f"\n🤖 Jarvis: {text}")
        try:
            self.speaker.Speak(text)
        except Exception as e:
            print(f"❌ Speech error: {e}")
            try:
                self.setup_voice()
                self.speaker.Speak(text)
            except:
                print("⚠️  Speech engine failed")
                
    def listen_continuous(self):
        """Continuous listening with wake word detection"""
        print("\n🎤 Listening for wake word 'Jarvis'...")
        print("💡 Say 'Jarvis' followed by your command\n")
        
        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Status: {status}")
            self.audio_queue.put(bytes(indata))
        
        try:
            with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                                  channels=1, callback=audio_callback):
                
                while True:
                    data = self.audio_queue.get()
                    
                    if self.recognizer.AcceptWaveform(data):
                        result = json.loads(self.recognizer.Result())
                        text = result.get('text', '').lower()
                        
                        if text:
                            if self.wake_word in text:
                                print(f"🟢 Wake word detected!")
                                command = text.replace(self.wake_word, '').strip()
                                
                                if command:
                                    print(f"✓ Command: {command}")
                                    return command
                                else:
                                    print("🎤 Yes Sir? I'm listening...")
                                    self.speak("Yes Sir Abdessamed?")
                                    command = self.listen_for_command()
                                    if command:
                                        return command
                    else:
                        partial = json.loads(self.recognizer.PartialResult())
                        partial_text = partial.get('partial', '')
                        if partial_text and self.wake_word in partial_text:
                            print(f"   Detecting: {partial_text}", end='\r')
                            
        except KeyboardInterrupt:
            print("\n⏹️  Stopped listening")
            return None
        except Exception as e:
            print(f"\n❌ Microphone error: {e}")
            return None
    
    def listen_for_command(self, timeout=5):
        """Listen for a command after wake word"""
        start_time = time.time()
        
        try:
            while time.time() - start_time < timeout:
                data = self.audio_queue.get(timeout=1)
                
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get('text', '').lower()
                    
                    if text:
                        print(f"✓ Command: {text}")
                        return text
        except:
            pass
        
        return ""
    
    # AI & Search Functions
    def ask_gemini(self, question):
        """Ask Google Gemini AI a question"""
        if not self.gemini_model:
            self.speak("Sir Abdessamed, AI conversations are not configured. Please set up your Gemini API key")
            return
        
        try:
            self.speak("Sir Abdessamed, let me think about that")
            prompt = f"You are Jarvis, an AI assistant. Answer this question concisely in 2-3 sentences: {question}"
            response = self.gemini_model.generate_content(prompt)
            answer = response.text
            self.speak(f"Sir Abdessamed, {answer}")
        except Exception as e:
            print(f"Gemini error: {e}")
            self.speak("Sir Abdessamed, I encountered an error processing your question")
    
    # Time & Weather Functions
    def get_time(self):
        """Get current time"""
        now = datetime.datetime.now()
        time_str = now.strftime("%I:%M %p")
        self.speak(f"Sir Abdessamed, the time is {time_str}")
        
    def get_date(self):
        """Get current date"""
        now = datetime.datetime.now()
        date_str = now.strftime("%A, %B %d, %Y")
        self.speak(f"Sir Abdessamed, today is {date_str}")
        
    def get_weather(self, city="Algiers"):
        """Get weather information"""
        try:
            url = f"http://wttr.in/{city}?format=%C+%t"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                weather_info = response.text.strip()
                self.speak(f"Sir Abdessamed, the weather in {city} is {weather_info}")
            else:
                self.speak("Sir Abdessamed, I couldn't retrieve the weather information")
        except Exception as e:
            self.speak("Sir Abdessamed, weather service is currently unavailable")
    
    # News Functions
    def get_news(self):
        """Get latest news headlines"""
        try:
            # Using NewsAPI (you can get free API key from newsapi.org)
            api_key = os.environ.get('NEWS_API_KEY')
            
            if not api_key:
                # Fallback to RSS feed scraping
                self.speak("Sir Abdessamed, fetching latest headlines")
                url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    # Simple parsing of first few headlines
                    import re
                    titles = re.findall(r'<title>(.*?)</title>', response.text)[1:4]  # Skip first (feed title)
                    
                    headlines = "Here are the top headlines: "
                    for i, title in enumerate(titles, 1):
                        # Remove CDATA tags
                        clean_title = title.replace('<![CDATA[', '').replace(']]>', '')
                        headlines += f"{i}. {clean_title}. "
                    
                    self.speak(f"Sir Abdessamed, {headlines}")
                else:
                    self.speak("Sir Abdessamed, I couldn't fetch the news at the moment")
            else:
                # Use NewsAPI if available
                url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
                response = requests.get(url, timeout=10)
                data = response.json()
                
                if data['status'] == 'ok':
                    articles = data['articles'][:3]
                    headlines = "Here are the top headlines: "
                    for i, article in enumerate(articles, 1):
                        headlines += f"{i}. {article['title']}. "
                    self.speak(f"Sir Abdessamed, {headlines}")
                    
        except Exception as e:
            print(f"News error: {e}")
            self.speak("Sir Abdessamed, I encountered an error fetching the news")
    
    # Email Functions
    def send_email(self, command):
        """Send email via voice command"""
        if not self.email_config['email'] or not self.email_config['password']:
            self.speak("Sir Abdessamed, email is not configured. Please set up your email credentials")
            return
        
        try:
            # Parse command for recipient and message
            # Example: "send email to john@example.com saying hello"
            self.speak("Sir Abdessamed, what is the recipient's email address?")
            # In real implementation, you'd listen for the email
            # For now, we'll guide the user
            self.speak("Please note: Voice email sending requires additional setup. I recommend using the web interface for now")
            
        except Exception as e:
            print(f"Email error: {e}")
            self.speak("Sir Abdessamed, I encountered an error sending the email")
    
    # Volume Control Functions
    def set_volume(self, level):
        """Set system volume (0-100)"""
        if not self.volume:
            self.speak("Sir Abdessamed, volume control is not available")
            return
        
        try:
            volume_level = max(0.0, min(1.0, level / 100.0))
            self.volume.SetMasterVolumeLevelScalar(volume_level, None)
            self.speak(f"Sir Abdessamed, volume set to {level} percent")
        except Exception as e:
            print(f"Volume error: {e}")
            self.speak("Sir Abdessamed, I couldn't adjust the volume")
    
    def increase_volume(self):
        """Increase volume by 10%"""
        if not self.volume:
            self.speak("Sir Abdessamed, volume control is not available")
            return
        
        try:
            current = self.volume.GetMasterVolumeLevelScalar()
            new_volume = min(1.0, current + 0.1)
            self.volume.SetMasterVolumeLevelScalar(new_volume, None)
            self.speak(f"Sir Abdessamed, volume increased to {int(new_volume * 100)} percent")
        except Exception as e:
            self.speak("Sir Abdessamed, I couldn't increase the volume")
    
    def decrease_volume(self):
        """Decrease volume by 10%"""
        if not self.volume:
            self.speak("Sir Abdessamed, volume control is not available")
            return
        
        try:
            current = self.volume.GetMasterVolumeLevelScalar()
            new_volume = max(0.0, current - 0.1)
            self.volume.SetMasterVolumeLevelScalar(new_volume, None)
            self.speak(f"Sir Abdessamed, volume decreased to {int(new_volume * 100)} percent")
        except Exception as e:
            self.speak("Sir Abdessamed, I couldn't decrease the volume")
    
    def mute_volume(self):
        """Mute/unmute system volume"""
        if not self.volume:
            self.speak("Sir Abdessamed, volume control is not available")
            return
        
        try:
            current_mute = self.volume.GetMute()
            self.volume.SetMute(not current_mute, None)
            status = "unmuted" if current_mute else "muted"
            self.speak(f"Sir Abdessamed, system {status}")
        except Exception as e:
            self.speak("Sir Abdessamed, I couldn't mute the system")
    
    # File Management Functions
    def create_file(self, command):
        """Create a new file"""
        try:
            # Extract filename from command
            words = command.split()
            if "file" in words:
                idx = words.index("file") + 1
                if idx < len(words):
                    filename = words[idx]
                    if not '.' in filename:
                        filename += '.txt'
                    
                    desktop = Path.home() / "Desktop"
                    filepath = desktop / filename
                    
                    filepath.touch()
                    self.speak(f"Sir Abdessamed, I have created {filename} on your desktop")
                else:
                    self.speak("Sir Abdessamed, please specify a filename")
            else:
                self.speak("Sir Abdessamed, I didn't understand the filename")
        except Exception as e:
            print(f"File creation error: {e}")
            self.speak("Sir Abdessamed, I encountered an error creating the file")
    
    def create_folder(self, command):
        """Create a new folder"""
        try:
            words = command.split()
            if "folder" in words:
                idx = words.index("folder") + 1
                if idx < len(words):
                    foldername = words[idx]
                    
                    desktop = Path.home() / "Desktop"
                    folderpath = desktop / foldername
                    
                    folderpath.mkdir(exist_ok=True)
                    self.speak(f"Sir Abdessamed, I have created folder {foldername} on your desktop")
                else:
                    self.speak("Sir Abdessamed, please specify a folder name")
            else:
                self.speak("Sir Abdessamed, I didn't understand the folder name")
        except Exception as e:
            print(f"Folder creation error: {e}")
            self.speak("Sir Abdessamed, I encountered an error creating the folder")
    
    def delete_file(self, command):
        """Delete a file (with safety confirmation)"""
        self.speak("Sir Abdessamed, file deletion requires manual confirmation for safety")
    
    # Screenshot & System Functions  
    def take_screenshot(self):
        """Take a screenshot"""
        try:
            screenshot = pyautogui.screenshot()
            filename = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            desktop = Path.home() / "Desktop"
            filepath = desktop / filename
            screenshot.save(filepath)
            self.speak(f"Sir Abdessamed, I have captured your screen and saved it to your desktop")
        except Exception as e:
            self.speak("Sir Abdessamed, I encountered an error taking the screenshot")
    
    def get_system_info(self):
        """Get system information"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            battery = psutil.sensors_battery()
            
            info = f"Sir Abdessamed, CPU usage is at {cpu_percent} percent, memory usage is at {memory_percent} percent"
            
            if battery:
                battery_percent = battery.percent
                plugged = "plugged in" if battery.power_plugged else "on battery"
                info += f", and battery is at {battery_percent} percent and {plugged}"
            
            self.speak(info)
        except Exception as e:
            self.speak("Sir Abdessamed, I encountered an error getting system information")
    
    # Application & Web Functions
    def open_application(self, app_name):
        """Open applications"""
        import subprocess
        apps = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "chrome": "chrome.exe",
            "browser": "chrome.exe",
            "explorer": "explorer.exe",
            "paint": "mspaint.exe",
            "word": "winword.exe",
            "excel": "excel.exe"
        }
        
        for key, exe in apps.items():
            if key in app_name:
                try:
                    subprocess.Popen(exe)
                    self.speak(f"Sir Abdessamed, opening {key}")
                    return
                except:
                    self.speak(f"Sir Abdessamed, I couldn't open {key}")
                    return
        
        self.speak("Sir Abdessamed, I don't know how to open that application")
    
    def open_website(self, command):
        """Open websites"""
        websites = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "gmail": "https://mail.google.com",
            "facebook": "https://www.facebook.com",
            "twitter": "https://www.twitter.com",
            "reddit": "https://www.reddit.com",
            "github": "https://www.github.com",
            "amazon": "https://www.amazon.com",
            "netflix": "https://www.netflix.com",
            "linkedin": "https://www.linkedin.com"
        }
        
        for site, url in websites.items():
            if site in command:
                webbrowser.open(url)
                self.speak(f"Sir Abdessamed, opening {site}")
                return True
        return False
    
    def search_google(self, query):
        """Search Google"""
        search_query = query.replace("search google for", "").replace("google", "").strip()
        if search_query:
            url = f"https://www.google.com/search?q={search_query}"
            webbrowser.open(url)
            self.speak(f"Sir Abdessamed, searching Google for {search_query}")
        else:
            self.speak("Sir Abdessamed, what would you like me to search for?")
    
    def search_wikipedia(self, query):
        """Search Wikipedia"""
        search_query = query.replace("wikipedia", "").replace("search", "").strip()
        if search_query:
            try:
                self.speak(f"Sir Abdessamed, searching Wikipedia for {search_query}")
                result = wikipedia.summary(search_query, sentences=2)
                self.speak(f"According to Wikipedia: {result}")
            except wikipedia.exceptions.DisambiguationError:
                self.speak(f"Sir Abdessamed, there are multiple results. Please be more specific")
            except wikipedia.exceptions.PageError:
                self.speak(f"Sir Abdessamed, I couldn't find any results for {search_query}")
            except:
                self.speak("Sir Abdessamed, Wikipedia search is currently unavailable")
        else:
            self.speak("Sir Abdessamed, what would you like me to search on Wikipedia?")
    
    # Music & Media Functions
    def find_music_folder(self):
        """Find music folder"""
        possible_paths = [
            Path.home() / "Music",
            Path.home() / "Downloads",
            Path("C:/Music"),
            Path.home() / "Desktop"
        ]
        
        for path in possible_paths:
            try:
                if path.exists():
                    music_files = list(path.glob("*.mp3")) + list(path.glob("*.wav"))
                    if music_files:
                        return path
            except:
                continue
        return None
    
    def play_music(self):
        """Play random music from music folder"""
        if not self.music_folder:
            self.speak("Sir Abdessamed, I couldn't find any music files. Please add MP3 files to your Music folder")
            return
        
        music_files = list(self.music_folder.glob("*.mp3")) + list(self.music_folder.glob("*.wav"))
        
        if not music_files:
            self.speak("Sir Abdessamed, no music files found in the Music folder")
            return
        
        song = random.choice(music_files)
        os.startfile(song)
        self.speak(f"Sir Abdessamed, playing {song.stem}")
    
    # Reminder Functions
    def set_reminder(self, command):
        """Set a reminder/timer"""
        words = command.split()
        
        try:
            if "minute" in command or "minutes" in command:
                for i, word in enumerate(words):
                    if word.isdigit():
                        minutes = int(word)
                        reminder_text = " ".join(words[i+2:]) if len(words) > i+2 else "your reminder"
                        
                        self.speak(f"Sir Abdessamed, setting a reminder for {minutes} minutes")
                        
                        def remind():
                            time.sleep(minutes * 60)
                            self.speak(f"Sir Abdessamed, reminder: {reminder_text}")
                        
                        reminder_thread = threading.Thread(target=remind, daemon=True)
                        reminder_thread.start()
                        return
            
            elif "second" in command or "seconds" in command:
                for i, word in enumerate(words):
                    if word.isdigit():
                        seconds = int(word)
                        reminder_text = " ".join(words[i+2:]) if len(words) > i+2 else "your reminder"
                        
                        self.speak(f"Sir Abdessamed, setting a reminder for {seconds} seconds")
                        
                        def remind():
                            time.sleep(seconds)
                            self.speak(f"Sir Abdessamed, reminder: {reminder_text}")
                        
                        reminder_thread = threading.Thread(target=remind, daemon=True)
                        reminder_thread.start()
                        return
        except:
            pass
        
        self.speak("Sir Abdessamed, I didn't understand the time. Please say something like 'remind me in 5 minutes'")
    
    # Command Processing
    def process_command(self, command):
        """Process commands with fuzzy matching for better recognition"""
        if not command:
            return True
            
        command = command.lower().strip()
        
        # Show what was heard for debugging
        print(f"📝 Recognized: '{command}'")
        
        # Fuzzy matching helpers
        def contains_any(text, words):
            return any(word in text for word in words)
        
        # Time and Date
        if contains_any(command, ["time", "clock"]):
            self.get_time()
        
        elif contains_any(command, ["date", "day", "today"]):
            self.get_date()
        
        # Weather & News
        elif contains_any(command, ["weather", "temperature"]):
            self.get_weather()
        
        elif contains_any(command, ["news", "headline"]):
            self.get_news()
        
        # Volume Control - more flexible matching
        elif contains_any(command, ["louder", "turn up", "raise volume"]) or "increase volume" in command or "volume up" in command:
            self.increase_volume()
        
        elif contains_any(command, ["quieter", "turn down", "lower volume"]) or "decrease volume" in command or "volume down" in command:
            self.decrease_volume()
        
        elif "mute" in command or "unmute" in command or "silent" in command:
            self.mute_volume()
        
        elif contains_any(command, ["set volume", "volume to", "volume at"]):
            try:
                # Extract number from command
                import re
                numbers = re.findall(r'\d+', command)
                if numbers:
                    self.set_volume(int(numbers[0]))
                    return True
                self.speak("Sir Abdessamed, please specify a volume level between 0 and 100")
            except:
                self.speak("Sir Abdessamed, I didn't understand the volume level")
        
        # File Management - more flexible
        elif contains_any(command, ["create file", "make file", "new file"]):
            self.create_file(command)
        
        elif contains_any(command, ["create folder", "make folder", "new folder"]):
            self.create_folder(command)
        
        # Screenshot - multiple ways to say it
        elif contains_any(command, ["screenshot", "screen shot", "capture screen", "take picture", "screen capture"]):
            self.take_screenshot()
        
        # Open websites - more flexible
        elif "open" in command:
            if not self.open_website(command):
                self.open_application(command)
        
        # Search - handle variations
        elif contains_any(command, ["search google", "google search", "look up", "search for"]):
            self.search_google(command)
        
        elif contains_any(command, ["wikipedia", "wiki"]):
            self.search_wikipedia(command)
        
        # Music - multiple phrases
        elif contains_any(command, ["play music", "play song", "play a song", "put on music"]):
            self.play_music()
        
        # Reminders - handle variations
        elif contains_any(command, ["remind me", "reminder", "set timer", "set alarm"]):
            self.set_reminder(command)
        
        # System info - multiple ways
        elif contains_any(command, ["system info", "system status", "cpu", "battery", "memory", "performance"]):
            self.get_system_info()
        
        # Email
        elif contains_any(command, ["send email", "write email", "compose email"]):
            self.send_email(command)
        
        # Greetings - more variations
        elif contains_any(command, ["hello", "hi", "hey", "greetings"]):
            self.speak("Hello Sir Abdessamed, how may I assist you today?")
        
        elif contains_any(command, ["how are you", "how you doing", "what's up"]):
            self.speak("I'm functioning at optimal capacity, Sir Abdessamed. How may I help you?")
        
        elif contains_any(command, ["thank", "thanks", "appreciate"]):
            self.speak("You're most welcome, Sir Abdessamed")
        
        # Exit - multiple ways to say goodbye
        elif contains_any(command, ["exit", "quit", "goodbye", "good bye", "bye", "stop", "shutdown", "shut down", "close"]):
            self.speak("Goodbye Sir Abdessamed, have a great day")
            return False
        
        # AI Conversation - if nothing else matches
        else:
            question_words = ["what", "who", "when", "where", "why", "how", "can", "is", "are", "do", "does", "tell me", "explain", "define"]
            if any(word in command for word in question_words):
                self.ask_gemini(command)
            else:
                # Give helpful feedback
                self.speak("Sir Abdessamed, I didn't quite understand that command")
                print("💡 Try rephrasing or check the command list")
        
        return True
    
    def run(self):
        """Main loop with wake word detection"""
        print("\n" + "="*70)
        print(" "*15 + "🤖 JARVIS AI ASSISTANT - ULTIMATE EDITION 🤖")
        print("="*70)
        
        self.speak("Good day, Sir Abdessamed. Jarvis is online and ready to assist")
        
        print("\n📋 ULTIMATE FEATURES:")
        print("   🎤 Wake Word Detection - Say 'Jarvis'")
        print("   🤖 AI Conversations - Ask me anything")
        print("   📧 Email Integration - Send emails by voice")
        print("   📰 News Reader - Latest headlines")
        print("   🔊 Volume Control - Adjust system volume")
        print("   📁 File Management - Create files & folders")
        print("   ⏰ Time & Weather | 🌐 Web & Search | 🎵 Music")
        print("   ⏲️ Reminders | 💻 System Info | 📸 Screenshots")
        
        print("\n💡 EXAMPLE COMMANDS:")
        print("   • 'Jarvis, what time is it?'")
        print("   • 'Jarvis, open youtube'")
        print("   • 'Jarvis, what is quantum physics?'")
        print("   • 'Jarvis, get me the latest news'")
        print("   • 'Jarvis, increase volume'")
        print("   • 'Jarvis, create file report'")
        print("   • 'Jarvis, create folder projects'")
        print("   • 'Jarvis, set volume to 50'")
        print("   • 'Jarvis, remind me in 5 minutes'")
        print("   • Say 'Jarvis shutdown' to exit")
        print("\n" + "="*70 + "\n")
        
        running = True
        while running:
            try:
                command = self.listen_continuous()
                if command:
                    running = self.process_command(command)
                    if running:
                        print("\n🎤 Listening for wake word 'Jarvis'...\n")
            except KeyboardInterrupt:
                print("\n\n⚠️  Shutting down...")
                self.speak("Goodbye Sir Abdessamed")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                continue

if __name__ == "__main__":
    print("\n" + "="*70)
    print("📦 JARVIS ULTIMATE EDITION - INSTALLATION CHECK")
    print("="*70)
    print("\nRequired packages:")
    print("  • vosk, sounddevice, pywin32")
    print("  • requests, pyautogui, pillow")
    print("  • psutil, wikipedia")
    print("  • google-generativeai")
    print("  • pycaw (for volume control)")
    print("\nOptional configuration:")
    print("  • GEMINI_API_KEY - For AI conversations")
    print("  • NEWS_API_KEY - For detailed news (optional)")
    print("  • JARVIS_EMAIL - For email sending (optional)")
    print("  • JARVIS_EMAIL_PASSWORD - Gmail App Password (optional)")
    print("\n" + "="*70 + "\n")
    
    try:
        assistant = JarvisAssistant()
        assistant.run()
    except Exception as e:
        print(f"\n❌ Failed to start: {e}")
        print("\n📦 Install all packages:")
        print("pip install vosk sounddevice pywin32 requests pyautogui pillow")
        print("pip install psutil wikipedia google-generativeai pycaw")