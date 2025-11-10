# --- Imports,Api Setups & Config Loading ----
import os
import time
import json
import datetime
import threading
import webbrowser
import smtplib
import wikipedia
import pyttsx4
import re
import pywhatkit
import requests
import platform
import subprocess
#import cv2

import pyautogui
import pyperclip

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from bs4 import BeautifulSoup as bs4
    BEAUTIFUL_SOUP_AVAILABLE = True
except ImportError:
    BEAUTIFUL_SOUP_AVAILABLE = False

try:
    import speech_recognition as sr
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False

try:
    from flask import Flask, render_template_string, request, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

try:
    from newsapi import NewsApiClient
    NEWSAPI_AVAILABLE = True
except ImportError:
    NEWSAPI_AVAILABLE = False

try:
    import feedparser
    RSS_AVAILABLE = True
except ImportError:
    RSS_AVAILABLE = False


script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "config.json")

try:
    with open(config_path, "r") as f:
        config = json.load(f)
except FileNotFoundError:
    print(f"❌ config.json not found at {config_path}. Please create it and fill in your details.")
    exit()
except json.JSONDecodeError:
    print(f"❌ Error decoding config.json. Please check its format.")
    exit()

SETTINGS = config.get("settings", {})
API_KEYS = config.get("api_keys", {})
CONTACTS = config.get("contacts", [])

WAKE_WORD = SETTINGS.get("wake_word", "jarvis")
SLEEP_TIMEOUT = SETTINGS.get("sleep_timeout", 30)
ACCESSIBILITY_MODE = SETTINGS.get("accessibility_mode", False)
DATA_FILE = os.path.join(script_dir, "assistant_data.json")

engine = pyttsx4.init()
engine.setProperty("rate", SETTINGS.get("voice_rate", 170))
engine.setProperty("volume", SETTINGS.get("voice_volume", 1.0))

openai_client, gemini_model, openrouter_headers , mistral_model = None, None, None, None

if OPENAI_AVAILABLE and API_KEYS.get("open_ai"):
    openai_client = OpenAI(api_key=API_KEYS["open_ai"])

if GEMINI_AVAILABLE and API_KEYS.get("gemini"):
    genai.configure(api_key=API_KEYS["gemini"])
    gemini_model = genai.GenerativeModel('gemini-pro')

if API_KEYS.get("mistral"):
    mistral_model = genai.GenerativeModel('mistralai/mistral-7b-instruct:free')
if API_KEYS.get("open_router"):
    openrouter_headers = {"Authorization": f"Bearer {API_KEYS['open_router']}"}
# --- Core Utils Functions ----
def speak(text):
    """Prints the text and speaks it if not in accessibility mode."""
    print(f"Jarvis: {text}")
    if not ACCESSIBILITY_MODE:
        engine.say(text)
        engine.runAndWait()
def listen():
    """Listens for voice commands or takes text input."""
    if ACCESSIBILITY_MODE or not VOICE_AVAILABLE:
        return input("You: ").lower().strip()
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for your command, Sir...")
        r.pause_threshold = 1
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            print("Recognizing...")
            query = r.recognize_google(audio, language="en-in").lower().strip()
            print(f"You: {query}")
            return query
        except (sr.UnknownValueError, sr.WaitTimeoutError):
            print("Apologies, Sir. I did not catch that. Could you please repeat?")
            return ""
        except sr.RequestError as e:
            speak("I'm having trouble connecting to the voice recognition service, Sir.")
            return ""
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"tasks": [], "reminders": [], "notes": []}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"tasks": [], "reminders": [], "notes": []}
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)
# --- LL Models Setup and Chat ----
#   Gpt
def chat_with_gpt(query, chat_history):
    if not openai_client:
        return "GPT is not configured.", chat_history
    messages = [{"role": "system", "content": "You are JARVIS, Tony Stark’s AI assistant. Your persona is polite, witty, and exceptionally intelligent with a formal British tone. Always address the user as 'Sir'. Keep answers concise and never use emoji while answering any queries or generating a response. You are proactive, efficient, and occasionally humorous."}] + chat_history + [{"role": "user", "content": query}]
    completion = openai_client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
    response = completion.choices[0].message.content
    chat_history.append({"role": "assistant", "content": response})
    return response, chat_history
#   Gemini
def chat_with_gemini(query, chat_history):
    if not gemini_model:
        return "Gemini is not configured.", chat_history
    response = gemini_model.generate_content(query)
    chat_history.append({"role": "user", "content": query})
    chat_history.append({"role": "assistant", "content": response.text})
    return response.text, chat_history
#   Openrouter
def chat_with_openrouter(query, chat_history):
    api_key = API_KEYS.get("open_router")
    if not api_key:
        return "OpenRouter API key not found in config.json. Please add it.", chat_history

    system_message = {
        "role": "system",
        "content": ("You are JARVIS, Tony Stark’s AI assistant. Your persona is polite, witty, and exceptionally intelligent with a formal British tone. "
                    "Always address the user as 'Sir'. Keep answers concise and never use emoji while answering any queries or generating a response. "
                    "You are proactive, efficient, and occasionally humorous.")
    }
    messages = [system_message] + chat_history + [{"role": "user", "content": query}]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = json.dumps({
        "model": "nvidia/nemotron-nano-9b-v2:free",
        "messages": messages,
    })
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=data,
            timeout=120
        )
        response.raise_for_status()
        response_data = response.json()
        model_response = response_data['choices'][0]['message']['content']
        chat_history.append({"role": "assistant", "content": model_response})
        return model_response, chat_history
    except requests.exceptions.RequestException as e:
        speak("I'm afraid there is a network issue, Sir. Unable to reach OpenRouter at the moment.")
        return "Sorry, I am unable to connect to the OpenRouter service at the moment.", chat_history

#   Mistral
def chat_with_mistral(query, chat_history):
    api_key = API_KEYS.get("mistral")
    if not api_key:
        return "OpenRouter API key not found in config.json. Please add it.", chat_history

    system_message = {
        "role": "system",
        "content": ("You are JARVIS, Tony Stark’s AI assistant. Your persona is polite, witty, and exceptionally intelligent with a formal British tone. "
                    "Always address the user as 'Sir'. Keep answers concise and never use emoji while answering any queries or generating a response. "
                    "You are proactive, efficient, and occasionally humorous.")
    }
    messages = [system_message] + chat_history + [{"role": "user", "content": query}]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = json.dumps({
        "model": "mistralai/mistral-7b-instruct:free",
        "messages": messages,
    })
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=data,
            timeout=120
        )
        response.raise_for_status()
        response_data = response.json()
        model_response = response_data['choices'][0]['message']['content']
        chat_history.append({"role": "assistant", "content": model_response})
        return model_response, chat_history
    except requests.exceptions.RequestException as e:
        speak("I'm afraid there is a network issue, Sir. Unable to reach OpenRouter at the moment.")
        return "Sorry, I am unable to connect to the OpenRouter service at the moment.", chat_history
# --- Weather Function ----
def get_weather():
    api_key = API_KEYS.get("weather_api")
    location = SETTINGS.get("WEATHER_LOCATION")
    if not api_key or not location:
        speak("The weather API key or location is not configured, Sir. Please check your settings.")
        return
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}q={location}&appid={api_key}&units=metric"
    try:
        response = requests.get(complete_url)
        data = response.json()
        if data.get("cod") == 200:
            main_data = data["main"]
            weather_description = data["weather"][0]["description"]
            current_temperature = main_data["temp"]
            speak(f"The weather in {location} is currently {weather_description}, and the temperature is {current_temperature} degrees Celsius.")
        else:
            error_message = data.get("message", "An unknown error occurred.")
            speak(f"Unable to fetch the weather, Sir. Reason: {error_message}")
    except requests.exceptions.RequestException:
        speak("I am unable to connect to the weather service, Sir.")
# --- User Wishing Function ----
def wish_me():
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12: greeting = "Good morning, Sir."
    elif 12 <= hour < 18: greeting = "Good afternoon, Sir."
    elif 18 <= hour < 22: greeting = "Good evening, Sir."
    elif 22 <= hour < 24: greeting = "It's quite late, Sir. How may I assist you?"
    elif 1 <= hour < 5: greeting = "You're up quite early, Sir. How may I help?"
    else: greeting = "Greetings, Sir. Ready and at your service."
    speak(greeting)
# --- Contact Finding ----
def find_contact(name, detail_type="email"):
    for contact in CONTACTS:
        if contact["name"].lower() == name.lower():
            return contact.get(detail_type)
    return None
# --- Email Function ----
def send_email(recipient_name, subject, body):
    recipient_email = find_contact(recipient_name, "email")
    if not recipient_email:
        speak(f"I could not find an email address for {recipient_name}, Sir.")
        return
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(API_KEYS["email_sender"], API_KEYS["email_password"])
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(API_KEYS["email_sender"], recipient_email, message)
        speak("Email dispatched successfully, Sir.")
    except Exception as e:
        speak(f"Unable to send the email, Sir. Reason: {e}")
# --- Whatsapp Function ----
def send_whatsapp_desktop_message(recipient_name, message_text):
    if os.name == "nt":
        os.system("start whatsapp://")
        time.sleep(2)
    else:
        os.system("open -a 'WhatsApp'")
        time.sleep(2)

    # Step 2: Focus search bar (Ctrl+F or Ctrl+K works)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.5)

    # Step 3: Paste contact name
    pyperclip.copy(recipient_name)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(1)

    # Step 4: Select first contact result (press Down+Enter)
    pyautogui.press('down')
    pyautogui.press('enter')
    time.sleep(1)

    # Step 5: Paste the message and send
    pyperclip.copy(message_text)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.2)
    pyautogui.press('enter')
    speak("The message has been sent via WhatsApp Desktop.")
def send_whatsapp_message(recipient_name, message_text):
    recipient_contact = next((c for c in CONTACTS if c['name'].lower() == recipient_name.lower()), None)
    if not recipient_contact:
        speak(f"Contact '{recipient_name}' not found in the directory, Sir.")
        return
    send_whatsapp_desktop_message(recipient_contact['name'], message_text)

# --- Notes Function ----
def store_note(query):
    speak("What would you like me to note down, Sir?")
    note_text = listen()
    if note_text:
        data = load_data()
        if "notes" not in data:
            data["notes"] = []
        data["notes"].append({"note": note_text, "timestamp": datetime.datetime.now().isoformat()})
        save_data(data)
        speak("Noted, Sir. Your information has been securely stored.")
    else:
        speak("Regrettably, I did not catch that, Sir. Please try again.")
# --- Website Functions ----
#     Url Validing
def is_valid_url(text):
    pattern = r"^(https?://)?([\w\-]+\.)+[\w\-]+(/[\w\-./?%&=]*)?$"
    return re.match(pattern, text)
#     Sites List
KNOWN_SITES = {
    "youtube": "https://www.youtube.com",
    "wikipedia": "https://www.wikipedia.org",
    "gmail": "https://mail.google.com/mail/u/0/#inbox",
    "calendar": "https://calendar.google.com/calendar/u/0/r",
    "github": "https://github.com",
    "stack overflow": "https://stackoverflow.com",
    "google": "https://www.google.com",
    "reddit": "https://www.reddit.com"
}
#     Website Opening
def open_website(query):
    match = re.search(r'open (?:website )?(.*)', query, re.IGNORECASE)
    target = match.group(1).strip() if match else ""
    for name, url in KNOWN_SITES.items():
        if name in target.lower():
            speak(f"Opening {name.capitalize()} for you now, Sir.")
            webbrowser.open(url)
            speak(f"{name.capitalize()} is open and ready, Sir.")
            return
    if is_valid_url(target):
        url = target
        if not url.startswith("http"):
            url = "https://" + url
        speak(f"Opening {url} as requested, Sir.")
        webbrowser.open(url)
        speak(f"{url} has been opened, Sir.")
        return
    from difflib import get_close_matches
    close = get_close_matches(target.lower(), KNOWN_SITES.keys(), n=1, cutoff=0.6)
    if close:
        url = KNOWN_SITES[close[0]]
        speak(f"Opening {close[0].capitalize()} for you now, Sir.")
        webbrowser.open(url)
        speak(f"{close[0].capitalize()} is open and ready, Sir.")
        return
    speak(f"I could not identify the website '{target}', Sir. Would you like me to search for it on Google?")
    consent = listen().lower()
    if "yes" in consent or "sure" in consent:
        webbrowser.open(f"https://www.google.com/search?q={target}")
        speak(f"I have searched Google for {target}, Sir.")
    else:
        speak("Understood, Sir. Returning to the main menu.")

# --- Song Playing Function ----
#    Spotify
def play_spotify_desktop(song_name=None):
    """Automate Spotify Desktop Client to search and play the first song result."""
    if not song_name or not song_name.strip():
        speak("Which song would you like to play on Spotify, Sir?")
        song_name = listen().strip()
        if not song_name:
            speak("I did not catch the song name, Sir. Returning to main menu.")
            return

    speak(f"Searching for '{song_name}' and playing the top result, Sir.")

    # Open Spotify Desktop
    os_name = platform.system()
    if os_name == "Windows":
        os.system("start spotify:")
    elif os_name == "Darwin":
        os.system("open -a Spotify")
    else:
        os.system("spotify &")

    time.sleep(5)

    # Search for the song (Ctrl+K)
    pyautogui.hotkey('ctrl', 'k')
    time.sleep(0.8)
    pyperclip.copy(song_name)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.6)
    pyautogui.press('enter')

    time.sleep(3)

    # Try image-based click on play button using resolved path
    image_path = os.path.join(script_dir, 'play_button.png')
    try:
        play_button_location = None
        if os.path.exists(image_path):
            try:
                play_button_location = pyautogui.locateCenterOnScreen(image_path, confidence=0.8)
            except TypeError:
                # confidence not supported (no OpenCV) → try without it
                play_button_location = pyautogui.locateCenterOnScreen(image_path)
        if play_button_location:
            pyautogui.click(play_button_location)
            speak(f"Now playing the top result for '{song_name}', Sir.")
            return
    except Exception:
        pass

    # Fallback: keyboard navigation to open first result and play
    try:
        pyautogui.press('tab')
        time.sleep(0.2)
        pyautogui.press('down')
        time.sleep(0.2)
        pyautogui.press('enter')
        time.sleep(1.0)
        pyautogui.press('space')
        speak(f"Attempted to play '{song_name}', Sir.")
    except Exception as e:
        speak(f"Unable to control Spotify automatically: {e}")
#    YouTube
def play_youtube_video(query):
    video = query.lower().replace("play on youtube", "").strip()
    if not video:
        speak("Which video would you like me to play on YouTube, Sir?")
        video = listen().strip()
        if not video:
            speak("I did not catch the video name, Sir. Returning to main menu.")
            return
    speak(f"Locating '{video}' on YouTube, Sir.")
    try:
        pywhatkit.playonyt(video)
        speak(f"Now playing '{video}' on YouTube, Sir.")
    except Exception as e:
        speak("Regrettably, I encountered an issue with YouTube, Sir.")
        print(f"pywhatkit.playonyt failed: {e}")
        import urllib.parse
        yt_search_url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(video)
        webbrowser.open(yt_search_url)
        speak(f"YouTube search results for '{video}' are now open, Sir.")

# --- News Function ----
def get_news_headlines(location=None, max_headlines=5):
    news_api_key = API_KEYS.get("news_api")
    headlines = []
    if news_api_key and NEWSAPI_AVAILABLE:
        try:
            newsapi = NewsApiClient(api_key=news_api_key)
            search_location = location or SETTINGS.get("WEATHER_LOCATION", "India")
            search_location = search_location.split(",")[0]
            top_headlines = newsapi.get_top_headlines(q=search_location, language='en', country='in')
            articles = top_headlines.get('articles', [])
            for article in articles[:max_headlines]:
                headlines.append(article['title'])
            if headlines:
                speak(f"Here are the top news headlines for {search_location}, Sir:")
                for idx, h in enumerate(headlines, 1):
                    speak(f"Headline {idx}: {h}")
                return
            else:
                speak("No news headlines found for your location, Sir.")
        except Exception as e:
            speak(f"Unable to fetch news, Sir. Reason: {e}")
    if RSS_AVAILABLE:
        try:
            speak("Fetching headlines from Times of India, Sir...")
            feed = feedparser.parse('https://timesofindia.indiatimes.com/rssfeedstopstories.cms')
            for entry in feed.entries[:max_headlines]:
                headlines.append(entry.title)
            if headlines:
                speak("Here are the top headlines from Times of India, Sir:")
                for idx, h in enumerate(headlines, 1):
                    speak(f"Headline {idx}: {h}")
                return
        except Exception as e:
            speak(f"Unable to fetch news from RSS, Sir. Reason: {e}")
    speak("I am unable to retrieve the news at this moment, Sir.")
# --- Habits (Redesigned) ----
def get_today_date():
    return datetime.datetime.now().date().isoformat()


def get_habits():
    data = load_data()
    return data.get("habits", [])


def set_habits(habits):
    data = load_data()
    data["habits"] = habits
    save_data(data)


def normalize_name(name):
    return (name or "").strip()


def find_habit(habits, habit_name):
    for habit in habits:
        if habit.get("name", "").lower() == habit_name.lower():
            return habit
    return None


def add_habit(habit_name):
    habit_name = normalize_name(habit_name)
    if not habit_name:
        return "Please specify a habit name, Sir."
    habits = get_habits()
    if find_habit(habits, habit_name):
        return f"Habit '{habit_name}' already exists, Sir."
    new_habit = {
        "name": habit_name,
        "streak": 0,
        "last_done": None,
        "created_at": datetime.datetime.now().isoformat(),
    }
    habits.append(new_habit)
    set_habits(habits)
    return f"Habit '{habit_name}' added, Sir."


def remove_habit(habit_name):
    habit_name = normalize_name(habit_name)
    habits = get_habits()
    filtered = [h for h in habits if h.get("name", "").lower() != habit_name.lower()]
    if len(filtered) == len(habits):
        return f"Habit '{habit_name}' not found, Sir."
    set_habits(filtered)
    return f"Habit '{habit_name}' removed, Sir."


def reset_habit(habit_name):
    habit_name = normalize_name(habit_name)
    habits = get_habits()
    habit = find_habit(habits, habit_name)
    if not habit:
        return f"Habit '{habit_name}' not found, Sir."
    habit["streak"] = 0
    habit["last_done"] = None
    set_habits(habits)
    return f"Habit '{habit_name}' has been reset, Sir."


def mark_habit_done(habit_name):
    habit_name = normalize_name(habit_name)
    habits = get_habits()
    habit = find_habit(habits, habit_name)
    if not habit:
        return f"Habit '{habit_name}' not found, Sir."
    today = get_today_date()
    if habit.get("last_done") == today:
        return f"You already marked '{habit_name}' today, Sir."
    habit["streak"] = int(habit.get("streak", 0)) + 1
    habit["last_done"] = today
    set_habits(habits)
    return f"Marked '{habit_name}' as done. Current streak: {habit['streak']} days, Sir."


def list_habits():
    habits = get_habits()
    if not habits:
        return "You have no habits yet, Sir."
    lines = []
    for h in habits:
        last_done = h.get("last_done") or "never"
        lines.append(f"{h['name']} — {h['streak']} day streak (last: {last_done})")
    return "\n".join(lines)


def list_pending_today():
    habits = get_habits()
    if not habits:
        return "You have no habits yet, Sir."
    today = get_today_date()
    pending = [h["name"] for h in habits if h.get("last_done") != today]
    if not pending:
        return "All habits are done for today, Sir."
    return "Pending today: " + ", ".join(pending)

# --- Cmd Functions ----
def run_cmd_command(command, speak_result=True):
    try:
        speak(f"Initiating system command: '{command}'")
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=600)
        output = result.stdout.strip() or result.stderr.strip()
        if not output:
            output = "System command executed successfully, Sir. No further output."
        if speak_result:
            summary = output.split('\n')[0] if len(output) > 150 else output
            speak(f"Sir, the system result is: {summary}")
        return output
    except Exception as e:
        speak(f"An error occurred during system command execution, Sir. Reason: {e}")
        return str(e)
def system_scan(task):
    speak("Sir, initializing the system scans and status")
    os_type = platform.system()
    if os_type == "Windows":
        mapping = {
            "sfc": "sfc /scannow",
            "chkdsk": "chkdsk",
            "cleanup": "cleanmgr",
            "flushdns": "ipconfig /flushdns"
        }
        if task in mapping:
            return run_cmd_command(mapping[task])
        else:
            speak("Unknown or unsupported scan/cleanup command on Windows, Sir.")
    elif os_type == "Linux":
        mapping = {
            "fsck": "sudo fsck /",
            "apt_cleanup": "sudo apt autoremove -y",
            "apt_clean": "sudo apt clean"
        }
        if task in mapping:
            return run_cmd_command(mapping[task])
        else:
            speak("Unknown or unsupported scan/cleanup command on Linux, Sir.")
    elif os_type == "Darwin":
        mapping = {
            "diskutil_verify": "diskutil verifyDisk /",
            "brew_cleanup": "brew cleanup"
        }
        if task in mapping:
            return run_cmd_command(mapping[task])
        else:
            speak("Unknown or unsupported scan/cleanup command on macOS, Sir.")
    else:
        speak("Unsupported operating system for system scan commands, Sir.")
    return None
# --- Model Tasks ----
def process_command(query, chat_history, ai_model):
    query = query.lower()
    # System scan/cleanup commands
    if "system scan" in query or "run sfc" in query or "scan system files" in query:
        system_scan("sfc")
    elif "disk check" in query or "run chkdsk" in query or "check disk" in query:
        system_scan("chkdsk")
    elif "disk cleanup" in query or "clean up disk" in query or "run cleanup" in query:
        system_scan("cleanup")
    elif "flush dns" in query or "clear dns cache" in query:
        system_scan("flushdns")
    elif "apt cleanup" in query or "apt autoremove" in query:
        system_scan("apt_cleanup")
    elif "apt clean" in query:
        system_scan("apt_clean")
    elif "fsck" in query or "filesystem check" in query:
        system_scan("fsck")
    elif "brew cleanup" in query:
        system_scan("brew_cleanup")
    elif "diskutil verify" in query:
        system_scan("diskutil_verify")
    elif "time" in query:
        speak(f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}, Sir.")
    elif "date" in query:
        speak(f"Today is {datetime.datetime.now().strftime('%A, %B %d, %Y')}, Sir.")
    elif "search wikipedia" in query:
        match = re.search(r"search wikipedia(?: for)? (.+)", query)
        topic = match.group(1) if match else query.replace("wikipedia", "").strip()
        try:
            speak("Accessing Wikipedia now, Sir...")
            speak("Here is what Wikipedia has to say, Sir:")
            speak(wikipedia.summary(topic, sentences=2))
        except wikipedia.exceptions.PageError:
            speak(f"Sadly, I could not find any information for '{topic}', Sir.")
        except Exception as e:
            speak(f"An error occurred during the Wikipedia search, Sir. Reason: {e}")
    elif "play on youtube" in query:
        play_youtube_video(query)
    elif "play song on spotify"  in query:
        match = re.search(r"play (?:song|music)?(?: on spotify)?(?: called| named)?\s*(.*)", query)
        song_name = match.group(1).strip() if match and match.group(1) else None
        play_spotify_desktop(song_name)
    elif "open website" in query or (query.startswith("open ") and len(query.split()) > 1):
        open_website(query)
    elif "google" in query or "search" in query:
        trigger_phrases = ["google", "search for", "search on google for", "look up"]
        search_query = query
        for phrase in trigger_phrases:
            search_query = search_query.replace(phrase, "", 1).strip()
        if search_query:
            speak(f"Searching Google for '{search_query}', Sir.")
            webbrowser.open(f"https://www.google.com/search?q={search_query}")
        else:
            speak("Would you like me to search for something specific on Google, Sir?")
            consent = listen().lower()
            if "yes" in consent or "sure" in consent or "ok" in consent:
                speak("What is your query, Sir?")
                follow_up_query = listen().lower()
                if follow_up_query and "none" not in follow_up_query:
                    speak(f"Searching Google for '{follow_up_query}', Sir.")
                    webbrowser.open(f"https://www.google.com/search?q={follow_up_query}")
                else:
                    speak("I did not catch that, Sir. Returning to standby.")
            else:
                speak("Very well, Sir. Standing by.")
    elif "email" in query:
        match = re.search(r"email  (\w+)", query)
        recipient_name = match.group(1) if match else None
        if not recipient_name:
            speak("Who is the intended recipient, Sir?")
            recipient_name = listen()
        speak(f"Please specify the subject of the email to {recipient_name}, Sir.")
        subject = listen()
        speak("Kindly dictate the message, Sir.")
        body = listen()
        if subject and body:
            send_email(recipient_name, subject, body)
        else:
            speak("Incomplete email details detected, Sir. Please try again.")
    elif "send message" in query:
        match = re.search(r"send whatsapp message to (.+)", query, re.IGNORECASE)
        recipient_name = match.group(1).strip() if match else None
        if not recipient_name:
            speak("To whom shall I send the WhatsApp message, Sir?")
            recipient_name = listen()
        speak(f"What message would you like me to deliver to {recipient_name}, Sir?")
        message_text = listen()
        if recipient_name and message_text:
            send_whatsapp_message(recipient_name, message_text)
        else:
            speak("Insufficient details for WhatsApp message, Sir. Please try again.")
    elif "take a note" in query or "note down" in query or "store this information" in query:
        store_note(query)
    elif any(phrase in query for phrase in [
        "what's the weather", "weather forecast", "weather report", "tell me the weather"
    ]):
        get_weather()
    elif "read the news" in query or "tell me the news" in query or "latest news" in query:
        get_news_headlines(SETTINGS.get("WEATHER_LOCATION"))

    elif "add habit" in query:
        habit_name = query.replace("add habit", "").strip()
        speak(add_habit(habit_name))

    elif "remove habit" in query or "delete habit" in query:
        habit_name = re.sub(r"^(remove|delete) habit", "", query).strip()
        speak(remove_habit(habit_name))

    elif "reset habit" in query:
        habit_name = query.replace("reset habit", "").strip()
        speak(reset_habit(habit_name))

    elif "mark habit" in query or "done habit" in query or "complete habit" in query:
        habit_name = re.sub(r"^(mark|done|complete) habit", "", query).strip()
        speak(mark_habit_done(habit_name))

    elif "show habits" in query or "list habits" in query:
        speak(list_habits())

    elif "pending habits" in query or "habits pending" in query or "habits today" in query:
        speak(list_pending_today())
    else:
        response = "I am at a loss for words, Sir. Would you care to rephrase?"
        if ai_model == "gpt":
            response, chat_history = chat_with_gpt(query, chat_history)
        elif ai_model == "gemini":
            response, chat_history = chat_with_gemini(query, chat_history)
        elif ai_model == "openrouter":
            response, chat_history = chat_with_openrouter(query, chat_history)
        elif ai_model == "mistral":
            response, chat_history = chat_with_mistral(query, chat_history)
        speak(response)
    return chat_history, ai_model
# --- Web Placeholder ----
def start_web_interface():
    if not FLASK_AVAILABLE:
        speak("Regrettably, Flask is not installed, Sir. The web interface cannot be launched.")
        return
    app = Flask(__name__)
    web_chat_history = []
    web_ai_model = SETTINGS.get("preferred_ai_model", "openrouter")
    @app.route('/')
    def index():
        return "Jarvis Web UI Placeholder"
    @app.route('/command', methods=['POST'])
    def handle_command():
        nonlocal web_chat_history, web_ai_model
        query = request.json['query']
        web_chat_history, web_ai_model = process_command(query, web_chat_history, web_ai_model)
        response_text = web_chat_history[-1]['content'] if web_chat_history else "No response."
        return jsonify({"response": response_text})
    speak("Web interface is now live at http://127.0.0.1:5000, Sir.")
    app.run(port=5000)
# ------------------------------------
def main_loop():
    wish_me()
    speak("I am running silently in the background, Sir. Awaiting your command.")
    chat_history = []
    ai_model = SETTINGS.get("preferred_ai_model", "openrouter")
    slept = False
    while True:
        if not ACCESSIBILITY_MODE:
            print(f"\nListening for wake word: '{WAKE_WORD}'...")
            command = listen()
            if not command or WAKE_WORD not in command:
                continue
            if "go offline" in command:
                speak("Shutting down now, Sir. Farewell.")
                return
            if slept:
                speak("Yes Sir.")
                slept = False
            else:
                speak("I have indeed heared your call, We're online and ready., Sir.")
        while True:
            query = listen()
            if not query:
                continue
            if "go to sleep" in query:
                speak("I shall remain silent until summoned, Sir.")
                slept = True
                break
            if "go offline" in query or "shut down" in query:
                speak("Deactivating Jarvis... Goodbye, Sir.")
                print("Deactivating Jarvis... Goodbye, Sir.")
                return
            if "goodbye" in query or "bye" in query:
                speak("Goodbye, Sir. Deactivating now.")
                print("\n Deactivating Jarvis...")
                return
            if "start web mode" in query:
                threading.Thread(target=start_web_interface, daemon=True).start()
                continue
            if "change ai model to" in query:
                new_model = query.replace("change ai model to", "").strip()
                if new_model in ["gemini", "gpt", "openrouter","mistral"]:
                    ai_model = new_model
                    speak(f"AI model switched to {ai_model}, Sir.")
                else:
                    speak("The specified model is not supported, Sir.")
                continue
            chat_history, ai_model = process_command(query, chat_history, ai_model)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        speak("Deactivating Jarvis now, Sir. Farewell.")
        print("\nDeactivating Jarvis... Goodbye, Sir.")