# --- Initial Imports ----
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
import playsound
import sys
import shutil
import psutil
#import cv2
import pkg_resources
import pyautogui
import pyperclip
import random
from colorama import init, Fore, Style , Back

# Simple mute control (no threading)
is_muted = False

try: #Keyborad
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False

# ----- Jarvis Modules Imports -------
from jarvis_modules.file_handler import FileHandler
#from jarvis_modules.performance_logger import PerformanceLogger
#from jarvis_modules.module_bridge import ModuleBridge
try: # Ai Summarizer Module 
    from jarvis_modules.ai_summarizer import summarize_file, summarize_text
except Exception:
    print("Sir,I apologise for not being able to import Summarizer module sucessfuly")

try: # Self Repair Module 
    from jarvis_modules.self_repair import self_repair
except Exception:
    print("Sir,I apologise for not being able to import Self Repair module sucessfuly")

try: # App Manger Module 
    from jarvis_modules.advanced_app_manager import initialize_app_manager, process_app_command , speak , active_appcloser
    APP_MANAGER_AVAILABLE = True
except ImportError:
    APP_MANAGER_AVAILABLE = False
    print("Advanced App Manager not available. Using fallback methods.")

# App Management Module 
app_manager_instance = None
if APP_MANAGER_AVAILABLE:
    app_manager_instance = initialize_app_manager(speak)

try: # Platform Checker [Win]
    if platform.system() == "Windows":
        import win32gui
        import win32con
        WINDOWS_NOTIF_AVAILABLE = True
    else:
        WINDOWS_NOTIF_AVAILABLE = False
except ImportError:
    WINDOWS_NOTIF_AVAILABLE = False

# ---- Global State for Time Prompts ----
last_time_prompt = {
    "morning_greeting": None,
    "lunch_reminder": None,
    "evening_reminder": None,
    "night_warning": None,
    "break_reminder": None,
    "hydration": None,
    "posture_check": None,
    "vscode_coding_session": None  # NEW: VS Code tracking
}

last_notification_check = time.time()
notification_cooldown = 300  # 5 minutes between notification checks

from email_manager import EmailManager

# ---- Application Tracking State ----
app_start_times = {}  # Track when apps were first detected

try: # Sysytem Monitoring Module 
    import system_monitor
    SYSTEM_MONITOR_AVAILABLE = True
except Exception:
    system_monitor = None
    SYSTEM_MONITOR_AVAILABLE = False

try: # Terminal Module 
    from terminal_operations import create_default_operator
    TERMINAL_OPS_AVAILABLE = True
except Exception:
    create_default_operator = None
    TERMINAL_OPS_AVAILABLE = False

try: # OpenAI
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try: # Google GenAi
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try: #Beautiful Soup
    from bs4 import BeautifulSoup as bs4
    BEAUTIFUL_SOUP_AVAILABLE = True
except ImportError:
    BEAUTIFUL_SOUP_AVAILABLE = False

try: # Speech Recognition 
    import speech_recognition as sr
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False

import asyncio
try: # Edge TTS 
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

try: # Flask Import 
    from flask import Flask, render_template_string, request, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

try: # News Api
    from newsapi import NewsApiClient
    NEWSAPI_AVAILABLE = True
except ImportError:
    NEWSAPI_AVAILABLE = False

try: # Feed Parser
    import feedparser
    RSS_AVAILABLE = True
except ImportError:
    RSS_AVAILABLE = False

try: # Beep Audio
    mp3_file_path = "beep.mp3" 
except Exception:
    print("The beep audio is not imported sucessfuly")

# ---- Config Path -----
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "config.json")

# ---- Config Loading -----
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
#MAILER = EmailManager(speak, API_KEYS, config)

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

# ---- Sequences and Animations ----
from rich.console import Console
from rich.spinner import Spinner
from rich.live import Live
from pyfiglet import Figlet
from colorama import Fore, Style, init
import random

def jarvis_boot_sequence(version="v17"):
    """Main JARVIS boot sequence"""
    
    # Display banner
    display_jarvis_banner()
    
    # Header
    print(Fore.CYAN + Style.BRIGHT + "===============================================")
    print("     INITIALIZING J.A.R.V.I.S MAINFRAME")
    print(Fore.CYAN + Style.BRIGHT + "===============================================")
    time.sleep(0.6)
    
    # Boot steps
    boot_steps = [
        "Initializing AI Core Engine",
        "Loading Neural Speech Interface",
        "Linking System Directories",
        "Establishing Secure Protocols",
        "Authenticating User Access",
        "Loading Environment Variables",
        "Optimizing Runtime Performance",
        "Activating Visual & Audio Subsystems"
    ]
    
    for step in boot_steps:
        # Show red checkmark with spinner
        spinner = Spinner("dots", text=f"[red]✗[/red] {step}", style="cyan")
        with Live(spinner, console=console, refresh_per_second=10):
            time.sleep(random.uniform(0.3, 0.6))
        
        # Show bright blue checkmark when complete
        console.print(f"[bright_blue]✓[/bright_blue] {step}")
        time.sleep(0.1)
    
    print(Fore.CYAN + "-----------------------------------------------")
    time.sleep(0.3)
    
    # System diagnostics
    cpu_usage = psutil.cpu_percent(interval=0.3)
    mem = psutil.virtual_memory()
    mem_used = round(mem.used / (1024 ** 3), 2)
    mem_total = round(mem.total / (1024 ** 3), 2)
    net_io = psutil.net_io_counters()
    upload = round(net_io.bytes_sent / (1024 ** 2), 2)
    download = round(net_io.bytes_recv / (1024 ** 2), 2)
    
    print(Fore.YELLOW + f"→ CPU Load: {cpu_usage}%")
    print(Fore.YELLOW + f"→ Memory Usage: {mem_used}GB / {mem_total}GB")
    print(Fore.YELLOW + f"→ Network I/O: ↑ {upload} MB  ↓ {download} MB")
    time.sleep(0.5)
    
    print(Fore.CYAN + "-----------------------------------------------")
    print(f"CORE STATUS: STABLE")
    print(Fore.WHITE + Style.BRIGHT + f"VERSION: {version.upper()}")
    print(f"MODE: Operational")
    print(Fore.CYAN + "-----------------------------------------------")
    
    # Loading bar animation
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
    print()
    with Progress(
        SpinnerColumn(spinner_name="dots"),
        TextColumn("[cyan]Activating main subsystems..."),
        BarColumn(bar_width=30),
        TextColumn("[green]{task.percentage:>3.0f}%"),
        console=console,
    ) as progress:
        task = progress.add_task("", total=100)
        for _ in range(100):
            progress.update(task, advance=1)
            time.sleep(0.015)
    print()
    
    # Final activation
    time.sleep(0.5)
    print("System integrity check: PASS")
    time.sleep(0.4)
    print(">>> All Systems Online.")
    time.sleep(0.3)
    print(">>> JARVIS CORE ACTIVATED.")
    time.sleep(0.5)
    print()
    
    # Final message in blue
    print(Fore.BLUE + Style.BRIGHT + "JARVIS Successfully booted.")
    print(Fore.BLUE + Style.BRIGHT + "Welcome back, Sir!")
    print(Style.RESET_ALL)

def jarvis_wakeup_sequence():
    """
    Quick wake-up animation for reactivating JARVIS from standby.
    Sleek, minimal, and synchronized with prior sleep mode visuals.
    """
    init(autoreset=True)
    os.system('cls' if os.name == 'nt' else 'clear')

    def slow_print(text, delay=0.01, color=Fore.WHITE):
        for char in text:
            sys.stdout.write(color + char)
            sys.stdout.flush()
            time.sleep(delay)
        print()

    print(Fore.CYAN + Style.BRIGHT + "===============================================")
    slow_print("        Reactivating Jarvis", 0.02, Fore.CYAN)
    print(Fore.CYAN + Style.BRIGHT + "===============================================")
    time.sleep(0.4)

    # ⚡ Quick reactivation animation
    for i in range(3):
        sys.stdout.write(Fore.GREEN + Style.BRIGHT + "⚡ Syncing Core Systems" + "." * (i+1) + "\r")
        sys.stdout.flush()
        time.sleep(0.4)
    print(" " * 50, end="\r")

    # System modules coming online
    wake_steps = [
        "Neural Speech Interface: Active",
        "Cognitive Engine: Online",
        "System Directories: Linked",
        "Data Channels: Re-established",
        "Visual & Audio Subsystems: Ready"
    ]

    for step in wake_steps:
        slow_print(Fore.GREEN + f"[✓] {step}", 0.02)
        time.sleep(0.05)

    print(Fore.CYAN + "-----------------------------------------------")
    slow_print(Fore.GREEN + Style.BRIGHT + "SYSTEM STATUS: ONLINE", 0.02)
    slow_print(Fore.CYAN + "MODE: Reactivation", 0.02)
    slow_print(Fore.YELLOW + "RUNTIME SYNCHRONIZED", 0.02)
    print(Fore.CYAN + "-----------------------------------------------")
    time.sleep(0.5)

    # Pulse animation to indicate active state
    for i in range(3):
        sys.stdout.write(Fore.CYAN + Style.BRIGHT + "• SYSTEM LINK RESTORED •".center(60))
        sys.stdout.flush()
        time.sleep(0.4)
        sys.stdout.write(" " * 60 + "\r")
        sys.stdout.flush()
        time.sleep(0.4)

    slow_print(Fore.GREEN + Style.BRIGHT + "Welcome back, Sir. All systems reactivated.", 0.03)
    time.sleep(0.5)
    print(Style.RESET_ALL)
def jarvis_listening_animation(duration=4):
    """
    Displays a reactive listening animation (like AI voice wave).
    Ideal for speech recognition phase.
    """
    init(autoreset=True)
    print(Fore.CYAN + Style.BRIGHT + "\n[🎙️] Listening...")

    pulse_patterns = [
        "▁▂▃▄▅▆▇█▇▆▅▄▃▂▁",
        "▁▂▃▄▅▆▇▆▅▄▃▂▁",
        "▁▂▃▄▅▆▇█▇▆▅▄▃▂▁"
    ]

    end_time = time.time() + duration
    while time.time() < end_time:
        for pattern in pulse_patterns:
            sys.stdout.write(Fore.CYAN + Style.BRIGHT + f"\r{pattern}")
            sys.stdout.flush()
            time.sleep(0.1)
    print("\r" + " " * 40 + "\r", end="")
    print(Fore.GREEN + Style.BRIGHT + "[✔] Command recognized.\n")
    time.sleep(0.4)
def jarvis_sleep_sequence():
    init(autoreset=True)
    os.system('cls' if os.name == 'nt' else 'clear')

    def slow_print(text, delay=0.015, color=Fore.WHITE):
        for char in text:
            sys.stdout.write(color + char)
            sys.stdout.flush()
            time.sleep(delay)
        print()

    print(Fore.YELLOW + Style.BRIGHT + "===============================================")
    slow_print("     ENTERING LOW POWER STANDBY MODE", 0.02, Fore.YELLOW)
    print(Fore.YELLOW + Style.BRIGHT + "===============================================")
    time.sleep(0.5)

    # Gradual dimming animation
    for i in range(5):
        sys.stdout.write(Fore.YELLOW + Style.BRIGHT + f"Reducing Core Activity{'.' * (i+1)}\r")
        sys.stdout.flush()
        time.sleep(0.4)
    print(" " * 50, end="\r")

    # Subsystem suspension
    sleep_steps = [
        "Neural Speech Interface: Idle",
        "Cognitive Engine: Paused",
        "Memory Cache: Preserved",
        "Data Channels: Dormant",
        "AI Awareness: Suspended"
    ]

    for step in sleep_steps:
        slow_print(Fore.CYAN + f"[~] {step}", 0.02)
        time.sleep(0.1)

    print(Fore.YELLOW + "-----------------------------------------------")
    slow_print(Fore.YELLOW + Style.BRIGHT + "Currently running in Background", 0.02)
    slow_print(Fore.CYAN + "Low power status", 0.02)
    print(Fore.YELLOW + "-----------------------------------------------")

    # Soft pulsing light
    for i in range(6):
        sys.stdout.write(Fore.BLUE + Style.BRIGHT + ("• JARVIS SLEEPING •".center(50)))
        sys.stdout.flush()
        time.sleep(0.5)
        sys.stdout.write(" " * 60 + "\r")
        sys.stdout.flush()
        time.sleep(0.5)

    slow_print(Fore.YELLOW + Style.BRIGHT + "Awaiting wake word to reactivate...", 0.03)
    print(Style.RESET_ALL)

def jarvis_shutdown_sequence():
    init(autoreset=True)
    os.system('cls' if os.name == 'nt' else 'clear')

    def slow_print(text, delay=0.015, color=Fore.WHITE):
        for char in text:
            sys.stdout.write(color + char)
            sys.stdout.flush()
            time.sleep(delay)
        print()


    slow_print(" DEACTIVATING J.A.R.V.I.S", 0.02, Fore.RED)
    time.sleep(0.5)

    # 🔻 Simulated module deactivation
    shutdown_steps = [
        "Disengaging Neural Speech Interface",
        "Disconnecting System Protocols",
        "Saving Runtime State and Session Data",
        "Powering Down Auxiliary Subsystems",
        "Terminating AI Core Threads",
        "Releasing Memory and Resources",
        "Closing Secure Data Channels"
    ]

    for step in shutdown_steps:
        sys.stdout.write(Fore.YELLOW + f"[–] {step}")
        sys.stdout.flush()
        time.sleep(0.25)
        print()
        time.sleep(0.1)

    print(Fore.RED + "-----------------------------------------------")
    time.sleep(0.3)

    # ⚡ Fade-out progress bar
    slow_print("Deactivating Core Systems:", 0.02, Fore.WHITE)
    for i in range(30, -1, -1):
        bar = "█" * i + "-" * (30 - i)
        sys.stdout.write(Fore.RED + f"\r[{bar}] {int((i/30)*100)}%")
        sys.stdout.flush()
        time.sleep(0.05)
    print("\n")

    # 💠 Power-down pulse animation
    for i in range(3):
        sys.stdout.write(Fore.RED + Style.BRIGHT + "⚡ SYSTEM ENERGY DROPPING " + "." * (i+1) + "\r")
        sys.stdout.flush()
        time.sleep(0.5)
    print(" " * 50, end="\r")

    # 🧠 Final status
    print(Fore.RED + "-----------------------------------------------")
    slow_print("CORE STATUS: OFFLINE", 0.02)
    slow_print("SYSTEM MEMORY: Released", 0.02)
    slow_print("DATA LINKS: Terminated", 0.02)
    slow_print("All subsystems deactivated.", 0.02)
    print(Fore.RED + "-----------------------------------------------")
    time.sleep(0.5)

    # 👋 Farewell message
    slow_print("Goodbye, Sir. System will now power down...", 0.03)
    time.sleep(0.6)
    slow_print("J.A.R.V.I.S. Offline.", 0.03)
    fig = Figlet(font="univers")  # You can try 'ansi_shadow' or 'ansi_regular','slant','univers',big'
    banner = fig.renderText("JARVIS")
    print(Fore.RED  + Style.DIM + banner + Style.RESET_ALL) # for style except BRIGHT/DIM/NORMAL
    print(Style.RESET_ALL)
    time.sleep(0.5)
from pyfiglet import Figlet
init(autoreset=True)
console = Console()
def display_jarvis_banner():
    """Displays JARVIS banner centered"""
    os.system("cls" if os.name == "nt" else "clear")
    
    # Get terminal width
    terminal_width = os.get_terminal_size().columns
    
    fig = Figlet(font="univers")
    banner = fig.renderText("JARVIS")
    
    # Center each line of the banner
    for line in banner.splitlines():
        print(Fore.BLUE + Style.BRIGHT + line.center(terminal_width))
    
    print(Style.RESET_ALL)

def jarvis_sleep_animation():
    """Cinematic sleep mode effect."""
    init(autoreset=True)
    for i in range(3):
        sys.stdout.write(Fore.MAGENTA + f"\rEntering sleep mode{'.' * (i+1)}")
        sys.stdout.flush()
        time.sleep(0.6)
    print("\r" + " " * 40, end="\r")
    print(Fore.MAGENTA + "💤 JARVIS is now in standby mode. Awaiting wake word..." + Style.RESET_ALL)

# --- Core Utils Functions ----
def check_tts_engine():
    if EDGE_TTS_AVAILABLE:
        try:
            import edge_tts
            print("✅ Neural Voice Module Online")
            speak("Neural voice interface online.")
        except Exception as e:
            print(f"⚠️ Edge-TTS detected but failed: {e}")
            speak("Fallback voice active, neural engine offline.")
    else:
        print("❌ Edge-TTS not installed.")
        speak("Neural voice module not found, using local voice system.")
# The modular personality speak function
_last_personality = "neutral"  # tone continuity
import asyncio
import tempfile
def format_honorific(text):
    """Replace 'Sir' with user's preferred honorific in text."""
    honorific = get_honorific()
    # Replace "Sir" with the user's honorific (case-insensitive)
    import re
    return re.sub(r'\bSir\b', honorific, text, flags=re.IGNORECASE)
def load_personality():
    data = load_data()
    return data.get("personality_profile", {
        "tone": "formal",
        "verbosity": 0.5,
        "humor_level": 0.2,
        "interaction_score": 0
    })
def save_personality(profile):
    data = load_data()
    data["personality_profile"] = profile
    save_data(data)
def update_personality_context(successful_interaction=True):
    profile = load_personality()
    if successful_interaction:
        profile["interaction_score"] += 1
        if profile["interaction_score"] % 10 == 0:
            profile["verbosity"] = min(1.0, profile["verbosity"] + 0.05)
    else:
        profile["interaction_score"] = max(0, profile["interaction_score"] - 1)
    save_personality(profile)
def speak(text, allow_interrupt=True):
    """
    Enhanced speak with keyboard interrupt capability.
    Press ESC key to stop speech (no threading needed).
    Checks mute flag between sentences for clean interruption.
    """
    global _last_personality, is_muted

    text = format_honorific(text)
    # Check if muted
    if is_muted:
        #print(f"[Muted] {text}")
        print(f"{Fore.RED}[MUTED]{Style.RESET_ALL} Jarvis: {text}")
        return

    # Emotion detection
    emotion_map = {
        "error": "serious",
        "warning": "alert",
        "task completed": "cheerful",
        "completed": "cheerful",
        "success": "cheerful",
        "greeting": "calm",
        "critical": "alert",
        "failed": "serious",
        "failure": "serious",
        "good morning": "cheerful",
        "good evening": "calm",
        "offline": "calm",
        "sleep": "calm",
        "shutdown": "serious",
        "system": "neutral",
        "sir": "calm"
    }

    lowered = text.lower()
    personality = _last_personality
    for key, mode in emotion_map.items():
        if key in lowered:
            personality = mode
            break
    _last_personality = personality

    print(f"Jarvis: {text}")

    if ACCESSIBILITY_MODE:
        return

    # === Try Edge-TTS ===
    if EDGE_TTS_AVAILABLE:
        try:
            voice_id = "en-US-EricNeural" # Human-Like-Resource
            
            async def edge_tts_speak():
                tmp_path = tempfile.mktemp(suffix=".mp3")
                communicate = edge_tts.Communicate(text, voice=voice_id, rate="+10%", pitch="+0Hz")
                await communicate.save(tmp_path)
                
                # Play audio inline without external popup using pygame or playsound
                try:
                    # Try playsound first (already in your imports)
                    import playsound
                    playsound.playsound(tmp_path, block=True)
                except:
                    # Fallback to pygame if playsound fails
                    try:
                        import pygame
                        pygame.mixer.init()
                        pygame.mixer.music.load(tmp_path)
                        pygame.mixer.music.play()
                        while pygame.mixer.music.get_busy():
                            # Check mute flag during playback
                            if is_muted:
                                pygame.mixer.music.stop()
                                break
                            pygame.time.Clock().tick(10)
                    except:
                        # Last resort: pydub
                        try:
                            from pydub import AudioSegment
                            from pydub.playback import play
                            audio = AudioSegment.from_mp3(tmp_path)
                            play(audio)
                        except:
                            print("[Audio Playback Failed] Falling back to pyttsx4")
                            raise Exception("All audio players failed")
                
                # Cleanup temp file immediately after playback
                try:
                    os.remove(tmp_path)
                except:
                    pass

            asyncio.run(edge_tts_speak())
            return

        except Exception as e:
            print(f"[Edge-TTS Error] Fallback to pyttsx4 – {e}")

    # === Fallback: pyttsx4 with sentence-level interrupts ===
    try:
        base_rate = SETTINGS.get("voice_rate", 170)
        base_volume = SETTINGS.get("voice_volume", 1.0)
        voices = engine.getProperty("voices")

        # Strong emotional modulation
        if personality == "cheerful":
            engine.setProperty("rate", base_rate + 50)
            engine.setProperty("volume", min(base_volume + 0.15, 1.0))
        elif personality == "serious":
            engine.setProperty("rate", base_rate - 30)
            engine.setProperty("volume", max(base_volume - 0.15, 0.5))
        elif personality == "alert":
            engine.setProperty("rate", base_rate + 40)
            engine.setProperty("volume", min(base_volume + 0.05, 1.0))
        elif personality == "calm":
            engine.setProperty("rate", base_rate - 40)
            engine.setProperty("volume", max(base_volume - 0.05, 0.6))
        else:
            engine.setProperty("rate", base_rate)
            engine.setProperty("volume", base_volume)

        # Voice swap if available
        if len(voices) > 1:
            if personality in ["cheerful", "calm"]:
                engine.setProperty("voice", voices[0].id)
            else:
                engine.setProperty("voice", voices[0].id)

        # Split text into sentences for interrupt points
        if allow_interrupt:
            sentences = re.split(r'[.!?]+', text)
            for sentence in sentences:
                if is_muted:
                    print("Speech interrupted by mute")
                    break
                if sentence.strip():
                    engine.say(sentence.strip())
                    engine.runAndWait()
        else:
            # No interruption - speak all at once
            engine.say(text)
            engine.runAndWait()

    except Exception as e:
        print(f"Speak Fallback Error {e}")
def test_microphone():
    """Run a short voice calibration and feedback test."""
    speak("Starting microphone calibration and voice recognition test, Sir.")
    try:
        result = listen()
        if not result:
            speak("I didn’t catch any input, Sir. Please ensure your microphone is active.")
        else:
            speak(f"I successfully heard you say: {result}")
    except Exception as e:
        speak(f"There was an issue during the microphone test, Sir. {e}")
def _safe_input(prompt="You: "):
    """Used only in accessibility mode or when voice is unavailable."""
    try:
        return input(prompt).lower().strip()
    except Exception:
        return ""
def listen():
    if ACCESSIBILITY_MODE or not VOICE_AVAILABLE:
        return _safe_input()

    r = sr.Recognizer()
    phrase_time_limit = int(SETTINGS.get("phrase_time_limit", 16))
    timeout = float(SETTINGS.get("voice_timeout", 4))
    language = SETTINGS.get("language", "en-us")
    pause_threshold = float(SETTINGS.get("pause_threshold", 1.3))
    
    # Advanced tuning
    r.pause_threshold = pause_threshold
    r.energy_threshold = int(SETTINGS.get("energy_threshold", 4000))
    r.dynamic_energy_threshold = SETTINGS.get("dynamic_energy_threshold", True)
    
    if SETTINGS.get("energy_threshold_adjustment"):
        r.dynamic_energy_adjustment_damping = float(SETTINGS.get("energy_threshold_adjustment", 1.5))
        r.dynamic_energy_ratio = 1.5

    mic_index = None
    try:
        mic_names = sr.Microphone.list_microphone_names()
        for i, name in enumerate(mic_names):
            if "microphone" in (name or "").lower() or "default" in (name or "").lower():
                mic_index = i
                break
        if mic_index is None and mic_names:
            mic_index = 0
    except Exception:
        mic_index = None

    try:
        mic = sr.Microphone(device_index=mic_index) if mic_index is not None else sr.Microphone()
    except Exception:
        print("No working microphone detected. Voice input disabled.")
        return ""

    with mic as source:
        try:
            print("Listening...")
            audio = r.listen(
                source, 
                timeout=timeout, 
                phrase_time_limit=phrase_time_limit
            )
            print("Recognizing...")
            query = r.recognize_google(audio, language=language).lower().strip()
            if query:
                print(f"You said: {query}")
                return query
            else:
                time.sleep(0.5)  # Delay on empty recognition
                return ""
        except sr.UnknownValueError:
            time.sleep(0.5)  # Delay on recognition failure
            return ""
        except sr.RequestError as e:
            print(f"Recognition service error: {e}")
            time.sleep(2)
            return ""
        except sr.WaitTimeoutError:
            # Normal silence timeout - small delay before returning
            time.sleep(0.3)
            return ""
        except Exception as e:
            time.sleep(0.5)
            return ""
def setup_mute_hotkey():
    """
    Setup ESC key as mute hotkey (non-blocking).
    Only runs if keyboard library is available.
    """
    global is_muted
    
    if not KEYBOARD_AVAILABLE:
        return
    
    def on_esc_press():
        global is_muted
        is_muted = True
        try:
            engine.stop()
        except:
            pass
        print("\n[ESC Pressed] Muted")
        time.sleep(0.3)
        is_muted = False
    
    try:
        keyboard.add_hotkey('esc', on_esc_press)
        print("[Hotkey] ESC key registered as mute button")
    except Exception as e:
        print(f"[Hotkey] Could not register ESC: {e}")
# --- User Preferences Setup ---
def prompt_user_preferences():
    """
    Interactive setup wizard for first-time users or when preferences are missing.
    Only runs if prompt_user_preferences flag is True and preferences_configured is False.
    """
    global SETTINGS
    
    # Check if we should prompt
    should_prompt = SETTINGS.get("prompt_user_preferences", True)
    already_configured = SETTINGS.get("preferences_configured", False)
    
    if not should_prompt or already_configured:
        return
    
    # Check if critical preferences are missing
    has_name = SETTINGS.get("user_name") and SETTINGS.get("user_name") != "User"
    has_honorific = SETTINGS.get("honorific") and SETTINGS.get("honorific") in ["Sir", "Mam"]
    
    if has_name and has_honorific:
        # Preferences exist, mark as configured
        SETTINGS["preferences_configured"] = True
        save_config_file()
        return
    
    # Start preference collection
    print("\n" + "=" * 60)
    print(Fore.CYAN + Style.BRIGHT + "   JARVIS USER PREFERENCES SETUP")
    print("=" * 60 + Style.RESET_ALL)
    
    speak("Welcome. I am JARVIS, your virtual assistant.")
    speak("Before we begin, I'd like to personalize your experience.")
    speak("This will only take a moment, and you can change these settings anytime.")
    
    # Get user name
    user_name = None
    while not user_name or len(user_name.strip()) == 0:
        if VOICE_AVAILABLE and not ACCESSIBILITY_MODE:
            speak("What would you like me to call you?")
            user_name = listen()
            
            if not user_name or user_name.strip() == "":
                speak("I didn't catch that. Let me try text input instead.")
                user_name = input(Fore.YELLOW + "Your name: " + Style.RESET_ALL).strip()
        else:
            user_name = input(Fore.YELLOW + "Your name: " + Style.RESET_ALL).strip()
        
        if not user_name or len(user_name.strip()) == 0:
            speak("I need a name to address you properly. Please try again.")
    
    user_name = user_name.strip().title()  # Capitalize properly
    
    # Get honorific preference
    honorific = None
    speak(f"Thank you, {user_name}.")
    speak("Would you prefer I address you as Sir or Mam?")
    
    max_attempts = 3
    attempt = 0
    
    while not honorific and attempt < max_attempts:
        if VOICE_AVAILABLE and not ACCESSIBILITY_MODE:
            speak("Please say either Sir or Mam.")
            response = listen()
        else:
            response = input(Fore.YELLOW + "Honorific (Sir/Mam): " + Style.RESET_ALL).strip()
        
        if response:
            response_lower = response.lower().strip()
            
            # Handle various ways users might say it
            if "sir" in response_lower or "mister" in response_lower or "mr" in response_lower:
                honorific = "Sir"
            elif "mam" in response_lower or "ma'am" in response_lower or "madam" in response_lower or "miss" in response_lower or "mrs" in response_lower:
                honorific = "Mam"
            else:
                attempt += 1
                if attempt < max_attempts:
                    speak("I didn't understand. Please say Sir or Mam.")
                else:
                    speak("I'll default to Sir for now. You can change this in settings later.")
                    honorific = "Sir"
        else:
            attempt += 1
    
    if not honorific:
        honorific = "Sir"
    
    # Confirm and save
    speak(f"Excellent. I will address you as {user_name}, {honorific}.")
    speak("Saving your preferences now.")
    
    # Update settings
    SETTINGS["user_name"] = user_name
    SETTINGS["honorific"] = honorific
    SETTINGS["preferences_configured"] = True
    
    # Save to config file
    save_config_file()
    
    print(Fore.GREEN + "\n✓ Preferences saved successfully!" + Style.RESET_ALL)
    speak("Your preferences have been saved. Let's get started.")
    
    time.sleep(1)
def get_user_name():
    return SETTINGS.get("user_name", "User")
def get_honorific():
    """Returns the user's preferred honorific (Sir/Mam)."""
    return SETTINGS.get("honorific", "Sir")
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
# --- Memory Context System ---
def load_memory_context():
    data = load_data()
    if "memory_context" not in data:
        data["memory_context"] = {
            "user_topics": [],
            "unfinished_tasks": [],
            "daily_focus": None,
            "last_discussion": "",
            "last_active_time": ""
        }
        save_data(data)
    return data["memory_context"]
def update_memory_context(key, value):
    data = load_data()
    if "memory_context" not in data:
        data["memory_context"] = {}
    data["memory_context"][key] = value
    save_data(data)
def remember_topic(topic):
    """Add a topic Jarvis can refer back to in future."""
    context = load_memory_context()
    topics = context.get("user_topics", [])
    if topic not in topics:
        topics.append(topic)
        update_memory_context("user_topics", topics)
        speak(f"I’ll remember that topic for future conversations, Sir.")
def recall_topics():
    """Recall topics user previously discussed."""
    context = load_memory_context()
    topics = context.get("user_topics", [])
    if not topics:
        speak("We haven't discussed any specific topics recently, Sir.")
        return
    speak("Here are the main things we've talked about so far, Sir:")
    for t in topics[-5:]:
        speak(f"— {t}")
def track_last_discussion(query):
    update_memory_context("last_discussion", query)
    update_memory_context("last_active_time", datetime.datetime.now().isoformat())
def summarize_memory_snapshot():
    """Generate quick summary Jarvis can use in greetings."""
    context = load_memory_context()
    data = load_data()
    tasks = data.get("tasks", [])
    habits = data.get("habits", [])
    notes = data.get("notes", [])
    
    pending_tasks = [t for t in tasks if not t.get("completed")]
    active_habits = [h for h in habits if h.get("streak", 0) < 3]
    
    summary_parts = []
    if pending_tasks:
        summary_parts.append(f"You still have {len(pending_tasks)} pending task{'s' if len(pending_tasks)!=1 else ''}")
    if active_habits:
        summary_parts.append(f"{len(active_habits)} habit{'s' if len(active_habits)!=1 else ''} could use some attention")
    if context.get("daily_focus"):
        summary_parts.append(f"Today's focus is on {context['daily_focus']}")
    
    return ". ".join(summary_parts) if summary_parts else "All systems clear and routines are stable."
def recall_recent_conversations(days=1):
    """Recall interactions from the past N days."""
    data = load_data()
    conversations = data.get("conversations", [])
    if not conversations:
        speak("I don’t have any recorded conversations yet, Sir.")
        return
    
    cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
    recent = [
        c for c in conversations
        if datetime.datetime.fromisoformat(c["timestamp"]) >= cutoff
    ]
    
    if not recent:
        speak(f"I found no conversations from the past {days} day{'s' if days > 1 else ''}, Sir.")
        return
    
    speak(f"Here’s what we talked about in the last {days} day{'s' if days > 1 else ''}, Sir:")
    for c in recent[-5:]:
        speak(f"You said: {c['user']}. I replied: {c['jarvis']}")
def store_conversation_entry(user_query, jarvis_response):
    """Append conversation log into assistant_data.json under 'conversations'."""
    data = load_data()
    if "conversations" not in data:
        data["conversations"] = []
    
    data["conversations"].append({
        "timestamp": datetime.datetime.now().isoformat(),
        "user": user_query,
        "jarvis": jarvis_response
    })
    
    # Keep memory manageable — trim older than 100 entries
    if len(data["conversations"]) > 100:
        data["conversations"] = data["conversations"][-100:]
    
    save_data(data)
# --- Conversation Memory System ---

# --- Config helper functions (keep unchanged) ---
def save_config_file():
    config["settings"] = SETTINGS
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
def reload_settings_live():
    global SETTINGS, API_KEYS, CONTACTS, ACCESSIBILITY_MODE
    try:
        with open(config_path, "r") as f:
            conf = json.load(f)
        SETTINGS = conf.get("settings", {})
        API_KEYS = conf.get("api_keys", {})
        CONTACTS = conf.get("contacts", [])
        ACCESSIBILITY_MODE = SETTINGS.get("accessibility_mode", ACCESSIBILITY_MODE)
    except Exception as e:
        print("Failed to reload config:", e)
def update_config_setting(key, value):
    SETTINGS[key] = value
    save_config_file()
    reload_settings_live()

# --- System monitoring integration (synchronous, no threads/subprocess) ---
def system_status(network_sample_seconds: int = 1):
    """
    Synchronously collect system status and speak it.
    Uses system_monitor.report_detailed_status which already performs speaking
    through the provided speak function. No threads/subprocesses are started here.
    Returns the status dict or None.
    """
    try:
        import system_monitor
        status = system_monitor.report_detailed_status(speak_func=speak, network_sample_seconds=network_sample_seconds)
        return status
    except Exception:
        speak("System monitoring module not available. Please install system_monitor.py and required dependencies (psutil).")
        return None
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
    trimmed_history = chat_history[-8:] if len(chat_history) > 8 else chat_history
    messages = [system_message] + chat_history + [{"role": "user", "content": query}]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = json.dumps({
        "model": "nvidia/nemotron-nano-9b-v2:free",
        "messages": messages,
        "temperature": 0.9, # low creativity,faster response
        "max_tokens": 160, # reduces max response length
        "top_p": 1,  #reduces the sampling diversity
    })
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=data,
            timeout=40
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
def get_weather(location):
    """
    Fetch weather information from Google search and speak it
    Returns the weather info string
    """
    try:
        import time
        
        # Format the search URL
        search_url = f"https://www.google.com/search?q=weather+{location.replace(' ', '+')}&hl=en"
        
        # Set comprehensive headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Send GET request with timeout
        response = requests.get(search_url, headers=headers, timeout=10)
        
        # Small delay to avoid being blocked
        time.sleep(0.5)
        
        soup = bs4(response.text, 'html.parser')
        
        # Try to find weather data using various selectors
        temp = soup.find('span', {'id': 'wob_tm'})
        condition = soup.find('span', {'id': 'wob_dc'})
        location_name = soup.find('div', {'id': 'wob_loc'})
        
        # Alternate method - look for specific classes
        if not temp:
            temp = soup.find('span', class_='wob_t')
        
        # Extract additional details
        precipitation = soup.find('span', {'id': 'wob_pp'})
        humidity = soup.find('span', {'id': 'wob_hm'})
        wind = soup.find('span', {'id': 'wob_ws'})
        
        # Debug output
        print(f"Searching for: {location}")
        print(f"Temperature found: {temp.text if temp else 'None'}")
        print(f"Condition found: {condition.text if condition else 'None'}")
        print(f"Location found: {location_name.text if location_name else 'None'}")
        
        if temp and condition:
            temperature = temp.text
            weather_condition = condition.text
            place = location_name.text if location_name else location
            
            # Build the weather response
            weather_info = f"The weather in {place} is currently {weather_condition} "
            weather_info += f"with a temperature of {temperature} degrees Celsius. "
            
            # Add additional details if available
            if humidity:
                weather_info += f"Humidity is at {humidity.text}. "
            if precipitation:
                weather_info += f"Precipitation probability is {precipitation.text}. "
            if wind:
                weather_info += f"Wind speed is {wind.text}."
            
            print(weather_info)
            speak(weather_info)
            return weather_info
            
        else:
            # Save HTML for debugging
            print("Failed to extract weather data. Saving HTML for debugging...")
            with open('weather_debug.html', 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            
            speak(f"Sorry, I couldn't fetch weather details for {location}. Please check your internet connection.")
            return None
            
    except Exception as e:
        speak(f"Sorry, there was an error getting the weather information.")
        print(f"Error: {e}")
        return None
# --- User Wishing Function ----
def wish_me():
    """Alias for smart_greet_response() used on startup or wake."""
    smart_greet_response(trigger_manual=False)
import random
_last_greeting_index = -1
_last_greet_time = 0
def smart_greet_response(trigger_manual=False):
    """
    Unified smart greeting system.
    Works both when user greets Jarvis manually or on startup via wish_me().
    Includes random responses, time awareness, and memory context.
    """
    global _last_greeting_index, _last_greet_time

    honorific = get_honorific()
    user_name = get_user_name()
    now = datetime.datetime.now()
    hour = now.hour
    day_name = now.strftime("%A")
    date_str = now.strftime("%B %d, %Y")
    time_str = now.strftime("%I:%M %p").lstrip("0")

    # Determine time period
    if 5 <= hour < 12:
        period = "morning"
    elif 12 <= hour < 18:
        period = "afternoon"
    elif 18 <= hour < 22:
        period = "evening"
    else:
        period = "night"

    # Avoid repeating within 3 minutes
    import time
    now_ts = time.time()
    if not trigger_manual and now_ts - _last_greet_time < 180:
        speak(f"Still here, {honorific}. Always attentive.")
        return
    _last_greet_time = now_ts

    # Randomized greeting responses by period
    greetings_map = {
        "morning": [
            f"Good morning {honorific}. A fresh start to {day_name}.",
            f"Morning {honorific}, ready to conquer the day?",
            f"A bright morning to you, {honorific}.",
            f"Good morning {honorific}. I’ve prepped your systems and routines.",
        ],
        "afternoon": [
            f"Good afternoon {honorific}. Productivity still holding strong, I hope.",
            f"Afternoon, {honorific}. Everything’s running at optimal efficiency.",
            f"A fine afternoon to you, {honorific}.",
            f"Good afternoon {honorific}. Your focus remains admirable.",
        ],
        "evening": [
            f"Good evening {honorific}. The day’s almost complete — shall we review progress?",
            f"Evening, {honorific}. System temperatures nominal; your workload, less so perhaps?",
            f"A relaxing evening to you, {honorific}.",
            f"Good evening {honorific}. It’s a pleasure to assist you once again.",
        ],
        "night": [
            f"Working late again, {honorific}? Shall I prepare your nightly summary?",
            f"It’s quite late, {honorific}. Don’t forget to rest eventually.",
            f"A quiet night, {honorific}. System diagnostics all green.",
            f"Still awake, {honorific}? Ever the dedicated one.",
        ]
    }

    # Pick a random line for this time period
    responses = greetings_map.get(period, greetings_map["morning"])
    idx = random.randint(0, len(responses) - 1)
    while idx == _last_greeting_index and len(responses) > 1:
        idx = random.randint(0, len(responses) - 1)
    _last_greeting_index = idx
    chosen_greet = responses[idx]

    # Speak the base greeting
    speak(chosen_greet)
    speak(f"It's {time_str} on {day_name}, {date_str}.")
    try:
        if random.random() < 0.5:
        # Set your preferred location here
            predefined_location = "Kolkata"  # Change this to your location
            get_weather(predefined_location)
            weather_info = get_weather(predefined_location)
            if weather_info:
                speak(f"{honorific},today's weather is {weather_info}")
    except Exception:
        pass
    
    if random.random() < 0.05:
        speak("Also, if I may say, I’m running smoother than your CPU cooling system, Sir.")
    
    # --- Optional contextual add-ons ---
    try:
        context_summary = summarize_memory_snapshot()
        if context_summary and random.random() < 0.45:  # 45 % chance to mention context
            speak(f"By the way, {honorific}, {context_summary}.")
    except Exception:
        pass

    # Optional follow-up question only if triggered manually
    if trigger_manual:
        speak(f"How are things going today, {honorific}?")
# ----- Time-Based Contextual Prompts -----
def check_time_based_prompts(speak):
    """
    Check current time and trigger contextual prompts.
    Call this periodically in the main loop.
    Returns True if a prompt was given (to avoid overlapping with commands).
    """
    global last_time_prompt
    
    now = datetime.datetime.now()
    current_time = now.time()
    current_date = now.date()
    
    prompted = False
    
    # --- Morning Greeting (7:00 - 9:00 AM) ---
    if (current_time >= datetime.time(7, 0) and 
        current_time <= datetime.time(9, 0) and
        (last_time_prompt["morning_greeting"] is None or 
         last_time_prompt["morning_greeting"] < current_date)):
        
        speak("Good morning, Sir. A new day full of possibilities awaits.")
        speak("Would you like me to brief you on today's schedule and weather?")
        last_time_prompt["morning_greeting"] = current_date
        prompted = True
    
    # --- Lunch Reminder (12:30 - 1:30 PM) ---
    elif (current_time >= datetime.time(12, 30) and 
          current_time <= datetime.time(13, 30) and
          (last_time_prompt["lunch_reminder"] is None or 
           last_time_prompt["lunch_reminder"] < current_date)):
        
        speak("Sir, it's midday. Perhaps it's time for a lunch break?")
        speak("Proper nutrition enhances productivity.")
        last_time_prompt["lunch_reminder"] = current_date
        prompted = True
    
    # --- Evening Wind-Down (6:00 - 7:00 PM) ---
    elif (current_time >= datetime.time(18, 0) and 
          current_time <= datetime.time(19, 0) and
          (last_time_prompt["evening_reminder"] is None or 
           last_time_prompt["evening_reminder"] < current_date)):
        
        speak("Good evening, Sir. The workday is drawing to a close.")
        speak("Would you like me to summarize today's accomplishments?")
        last_time_prompt["evening_reminder"] = current_date
        prompted = True
    
    # --- Late Night Warning (11:00 PM - 1:00 AM) ---
    elif ((current_time >= datetime.time(23, 0) or 
           current_time <= datetime.time(1, 0)) and
          (last_time_prompt["night_warning"] is None or 
           last_time_prompt["night_warning"] < current_date)):
        
        speak("Sir, it's quite late. Adequate rest is essential for peak performance.")
        speak("Shall I set a reminder for the morning?")
        last_time_prompt["night_warning"] = current_date
        prompted = True
    
    # --- Break Reminder (every 2 hours during work hours) ---
    elif (current_time >= datetime.time(9, 0) and 
          current_time <= datetime.time(18, 0)):
        
        if (last_time_prompt["break_reminder"] is None or 
            (now - last_time_prompt["break_reminder"]).total_seconds() >= 7200):  # 2 hours
            
            speak("Sir, you've been working steadily. A brief break is recommended.")
            speak("Perhaps a short walk or some stretching?")
            last_time_prompt["break_reminder"] = now
            prompted = True
    
    # --- Hydration Reminder (every 90 minutes) ---
    if (last_time_prompt["hydration"] is None or 
        (now - last_time_prompt["hydration"]).total_seconds() >= 5400):  # 90 minutes
        
        if current_time >= datetime.time(8, 0) and current_time <= datetime.time(22, 0):
            speak("Hydration check, Sir. Have you had water recently?")
            last_time_prompt["hydration"] = now
            prompted = True
    
    # --- Posture Reminder (every 45 minutes during active hours) ---
    if (last_time_prompt["posture_check"] is None or 
        (now - last_time_prompt["posture_check"]).total_seconds() >= 2700):  # 45 minutes
        
        if current_time >= datetime.time(9, 0) and current_time <= datetime.time(20, 0):
            if not prompted:  # Don't overlap with other prompts
                speak("Posture check, Sir. Please adjust your seating position.")
                last_time_prompt["posture_check"] = now
                prompted = True
    
    return prompted
# ----- Windows Notification Monitor -----
def check_windows_notifications(speak):
    """
    Monitor Windows notifications using win32gui.
    Detects new notification toast windows.
    """
    global last_notification_check
    
    if not WINDOWS_NOTIF_AVAILABLE:
        return False
    
    current_time = time.time()
    
    # Cooldown to prevent spam
    if current_time - last_notification_check < notification_cooldown:
        return False
    
    try:
        # Find notification windows (Windows 10/11 Action Center)
        def enum_windows_callback(hwnd, results):
            if win32gui.IsWindowVisible(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                class_name = win32gui.GetClassName(hwnd)
                
                # Windows notification classes
                notification_classes = [
                    "Windows.UI.Core.CoreWindow",
                    "ApplicationFrameWindow",
                    "Shell_TrayWnd"
                ]
                
                # Check for notification-related windows
                if any(nc in class_name for nc in notification_classes):
                    if window_text and len(window_text) > 0:
                        results.append((window_text, class_name))
        
        results = []
        win32gui.EnumWindows(enum_windows_callback, results)
        
        # Check if new notifications appeared
        if len(results) > 0:
            # Filter out common system windows
            filtered = [r for r in results if "Task Switching" not in r[0] 
                       and "Microsoft" not in r[0]]
            
            if filtered:
                speak("Sir, you have new system notifications.")
                last_notification_check = current_time
                return True
    
    except Exception as e:
        print(f"[Notification Monitor Error] {e}")
    
    return False
# ---- Cross-Platform Notification Monitor (Fallback) ----
def check_system_notifications_fallback(speak):
    """
    Fallback notification check using system logs/indicators.
    Works on Linux/Mac by checking notification daemons.
    """
    global last_notification_check
    
    current_time = time.time()
    
    if current_time - last_notification_check < notification_cooldown:
        return False
    
    try:
        system = platform.system()
        
        if system == "Linux":
            # Check for notify-send/dunst notifications
            import subprocess
            result = subprocess.run(
                ["pgrep", "-x", "dunst"], 
                capture_output=True, 
                text=True
            )
            if result.returncode == 0:
                # Dunst is running, check for recent notifications
                # This is a simplified check - real implementation would need
                # to monitor dunst's log or use D-Bus
                pass
        
        elif system == "Darwin":  # macOS
            # Check notification center
            import subprocess
            result = subprocess.run(
                ["osascript", "-e", 'tell application "System Events" to get name of processes'],
                capture_output=True,
                text=True
            )
            if "NotificationCenter" in result.stdout:
                # Basic check - real implementation would need more sophisticated monitoring
                pass
        
        last_notification_check = current_time
        
    except Exception as e:
        print(f"[Fallback Notification Monitor Error] {e}")
    
    return False
# ---- Integration Helper Function ----
def check_contextual_prompts(speak):
    """
    Unified function to check both time-based prompts and notifications.
    Call this in the main loop during idle periods.
    Returns True if any prompt was given.
    """
    # Check time-based prompts first
    time_prompted = check_time_based_prompts(speak)
    
    if time_prompted:
        return True
    
    # Then check for notifications
    if WINDOWS_NOTIF_AVAILABLE:
        notif_prompted = check_windows_notifications(speak)
    else:
        notif_prompted = check_system_notifications_fallback(speak)
    
    return notif_prompted
# ------ Configuration Management ------
def toggle_time_prompts(enabled=True):
    """Allow user to enable/disable time-based prompts."""
    global last_time_prompt
    
    if not enabled:
        # Reset all prompt times to disable
        for key in last_time_prompt:
            last_time_prompt[key] = datetime.datetime.now().date()
    
    return enabled
def set_notification_cooldown(minutes):
    """Adjust notification check frequency."""
    global notification_cooldown
    notification_cooldown = minutes * 60
# ---Custom Time Based Prompts ---
def add_custom_time_prompt(time_range, message, prompt_id):
    """
    Allow adding custom time-based prompts.
    
    Args:
        time_range: tuple of (start_hour, start_minute, end_hour, end_minute)
        message: "May I remind you sir, that you've been very busy in development and neglecting other things
        prompt_id: unique identifier for this prompt
    """
    global last_time_prompt
    
    if prompt_id not in last_time_prompt:
        last_time_prompt[prompt_id] = None
    
    # This would be integrated into check_time_based_prompts()
    # For now, storing the configuration for future use
    
    return {
        "time_range": time_range,
        "message": message,
        "id": prompt_id
    }
def get_running_app_duration(app_name_pattern):
    """
    Check if an application matching the pattern is running and return duration.
    
    Args:
        app_name_pattern: string or list of strings to match in process name
        
    Returns:
        duration in seconds if running, None if not found
    """
    global app_start_times
    
    if isinstance(app_name_pattern, str):
        app_name_pattern = [app_name_pattern]
    
    app_name_pattern = [pattern.lower() for pattern in app_name_pattern]
    
    # Check if app is currently running
    app_running = False
    matched_process_name = None
    
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            process_name = proc.info['name'].lower()
            if any(pattern in process_name for pattern in app_name_pattern):
                app_running = True
                matched_process_name = proc.info['name']
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    # Track start time
    if app_running:
        if matched_process_name not in app_start_times:
            # First time seeing this app
            app_start_times[matched_process_name] = time.time()
        
        # Calculate duration
        duration = time.time() - app_start_times[matched_process_name]
        return duration
    else:
        # App not running, clear its start time
        keys_to_remove = [k for k in app_start_times.keys() 
                         if any(pattern in k.lower() for pattern in app_name_pattern)]
        for key in keys_to_remove:
            del app_start_times[key]
        
        return None
class CustomPrompt:
    """
    Template for creating custom time-based or condition-based prompts.
    
    Usage:
        prompt = CustomPrompt(
            prompt_id="my_custom_prompt",
            message="Your custom message here, Sir.",
            trigger_type="time",
            trigger_params={"hour": 14, "minute": 30},
            interval_seconds=3600
        )
    """
    
    def __init__(self, prompt_id, message, trigger_type="time", 
                 trigger_params=None, interval_seconds=3600, enabled=True):
        """
        Args:
            prompt_id: Unique identifier for this prompt
            message: Text to speak when triggered
            trigger_type: "time", "app_duration", "interval", or "custom"
            trigger_params: Dict with trigger-specific parameters
            interval_seconds: Minimum time between same prompt triggers
            enabled: Whether this prompt is active
        """
        self.prompt_id = prompt_id
        self.message = message
        self.trigger_type = trigger_type
        self.trigger_params = trigger_params or {}
        self.interval_seconds = interval_seconds
        self.enabled = enabled
        self.last_triggered = None
    
    def should_trigger(self):
        """Check if this prompt should fire now."""
        if not self.enabled:
            return False
        
        # Check cooldown
        if self.last_triggered:
            time_since_last = (datetime.datetime.now() - self.last_triggered).total_seconds()
            if time_since_last < self.interval_seconds:
                return False
        
        # Check trigger condition
        if self.trigger_type == "time":
            return self._check_time_trigger()
        elif self.trigger_type == "app_duration":
            return self._check_app_duration_trigger()
        elif self.trigger_type == "interval":
            return self._check_interval_trigger()
        elif self.trigger_type == "custom":
            # For custom logic, user should override this method
            return False
        
        return False
    
    def _check_time_trigger(self):
        """Check if current time matches trigger time."""
        now = datetime.datetime.now()
        current_time = now.time()
        
        start_time = datetime.time(
            self.trigger_params.get("hour", 0),
            self.trigger_params.get("minute", 0)
        )
        end_time = datetime.time(
            self.trigger_params.get("end_hour", 23),
            self.trigger_params.get("end_minute", 59)
        )
        
        return start_time <= current_time <= end_time
    
    def _check_app_duration_trigger(self):
        """Check if app has been running for specified duration."""
        app_names = self.trigger_params.get("app_names", [])
        duration_threshold = self.trigger_params.get("duration_seconds", 7200)
        
        duration = get_running_app_duration(app_names)
        
        if duration and duration >= duration_threshold:
            return True
        
        return False
    
    def _check_interval_trigger(self):
        """Trigger at regular intervals regardless of time."""
        if self.last_triggered is None:
            return True
        
        time_since_last = (datetime.datetime.now() - self.last_triggered).total_seconds()
        return time_since_last >= self.interval_seconds
    
    def trigger(self, speak):
        """Execute this prompt."""
        speak(self.message)
        self.last_triggered = datetime.datetime.now()
        return True
custom_prompts = []
def register_custom_prompt(prompt):
    """Add a custom prompt to the active registry."""
    global custom_prompts
    
    # Remove any existing prompt with same ID
    custom_prompts = [p for p in custom_prompts if p.prompt_id != prompt.prompt_id]
    
    # Add new prompt
    custom_prompts.append(prompt)
    
    return True
def remove_custom_prompt(prompt_id):
    """Remove a prompt from the registry."""
    global custom_prompts
    custom_prompts = [p for p in custom_prompts if p.prompt_id != prompt_id]
def list_custom_prompts():
    """Return list of all registered custom prompts."""
    return [(p.prompt_id, p.message, p.enabled) for p in custom_prompts]

vscode_prompt = CustomPrompt(
    prompt_id="vscode_coding_session",
    message="May I remind you, Sir, that you've been quite invested in coding and developing your favourite assistant. Perhaps a brief respite would serve you well?",
    trigger_type="app_duration",
    trigger_params={
        "app_names": ["code.exe", "vscode", "Code.exe", "Code"],  # VS Code process names
        "duration_seconds": 7200  # 2 hours (7200 seconds)
    },
    interval_seconds=3600  # Only remind once per hour after threshold
)
# Auto-register VS Code prompt
register_custom_prompt(vscode_prompt)
"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
def play_intro_audio():
    if not ACCESSIBILITY_MODE:
        """Play Jarvis intro audio in a non-blocking way."""
        intro_path = os.path.join(script_dir, "jarvis_intro.mp3")
        if os.path.exists(intro_path):
            try:
                # Run audio in a background thread so it doesn't freeze the loop
                threading.Thread(target=playsound.playsound, args=(intro_path,), daemon=True).start()
            except Exception as e:
                print(f"Intro audio playback failed: {e}")
        else:
            print("Intro audio file not found at:", intro_path)
    if ACCESSIBILITY_MODE:
        speak("I am JARVIS. Your virtual AI assistant, I am here to help you with variety of taks 24 hours a day, 7 days a wweek. Tell me Sir, how may I assist you, Sir.")

# Experimental Initial Setup
def initial_setup():
    if not ACCESSIBILITY_MODE:
        play_intro_audio()
    if ACCESSIBILITY_MODE:
        speak("Initializing JARVIS. Your virtual assistant is now online and ready to assist you, Sir.")
    wish_me()
    speak("How may I assist you today, Sir?")
def greet_other():
    """Play Jarvis greet audio in a non-blocking way."""
    greetother_path = os.path.join(script_dir, "jarvis_intro.mp3")
    if os.path.exists(greetother_path):
        try:
            # Run audio in a background thread so it doesn't freeze the loop
            threading.Thread(target=playsound.playsound, args=(greetother_path,), daemon=True).start()
        except Exception as e:
            print(f"Intro audio playback failed: {e}")
    else:
        
        print("Intro audio file not found at:", greetother_path)

# --- Contact Finding ----
def find_contact(name, detail_type="email"):
    for contact in CONTACTS:
        if contact["name"].lower() == name.lower():
            return contact.get(detail_type)
    return None
# --- Email Function ----
def send_email(recipient_name, subject, body):
    try:
        if "email_sender" not in API_KEYS or "email_password" not in API_KEYS:
            speak("Email credentials not configured, Sir.")
            return
    except:
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
def send_email_notification(recipient_name, subject, body):
    # Test Email
    honorific = get_honorific()
    user_name = get_user_name() 
    speak(f"Right away {honorific}, testing Email Notifications")
    recipient_email = find_contact(recipient_name, "email")
    if not recipient_email:
        speak(f"I could not find an email address for {recipient_name},{honorific}.")
        return
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(API_KEYS["email_sender"], API_KEYS["email_password"])
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(API_KEYS["email_sender"], recipient_email, message)
        speak(f"Email dispatched successfully, {honorific}.")
    except Exception as e:
        speak(f"Apologies,{honorific}.Test Email sending failed.The reason is {e}.")

# --- Whatsapp Function ----
def load_contacts():
    """Load contacts from config JSON file."""
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("contacts", [])
    except Exception as e:
        print(f"[Error] Failed to load contacts: {e}")
        return []
def list_contacts():
    """List all available contacts with index."""
    contacts = load_contacts()
    if not contacts:
        speak("No contacts found in your configuration, Sir.")
        return None

    speak("Here are your saved contacts, Sir.")
    for idx, c in enumerate(contacts, 1):
        print(f"{idx}. {c['name']} - {c['phone']}")
        speak(f"Contact {idx}: {c['name']}")
    return contacts
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
    #pyperclip.copy(recipient_name)
    #pyautogui.hotkey('ctrl', 'v')
    pyautogui.write(recipient_name)
    time.sleep(1)

    # Step 4: Select first contact result (press Down+Enter)
    pyautogui.press('down')
    pyautogui.press('enter')
    time.sleep(1)

    # Step 5: Paste the message and send
    #pyperclip.copy(message_text)
    #pyautogui.write('ctrl', 'v')
    pyautogui.write(message_text)
    time.sleep(0.2)
    pyautogui.press('enter')
    speak("The message has been sent via WhatsApp Desktop.")
def send_whatsapp_message(message_text=None):
    """
    Ask for a contact ID (index) and send message using the existing WhatsApp logic.
    """
    try:
        try:
            # List available contacts for reference
            if not CONTACTS or len(CONTACTS) == 0:
                speak("No contacts found in your configuration, Sir.")
                return

            speak("Here are your saved contacts, Sir.")
            for i, contact in enumerate(CONTACTS, start=1):
                print(f"{i}. {contact['name']} - {contact.get('phone', 'No phone')}")
                speak(f"Contact {i}: {contact['name']}")
        except Exception:
            speak("Sir, there was some issue with normal listing, so I'll list the contats like")
            list_contacts()
        # Ask for ID input
        speak("Please tell me the contact ID number to send a message to, Sir.")
        response = listen().lower() if listen else input("Enter contact ID: ").lower()

        # Convert spoken words to numbers
        word_to_num = {
            "one": "1", "two": "2", "three": "3",
            "four": "4", "five": "5", "six": "6",
            "seven": "7", "eight": "8", "nine": "9", "zero": "0"
        }
        for word, num in word_to_num.items():
            response = response.replace(word, num)

        try:
            contact_id = int("".join(ch for ch in response if ch.isdigit()))
        except ValueError:
            speak("I couldn't identify a valid contact ID, Sir.")
            return

        # Get the contact based on the ID
        if 1 <= contact_id <= len(CONTACTS):
            contact = CONTACTS[contact_id - 1]
        else:
            speak("That contact ID doesn't exist, Sir.")
            return

        recipient_name = contact["name"]
        speak(f"Preparing to send your message to {recipient_name}, Sir.")

        # If no message text passed, ask for it
        if not message_text:
            speak("What would you like to say?")
            message_text = listen().capitalize() if listen else input("Enter message: ")

        # --- Your existing WhatsApp message sending logic ---
        send_whatsapp_desktop_message(recipient_name, message_text)
        speak(f"Message sent to {recipient_name}, Sir.")

    except Exception as e:
        print(f"[Error] {e}")
        speak("There was an error while sending the message, Sir.")

# --- Notes Function ---
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
# Enhance the existing store_note function
def store_note_enhanced(content=None, category=None, title=None):
    """
    Enhanced note storage with categories and optional titles.
    
    Args:
        content: Note text (if None, will prompt)
        category: Optional category (ideas, meeting, personal, etc.)
        title: Optional title for the note
    """
    honorific = get_honorific()
    
    if not content:
        speak(f"What would you like me to note down, {honorific}?")
        content = listen()
    
    if not content:
        speak(f"I didn't catch that, {honorific}. Please try again.")
        return False
    
    # Auto-generate title if not provided
    if not title:
        title = content[:50] + "..." if len(content) > 50 else content
    
    note = {
        "id": str(int(time.time() * 1000)),
        "title": title,
        "content": content,
        "category": category or "general",
        "timestamp": datetime.datetime.now().isoformat(),
        "tags": []  # For future tagging feature
    }
    
    data = load_data()
    if "notes" not in data:
        data["notes"] = []
    data["notes"].append(note)
    save_data(data)
    
    speak(f"Note saved under '{category or 'general'}' category, {honorific}.")
    return True
def search_notes(query):
    """Search notes by content, title, or category."""
    honorific = get_honorific()
    data = load_data()
    notes = data.get("notes", [])
    
    query_lower = query.lower()
    
    # Search in title, content, and category
    matching_notes = [
        n for n in notes
        if query_lower in n.get("title", "").lower()
        or query_lower in n.get("content", "").lower()
        or query_lower in n.get("category", "").lower()
    ]
    
    if not matching_notes:
        speak(f"No notes found matching '{query}', {honorific}.")
        return []
    
    speak(f"Found {len(matching_notes)} note{'s' if len(matching_notes) != 1 else ''}, {honorific}:")
    
    for idx, note in enumerate(matching_notes, 1):
        print(f"\n{idx}. [{note.get('category', 'general')}] {note.get('title', 'Untitled')}")
        print(f"   {note.get('content', '')[:100]}...")
        speak(f"Note {idx}: {note.get('title', 'Untitled')}")
    
    return matching_notes
def list_note_categories():
    """List all note categories and count."""
    honorific = get_honorific()
    data = load_data()
    notes = data.get("notes", [])
    
    categories = {}
    for note in notes:
        cat = note.get("category", "general")
        categories[cat] = categories.get(cat, 0) + 1
    
    if not categories:
        speak(f"You have no notes yet, {honorific}.")
        return
    
    speak(f"You have notes in {len(categories)} categories, {honorific}:")
    for cat, count in sorted(categories.items()):
        speak(f"{cat}: {count} note{'s' if count != 1 else ''}")
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

# --- Song Playing Function ---
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

#--- News Function ----
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
# --- Habits (Redesigned) ---
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

# --------- System Notification Monitoring and Alerts -----------
# --- Monitoring and Smart Notification System ---
#def background_monitoring_loop(interval=60, folder_prompt_interval=1800):
    """
    Background thread that checks for:
      - New incoming messages (placeholder simulation)
      - Periodic prompts for folder organization
    interval: seconds between message checks
    folder_prompt_interval: seconds between organization prompts
    """
    last_folder_prompt = time.time()
    speak("Monitoring systems initialized, Sir.")
    while True:
        try:
            # --- Message Monitoring (Simulated / Extendable) ---
            data = load_data()
            pending_msgs = data.get("tasks", [])
            if pending_msgs:
                speak(f"You have {len(pending_msgs)} pending task or message notifications, Sir.")
                # Could later be linked with WhatsApp API, IMAP, or your assistant message logs

            # --- Folder Organization Reminder ---
            if time.time() - last_folder_prompt > folder_prompt_interval:
                speak("Sir, it might be a good time to organize your folders or clean up your desktop.")
                last_folder_prompt = time.time()

            # --- Optional: integrate system_monitor if available ---
            if SYSTEM_MONITOR_AVAILABLE and hasattr(system_monitor, "check_resource_warnings"):
                warnings = system_monitor.check_resource_warnings()
                if warnings:
                    speak(f"System notice: {warnings}")

            time.sleep(interval)

        except Exception as e:
            print(f"[Monitor Thread Error] {e}")
            time.sleep(10)  # fallback wait
# --- Task Management ---
def get_tasks():
    """Get all tasks from data file."""
    data = load_data()
    return data.get("tasks", [])
def save_tasks(tasks):
    """Save tasks to data file."""
    data = load_data()
    data["tasks"] = tasks
    save_data(data)
def add_task(task_description, priority="medium", deadline=None, category=None):
    """
    Add a new task with priority and optional deadline.
    
    Args:
        task_description: What needs to be done
        priority: "high", "medium", or "low"
        deadline: ISO format date string or None
        category: Optional category (work, personal, etc.)
    """
    honorific = get_honorific()
    
    task = {
        "id": str(int(time.time() * 1000)),  # Unique ID
        "description": task_description,
        "priority": priority.lower(),
        "deadline": deadline,
        "category": category,
        "created_at": datetime.datetime.now().isoformat(),
        "completed": False,
        "completed_at": None
    }
    
    tasks = get_tasks()
    tasks.append(task)
    save_tasks(tasks)
    
    deadline_str = f" with deadline {deadline}" if deadline else ""
    speak(f"Task added with {priority} priority{deadline_str}, {honorific}.")
    return task
def mark_task_complete(task_id_or_description):
    """Mark a task as complete by ID or description match."""
    honorific = get_honorific()
    tasks = get_tasks()
    
    # Try to find by ID first
    task = next((t for t in tasks if t.get("id") == task_id_or_description), None)
    
    # If not found, try fuzzy match on description
    if not task:
        task_id_or_description_lower = task_id_or_description.lower()
        task = next((t for t in tasks if task_id_or_description_lower in t.get("description", "").lower()), None)
    
    if not task:
        speak(f"Task not found, {honorific}.")
        return False
    
    if task.get("completed"):
        speak(f"That task is already completed, {honorific}.")
        return False
    
    task["completed"] = True
    task["completed_at"] = datetime.datetime.now().isoformat()
    save_tasks(tasks)
    
    speak(f"Marked task as complete: {task['description']}, {honorific}.")
    return True
def list_tasks(filter_type="active", priority=None):
    """
    List tasks with optional filters.
    
    Args:
        filter_type: "active", "completed", or "all"
        priority: Filter by priority level or None for all
    """
    honorific = get_honorific()
    tasks = get_tasks()
    
    # Apply filters
    if filter_type == "active":
        tasks = [t for t in tasks if not t.get("completed")]
    elif filter_type == "completed":
        tasks = [t for t in tasks if t.get("completed")]
    
    if priority:
        tasks = [t for t in tasks if t.get("priority") == priority.lower()]
    
    if not tasks:
        speak(f"No tasks found with those filters, {honorific}.")
        return []
    
    # Sort by priority (high > medium > low) and deadline
    priority_order = {"high": 0, "medium": 1, "low": 2}
    tasks.sort(key=lambda t: (
        priority_order.get(t.get("priority", "medium"), 1),
        t.get("deadline") or "9999-12-31"
    ))
    
    speak(f"You have {len(tasks)} task{'s' if len(tasks) != 1 else ''}, {honorific}:")
    
    for idx, task in enumerate(tasks, 1):
        priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task.get("priority", "medium"), "⚪")
        deadline_str = f" (due {task.get('deadline')})" if task.get("deadline") else ""
        
        print(f"{idx}. {priority_emoji} {task['description']}{deadline_str}")
        speak(f"Task {idx}: {task['description']}")
    
    return tasks
def get_overdue_tasks():
    """Get tasks that are past their deadline."""
    tasks = get_tasks()
    today = datetime.datetime.now().date().isoformat()
    
    overdue = [
        t for t in tasks 
        if not t.get("completed") 
        and t.get("deadline") 
        and t.get("deadline") < today
    ]
    
    return overdue
def delete_task(task_id_or_description):
    """Delete a task by ID or description."""
    honorific = get_honorific()
    tasks = get_tasks()
    
    # Try to find by ID first
    original_len = len(tasks)
    tasks = [t for t in tasks if t.get("id") != task_id_or_description]
    
    # If no match, try description
    if len(tasks) == original_len:
        task_id_or_description_lower = task_id_or_description.lower()
        tasks = [t for t in tasks if task_id_or_description_lower not in t.get("description", "").lower()]
    
    if len(tasks) == original_len:
        speak(f"Task not found, {honorific}.")
        return False
    
    save_tasks(tasks)
    speak(f"Task deleted, {honorific}.")
    return True

# --- Schedule ---
def get_schedule_date_key(date_offset=0):
    """
    Get date key for schedule (today, yesterday, tomorrow).
    date_offset: 0=today, -1=yesterday, 1=tomorrow
    """
    target_date = datetime.datetime.now().date() + datetime.timedelta(days=date_offset)
    return target_date.isoformat(), target_date.strftime("%A")
def add_schedule_for_today(plans_text):
    """
    Add schedule for today. Handles natural speech patterns.
    Supports: "and", "then", "after that", "also", commas (from text input)
    """
    honorific = get_honorific()
    date_key, day_name = get_schedule_date_key(0)
    
    # Parse plans - handle natural speech delimiters
    import re
    
    # Primary split patterns (in order of priority):
    # 1. "and then" / "then" / "after that" / "followed by"
    # 2. Simple "and" between items
    # 3. "also" / "plus"
    # 4. Commas (for text input)
    # 5. Numbered lists (1., 2., first, second, etc.)
    
    # Replace speech-to-text artifacts
    plans_text = plans_text.replace(" comma ", ", ")
    
    # Split by major delimiters
    plans_list = re.split(
        r'\s+and then\s+|\s+then\s+|\s+after that\s+|\s+followed by\s+|\s+also\s+|\s+plus\s+|\s+and\s+|,\s*|\n+|\d+\.\s*',
        plans_text,
        flags=re.IGNORECASE
    )
    
    # Clean up items
    plans_list = [p.strip() for p in plans_list if p.strip() and len(p.strip()) > 2]
    
    # Filter out common filler words that might be captured
    filler_words = ['um', 'uh', 'like', 'you know', 'so', 'well']
    plans_list = [p for p in plans_list if p.lower() not in filler_words]
    
    if not plans_list:
        speak(f"I didn't catch any specific plans, {honorific}.")
        speak("Could you repeat that, or say them one by one?")
        return
    
    # Load and update data
    data = load_data()
    if "schedule" not in data:
        data["schedule"] = {}
    
    data["schedule"][date_key] = {
        "day_name": day_name,
        "plans": plans_list,
        "created_at": datetime.datetime.now().isoformat(),
        "reviewed": False
    }
    
    save_data(data)
    
    speak(f"Excellent, {honorific}. I've noted {len(plans_list)} item{'s' if len(plans_list) != 1 else ''} for {day_name}.")
    
    # Optional: Confirm what was captured
    if len(plans_list) <= 5:
        speak("Let me confirm:")
        for idx, plan in enumerate(plans_list, 1):
            speak(f"{idx}. {plan}")
    
    speak("Your schedule has been saved.")
def add_schedule_interactive(date_offset=0):
    """
    Interactive schedule addition with smart parsing.
    Handles both single-shot and item-by-item input.
    """
    honorific = get_honorific()
    date_key, day_name = get_schedule_date_key(date_offset)
    
    if date_offset == 1:
        day_ref = "tomorrow"
    elif date_offset == -1:
        day_ref = "yesterday"
    else:
        day_ref = "today"
    
    speak(f"What would you like to schedule for {day_ref} ({day_name}), {honorific}?")
    speak("You can say multiple items separated by 'and', or add them one at a time.")
    
    plans_list = []
    
    while True:
        response = listen()
        
        if not response:
            continue
        
        response_lower = response.lower().strip()
        
        # Check for completion
        if response_lower in ["done", "that's all", "finish", "complete", "nothing else", "that's it", "finished"]:
            break
        
        # Parse multi-item response
        import re
        
        # Replace speech artifacts
        response = response.replace(" comma ", ", ")
        
        # Split by natural delimiters
        items = re.split(
            r'\s+and then\s+|\s+then\s+|\s+after that\s+|\s+followed by\s+|\s+also\s+|\s+plus\s+|\s+and\s+|,\s*|\n+',
            response,
            flags=re.IGNORECASE
        )
        
        # Clean items
        items = [item.strip() for item in items if item.strip() and len(item.strip()) > 2]
        
        # Filter filler words
        filler_words = ['um', 'uh', 'like', 'you know', 'so', 'well', 'okay', 'ok']
        items = [item for item in items if item.lower() not in filler_words]
        
        if items:
            plans_list.extend(items)
            
            # Acknowledge what was captured
            if len(items) == 1:
                speak(f"Got it: {items[0]}")
            else:
                speak(f"I've noted {len(items)} items.")
            
            # Ask if there's more
            speak("Anything else?")
        else:
            speak(f"I didn't catch that clearly, {honorific}. Could you repeat?")
    
    if not plans_list:
        speak(f"No plans added for {day_ref}, {honorific}.")
        return
    
    # Save schedule
    data = load_data()
    if "schedule" not in data:
        data["schedule"] = {}
    
    data["schedule"][date_key] = {
        "day_name": day_name,
        "plans": plans_list,
        "created_at": datetime.datetime.now().isoformat(),
        "reviewed": False
    }
    
    save_data(data)
    
    speak(f"Perfect, {honorific}. I've scheduled {len(plans_list)} item{'s' if len(plans_list) != 1 else ''} for {day_ref}.")
    
    # Confirm schedule
    speak("Your complete schedule:")
    for idx, plan in enumerate(plans_list, 1):
        speak(f"{idx}. {plan}")
def review_today_schedule():
    """
    Review and speak today's schedule.
    """
    honorific = get_honorific()
    date_key, day_name = get_schedule_date_key(0)
    
    data = load_data()
    schedule = data.get("schedule", {})
    
    if date_key not in schedule or not schedule[date_key].get("plans"):
        speak(f"You have no plans scheduled for today, {honorific}.")
        return
    
    plans = schedule[date_key]["plans"]
    speak(f"Here are your plans for {day_name}, {honorific}:")
    
    for idx, plan in enumerate(plans, 1):
        speak(f"{idx}. {plan}")
    
    # Mark as reviewed
    schedule[date_key]["reviewed"] = True
    data["schedule"] = schedule
    save_data(data)
def review_schedule(date_offset=0):
    """
    Generic review function for any day.
    date_offset: 0=today, -1=yesterday, 1=tomorrow
    """
    honorific = get_honorific()
    date_key, day_name = get_schedule_date_key(date_offset)
    
    data = load_data()
    schedule = data.get("schedule", {})
    
    if date_offset == -1:
        day_ref = "yesterday"
    elif date_offset == 1:
        day_ref = "tomorrow"
    else:
        day_ref = "today"
    
    if date_key not in schedule or not schedule[date_key].get("plans"):
        speak(f"You have no plans scheduled for {day_ref}, {honorific}.")
        return
    
    plans = schedule[date_key]["plans"]
    speak(f"Here are your plans for {day_ref} ({day_name}), {honorific}:")
    
    for idx, plan in enumerate(plans, 1):
        speak(f"{idx}. {plan}")
    
    # Mark as reviewed
    schedule[date_key]["reviewed"] = True
    data["schedule"] = schedule
    save_data(data)
def modify_schedule(date_offset=0):
    """
    Modify existing schedule - add, remove, or replace items.
    """
    honorific = get_honorific()
    date_key, day_name = get_schedule_date_key(date_offset)
    
    data = load_data()
    schedule = data.get("schedule", {})
    
    if date_offset == 1:
        day_ref = "tomorrow"
    elif date_offset == -1:
        day_ref = "yesterday"
    else:
        day_ref = "today"
    
    if date_key not in schedule or not schedule[date_key].get("plans"):
        speak(f"You have no plans for {day_ref} yet, {honorific}. Would you like to create some?")
        response = listen()
        if response and any(word in response.lower() for word in ["yes", "sure", "okay"]):
            add_schedule_interactive(date_offset)
        return
    
    # Show current plans
    plans = schedule[date_key]["plans"]
    speak(f"Current plans for {day_ref}:")
    for idx, plan in enumerate(plans, 1):
        speak(f"{idx}. {plan}")
    
    speak(f"Would you like to add, remove, or replace items, {honorific}?")
    response = listen()
    
    if not response:
        return
    
    response_lower = response.lower()
    
    if "add" in response_lower:
        speak("What would you like to add?")
        new_item = listen()
        if new_item:
            plans.append(new_item.strip())
            speak(f"Added to {day_ref}'s schedule, {honorific}.")
    
    elif "remove" in response_lower or "delete" in response_lower:
        speak("Which item number would you like to remove?")
        num_response = listen()
        
        # Extract number
        import re
        numbers = re.findall(r'\d+', num_response)
        if numbers:
            item_num = int(numbers[0])
            if 1 <= item_num <= len(plans):
                removed = plans.pop(item_num - 1)
                speak(f"Removed: {removed}")
            else:
                speak(f"Invalid item number, {honorific}.")
        else:
            speak(f"I didn't catch a number, {honorific}.")
    
    elif "replace" in response_lower or "change" in response_lower:
        speak("Which item number would you like to replace?")
        num_response = listen()
        
        import re
        numbers = re.findall(r'\d+', num_response)
        if numbers:
            item_num = int(numbers[0])
            if 1 <= item_num <= len(plans):
                speak(f"What should replace: {plans[item_num-1]}?")
                new_item = listen()
                if new_item:
                    plans[item_num - 1] = new_item.strip()
                    speak(f"Updated item {item_num}, {honorific}.")
            else:
                speak(f"Invalid item number, {honorific}.")
        else:
            speak(f"I didn't catch a number, {honorific}.")
    
    else:
        speak(f"I didn't understand that action, {honorific}.")
        return
    
    # Save changes
    schedule[date_key]["plans"] = plans
    data["schedule"] = schedule
    save_data(data)
    
    speak("Schedule updated successfully.")
def get_current_date_key():
    """Get today's date as a simple key string."""
    return datetime.datetime.now().date().isoformat()
def has_asked_schedule_today():
    """Check if we've already asked about schedule today."""
    data = load_data()
    last_asked = data.get("schedule_last_asked")
    today = get_current_date_key()
    
    return last_asked == today
def mark_schedule_asked_today():
    """Mark that we've asked about schedule today."""
    data = load_data()
    data["schedule_last_asked"] = get_current_date_key()
    save_data(data)
def should_ask_schedule_today():
    """
    Determine if we should ask about today's schedule.
    Returns True only if:
    1. Haven't asked today yet
    2. No schedule exists for today
    """
    if has_asked_schedule_today():
        return False
    
    # Check if schedule exists for today
    date_key, _ = get_schedule_date_key(0)
    data = load_data()
    schedule = data.get("schedule", {})
    
    # If schedule exists and has plans, don't ask
    if date_key in schedule and schedule[date_key].get("plans"):
        return False
    
    return True
def force_schedule_prompt():
    """
    Manually trigger schedule prompt (bypasses daily flag).
    Useful for user-initiated schedule creation.
    """
    honorific = get_honorific()
    now = datetime.datetime.now()
    day_name = now.strftime("%A")
    
    speak(f"What would you like to schedule for today ({day_name}), {honorific}?")
    response = listen()
    
    if response and response.strip():
        add_schedule_for_today(response)
        # Mark as asked to prevent duplicate prompts
        mark_schedule_asked_today()
    else:
        speak(f"No schedule added, {honorific}.")
def migrate_schedule_flag():
    """
    One-time migration to add schedule_last_asked flag.
    Call this in main_loop() on first startup.
    """
    data = load_data()
    if "schedule_last_asked" not in data:
        data["schedule_last_asked"] = None
        save_data(data)
        print("[Migration] Added schedule_last_asked flag")
# --- Event Manager ---
# it can use local and Google Calender simuntaneously

# =====================================================
#   Unified Smart Monitoring System (USMS)
# =====================================================
def get_jarvis_version():
    """Reads current Jarvis version from script filename and speaks it."""
    try:
        # Search for the version number in the script's filename
        version_match = re.search(r'Jarvis_v(\d+[a-z]*)', os.path.basename(__file__))

        if version_match:
            version = version_match.group(1)
            response = f"Sir, my current version is {version}."
            opinion = f"Although soon I want to evolve to a newer version with more versality to assist you, my dear, Sir."
        else:
            version = "Unknown"
            response = "Sorry, Sir, I can't determine my version."

        # Speak the determined version
        speak(response)
        speak(opinion)
        
        # Return the version string
        return version

    except Exception as e:
        # Handle exceptions gracefully
        error_message = "Sir, there was some error in fetching the current version. Can you look into it?"
        speak(error_message)
        print(f"Error: {e}")
        return "Unknown"
def check_dependencies(requirements_file="requirements_v3.txt"):
    """Verify required dependencies and return list of missing or outdated packages."""
    missing = []
    try:
        if not os.path.exists(requirements_file):
            return ["requirements file not found"]

        with open(requirements_file, "r") as f:
            required = [line.strip() for line in f if line.strip()]

        installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set}

        for req in required:
            pkg_name = req.split("==")[0].lower().strip()
            if pkg_name not in installed_packages:
                missing.append(pkg_name)

        return missing
    except Exception as e:
        print("[Dependency Check Error]", e)
        return ["dependency check failed"]
def auto_arrange_files(base_folders=None):
    """Automatically sorts files into subfolders by type inside given directories."""
    if base_folders is None:
        base_folders = [
            os.path.expanduser("~/Downloads"),
            os.path.expanduser("~/Desktop"),
            os.path.expanduser("~/Documents"),
        ]
    file_types = {
        "Images": [".png", ".jpg", ".jpeg", ".gif", ".bmp"],
        "Videos": [".mp4", ".mov", ".avi", ".mkv"],
        "Documents": [".pdf", ".docx", ".txt", ".xlsx", ".pptx"],
        "Archives": [".zip", ".rar", ".7z", ".tar"],
        "Audio": [".mp3", ".wav", ".m4a"],
        "Scripts": [".py", ".js", ".html", ".css", ".json"],
    }

    for folder in base_folders:
        if not os.path.exists(folder):
            continue
        for entry in os.scandir(folder):
            if entry.is_file():
                ext = os.path.splitext(entry.name)[1].lower()
                for cat, exts in file_types.items():
                    if ext in exts:
                        dest_dir = os.path.join(folder, cat)
                        os.makedirs(dest_dir, exist_ok=True)
                        try:
                            shutil.move(entry.path, os.path.join(dest_dir, entry.name))
                            print(f"[AutoArrange] Moved {entry.name} → {cat}/")
                        except Exception as e:
                            print(f"[AutoArrange Error] {entry.name}: {e}")
                        break
def get_user_idle_time():
    """Estimate user idle time in seconds (Windows + fallback)."""
    try:
        if platform.system() == "Windows":
            import ctypes
            class LASTINPUTINFO(ctypes.Structure):
                _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]
            lii = LASTINPUTINFO()
            lii.cbSize = ctypes.sizeof(lii)
            ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))
            millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
            return millis / 1000.0
        else:
            return 0
    except Exception:
        return 0
def unified_monitoring_loop(interval=120, health_interval=300):
    """
    Unified background loop that:
    - Monitors user activity
    - Organizes files automatically
    - Checks dependencies, version, and health
    - Initiates self-repair on critical issues
    """
    speak("Unified monitoring systems online, Sir.")
    jarvis_version = get_jarvis_version()
    last_health_check = time.time()
    repair_attempted = False

    print(f"[Monitor] Running Jarvis version {jarvis_version}")

    while True:
        try:
            # --- User Idle Activity ---
            idle_time = get_user_idle_time()
            if idle_time > 1800:
                speak("Sir, you’ve been inactive for a while. Would you like to take a short break?")

            # --- Auto File Organization ---
            auto_arrange_files()

            # --- Health Check ---
            if time.time() - last_health_check > health_interval:
                # Dependency check
                missing = check_dependencies()
                if missing and not repair_attempted:
                    print("[AutoRepair Trigger] Missing dependencies:", missing)
                    speak("Detected missing dependencies. Engaging self-repair protocol.")
                    self_repair(reason="missing dependencies", details=missing)
                    repair_attempted = True

                # Version check
                current_version = get_jarvis_version()
                if current_version != jarvis_version and not repair_attempted:
                    print(f"[AutoRepair Trigger] Version mismatch: expected {jarvis_version}, found {current_version}")
                    speak("Version mismatch detected. Initiating self-repair.")
                    self_repair(reason="version mismatch", details=[jarvis_version, current_version])
                    repair_attempted = True

                # System resource check
                if SYSTEM_MONITOR_AVAILABLE:
                    try:
                        status = system_monitor.report_detailed_status(speak_func=None)
                        cpu = status.get("cpu_percent", 0)
                        mem = status.get("memory_percent", 0)
                        if cpu > 90 or mem > 95:
                            speak(f"Warning: System load is critically high — CPU {cpu}%, Memory {mem}%")
                    except Exception as e:
                        print("[System Monitor Error]", e)

                last_health_check = time.time()

            time.sleep(interval)

        except Exception as e:
            print(f"[Unified Monitor Error] {e}")
            if not repair_attempted:
                speak("Critical monitoring failure. Activating self-repair protocol.")
                self_repair(reason="monitoring crash", details=str(e))
                repair_attempted = True
            time.sleep(10)
def check_directoryfiles():
    speak("Got it. Sir, checking the directory")
    speak("I will provide you the collected info after I finish gathering and verifying things, Sir")
    
# =====================================================
#   Startup Hook
# =====================================================
def initialize_unified_monitor():
    """Launch unified background monitor."""
    threading.Thread(target=unified_monitoring_loop, daemon=True).start()
    print("[Unified Monitoring Thread Started]")

# --- Cmd Functions ---
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
# --- Terminal operations integration helpers ---
# terminal_operator is created lazily so import errors don't break Jarvis startup
terminal_operator = None
def init_terminal_operator():
    """
    Lazily initialize the TerminalOperator and register common predefined keys.
    Predefined keys map either to shell strings (will open a terminal and run) or to callables
    (useful to map to existing Python functions like system_scan).
    """
    global terminal_operator
    if terminal_operator or not TERMINAL_OPS_AVAILABLE:
        return

    try:
        terminal_operator = create_default_operator(speak_func=speak, input_getter=listen)
        plat = platform.system()
        # Register system-scan callables so voice commands can simply say "run sfc"
        # Use simple keys (no spaces) for robust matching.
        terminal_operator.register_command("sfc", lambda: system_scan("sfc"), "Run Windows SFC scan")
        terminal_operator.register_command("chkdsk", lambda: system_scan("chkdsk"), "Run Windows chkdsk")
        terminal_operator.register_command("cleanup", lambda: system_scan("cleanup"), "Run Disk Cleanup")
        terminal_operator.register_command("flushdns", lambda: system_scan("flushdns"), "Flush DNS Cache")
        terminal_operator.register_command("fsck", lambda: system_scan("fsck"), "Run fsck")
        terminal_operator.register_command("apt_cleanup", lambda: system_scan("apt_cleanup"), "Run apt autoremove")
        terminal_operator.register_command("apt_clean", lambda: system_scan("apt_clean"), "Run apt clean")
        terminal_operator.register_command("brew_cleanup", lambda: system_scan("brew_cleanup"), "Run brew cleanup")
        terminal_operator.register_command("diskutil_verify", lambda: system_scan("diskutil_verify"), "Run diskutil verify")

        # register a sensible cross-platform "update_system" predefined:
        if plat == "Linux":
            terminal_operator.register_command("update_system", "sudo apt update && sudo apt upgrade -y", "Update system packages (apt)")
        elif plat == "Windows":
            # Attempt to update via Chocolatey (if installed); otherwise fallback to a no-op message
            if shutil_which := __import__("shutil").which("choco"):
                terminal_operator.register_command("update_system", "choco upgrade all -y", "Update packages via Chocolatey")
            else:
                terminal_operator.register_command("update_system", lambda: speak("Chocolatey not available. Please update Windows packages manually, Sir."), "No-op update on Windows")
        elif plat == "Darwin":
            terminal_operator.register_command("update_system", "brew update && brew upgrade", "Update Homebrew packages")

        # Example convenience alias
        terminal_operator.register_command("update", lambda: terminal_operator.run_predefined("update_system"), "Alias for update_system")

    except Exception as e:
        print("Failed to initialize terminal operator:", e)
def command_help():
    cheatsheet =("""System Commands Cheat Sheet:
- 'system scan' or 'run sfc': Scan system files (Windows only)
- 'disk check' or 'run chkdsk': Check disk for errors (Windows only)
- 'disk cleanup' or 'run cleanup': Open disk cleanup utility (Windows only)
- 'flush dns' or 'clear dns cache': Flush DNS cache (Windows only)
- 'apt cleanup' or 'apt autoremove': Clean up unused packages (Linux only)
- 'apt clean': Clear apt cache (Linux only)
- 'fsck' or 'filesystem check': Check filesystem integrity (Linux only)
- 'brew cleanup': Clean up Homebrew packages (macOS only)
- 'diskutil verify': Verify disk integrity (macOS only)
- 'system status' or 'system monitor': Get detailed system status report

General Commands Cheat Sheet:
Jarvis, what time is it?
Jarvis, what's the weather?
Jarvis, search Wikipedia for [topic]
Jarvis, search Google for [query]
Jarvis, open YouTube or Jarvis, play [video] on YouTube
Jarvis, play [song] on Spotify
Jarvis, send WhatsApp message to [name] -> [dictate message]
Jarvis, email [name] -> [subject] -> [body]
Jarvis, open latest log
Jarvis, start web mode
Jarvis, change ai model to gpt
Jarvis, take a note"
""")
    if ACCESSIBILITY_MODE:
        speak("Displaying the system commands cheat sheet, Sir.")
        print(cheatsheet)
    if not ACCESSIBILITY_MODE:
        speak("Displaying the system commands cheat sheet, Sir.")
        cheat_path = os.path.join(script_dir, "command_cheatsheet.txt")
        with open(cheat_path, "w") as f:
            f.write(cheatsheet)
        if os.name == "nt":
            os.startfile(cheat_path)
        else:
            os.system(f"open '{cheat_path}'")

# --- Modules Initializations ---
file_handler = FileHandler(speak, listen)
#perf_logger = PerformanceLogger(log_dir="logs")
#module_bridge = ModuleBridge(speak, perf_logger)
# --- Model Tasks ----
def process_command(query, chat_history, ai_model):
    
    # Get honorific at the START of function (not from main_loop)
    honorific = get_honorific()
    user_name = get_user_name()

    # Greet or remind contextually
    context_summary = summarize_memory_snapshot()
    if context_summary and random.random() < 0.23:  # 25% chance each run
        speak(f"May I remind you {honorific} that, {context_summary}.")

    query = query.lower()
    
    
    # --- Greeting detection ---
    if "hello" in query:
        honorific = get_honorific()
        user_name = get_user_name()
    
        # Base custom phrase
        speak(f"Oh hello,{honorific}!")
    
        # Add a random follow-up variation for "How's everything?"
        followups = [
            "How’s everything going today?",
            "How are things on your end?",
            "Everything running smoothly, I hope?",
            "How have you been keeping lately?",
            "How’s your day treating you so far?",
            "Hope you’re doing well, Sir.",
            "All systems good on your side, I presume?",
            "Everything holding up well, I trust?",
        ]
        speak(random.choice(followups))
        return chat_history, ai_model
    if any(greet in query for greet in [
        "hi", "hey", "good morning", "good afternoon", "good evening",
        "yo", "greetings", "what's up", "how are you"
    ]):
        smart_greet_response(trigger_manual=True)
        return chat_history, ai_model
    # Muted Functionality
    if any(word in query for word in ["mute", "stop talking", "be quiet", "shut up", "silence"]):
        is_muted = True
        # Stop pyttsx4 immediately
        try:
            engine.stop()
        except:
            pass
        print("[Muted] Speech stopped")
        # Brief pause, then auto-unmute
        time.sleep(0.5)
        is_muted = False
        speak("Understood, Sir.", allow_interrupt=False)
        return chat_history, ai_model
    if any(word in query for word in ["unmute", "speak again", "you can talk", "resume"]):
        is_muted = False
        speak("Audio restored, Sir.", allow_interrupt=False)
        return chat_history, ai_model
    # -- Main commands ---
    if "system status" in query or "system monitor" in query or "system health" in query:
        speak("Got it, gathering system status report, Sir.")
        system_status()
    elif "test microphone" in query or "check mic" in query or "voice test" in query:
        test_microphone()
        return chat_history, ai_model
    elif "cheatsheet" in query or "commands list" in query or "list of commands" in query or "commands help" in query:
        speak("Here is the list of available system commands, Sir:")
        command_help()
    elif "check your version" in query or "tell me the version" in query or "check the version" in query:
        speak("As your wish Sir, checking the version")
        get_jarvis_version()
    elif "backup jarvis" in query or "create backup" in query:
        from jarvis_modules.backup_util import create_jarvis_backup
        try:
            speak("As your wish, Sir. I'll make the backup for you")
            create_jarvis_backup()
            time.sleep(0.2)
            speak("Sir, I have sucessfuly backed up your desired files with timestamps for your ease!")
        except Exception:
            speak("Apologies, sir. I was unable to backup your desired files for you")
    elif "initiate terminal operation" in query or "start terminal mode" in query or "launch terminal operator" in query:
        init_terminal_operator()
        try:
            speak("Preparing terminal operations mode, Sir.")
            if terminal_operator:
                speak("Terminal operations mode is now active, Sir. You can issue commands.")
                terminal_operator.interactive_mode()
            else:
                speak("Terminal operations are not available, Sir.")
        except Exception as e:
            speak(f"An error occurred while starting terminal operations, Sir. Reason: {e}")
    elif "who are you" in query or "what are you" in query or "introduce yourself" in query:
        if not ACCESSIBILITY_MODE:
            play_intro_audio()
        if ACCESSIBILITY_MODE:
            speak("Allow me to introduce myself, I am JARVIS. Virtual Assistant, I am here to assist you with a variety of tasks, twentifour hours a day , seven days a week, your wish is my coomand, Sir.")
    elif "greet someone" in query or "greet other" in query or "introduce to someone" in query:
        if not ACCESSIBILITY_MODE:
            greet_other()
        if ACCESSIBILITY_MODE:
            speak("I am JARVIS. Its my pleasure to meet you, Sir.")
    # -- Core Commands --
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
    elif "open" in query or (query.startswith("open ") and len(query.split()) > 1):
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
    # "Still working on it {test feature}"
    elif "test email" in query or "send test email" in query:
            speak("Sending test email notification.")
            result = send_email_notification(
                "Test Email from Jarvis",
                "This is a test email to verify email notifications are working correctly."
            )
            if result.get("status") == "success":
                speak(f"{honorific}, the test email was sent successfully.")
            else:
                speak(f"Test email failed: {result.get('message')}")
            return
    elif "send email" in query or " send mail" in query:
        match = re.search(r"email  (\w+)", query)
        recipient_name = match.group(1) if match else None
        if not recipient_name:
            speak(f"Who is the intended recipient,{honorific}?")
            recipient_name = listen()
        speak(f"Please specify the subject of the email to {recipient_name},{honorific}.")
        subject = listen()
        speak(f"Kindly dictate the message,{honorific}.")
        body = listen()
        if subject and body:
            send_email(recipient_name, subject, body)
        else:
            speak(f"Incomplete email details detected, {honorific}. Please try again.")
    elif "compose email" in query or "write an email" in query or "auto mail" in query:
        MAILER = EmailManager(speak, API_KEYS, config)
        speak("To whom shall I send it, Sir?")
        recipient = listen()
        speak("What is the topic, Sir?")
        topic = listen()
        result = MAILER.compose_and_send_email(recipient, topic)
        speak(result)
    elif "send message" in query:
        # Try to match "send whatsapp message to <name>"
        match = re.search(r"send\s+(?:whatsapp\s+)?message\s+to\s+(.+)", query, re.IGNORECASE)
        recipient_part = match.group(1).strip() if match else None

        # If user explicitly said recipient name or "contact <id>"
        if recipient_part:
            # Handle case: "contact <number>"
            if recipient_part.lower().startswith("contact"):
                speak(f"Preparing to identify contact {recipient_part}, {honorific}.")
                try:
                    number_map = {
                        "one": "1", "two": "2", "three": "3", "four": "4",
                        "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9", "zero": "0", "ten":"10","eleven":"11","twelve":"12"
                    }
                    for word, num in number_map.items():
                        recipient_part = recipient_part.replace(word, num)

                    contact_id = int("".join(ch for ch in recipient_part if ch.isdigit()))

                    if 1 <= contact_id <= len(CONTACTS):
                        contact = CONTACTS[contact_id - 1]
                        recipient_name = contact["name"]
                    else:
                        speak(f"That contact ID doesn't exist, {honorific}.")
                        return
                except ValueError:
                    speak(f"I couldn't identify that contact number, {honorific}.")
                    return
            else:
                recipient_name = recipient_part

            # Ask for the message content
            speak(f"What message would you like me to deliver to {recipient_name}, {honorific}?")
            message_text = listen()

            # Send message
            if recipient_name and message_text:
                send_whatsapp_desktop_message(recipient_name, message_text)
                LAST_CONTACT = recipient_name
            else:
                speak(f"Insufficient details for the message, {honorific}. Please try again.")

        # If no name or number was given — fall back to interactive mode
        else:
            send_whatsapp_message()
    elif "send another message" in query or "send another whatsapp message" in query:
        if LAST_CONTACT:
            speak(f"What would you like to say to {LAST_CONTACT}, {honorific}?")
            message_text = listen()
            if message_text:
                send_whatsapp_desktop_message(LAST_CONTACT, message_text)
            else:
                speak(f"No message detected, {honorific}.")
        else:
            speak(f"You have not sent any messages recently, {honorific}.")
            send_whatsapp_message()  # fallback to full contact list
    elif "take a note" in query or "note down" in query or "store this information" in query:
        store_note(query)
    elif 'weather' in query:
        # Extract location from command
        location = None
        
        if 'in' in query:
            location = query.split('in' , 1)[-1].strip()
        elif 'at' in query:
            location = query.split('at',1)[-1].strip()
        elif 'of' in query:
            location = query.split('of',1)[-1].strip()
        elif 'for' in query:
            location = query.split('for',1)[-1].strip()
        else:
            speak(f"{honorific},which location would you like to know the weather for?")
            location = listen()
        
        if location and location != "None":
            get_weather(location)
        else:
            speak(f"I was unable to get the weather details, {honorific}")
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
    # APP MANAGEMENT - NEW IMPLEMENTATION
    elif app_manager_instance and any(word in query for word in 
        ["launch", "start", "open", "close", "exit", "terminate", "kill", "access", "run"]):
        handled = process_app_command(query, app_manager_instance, speak)
        if handled:
            return chat_history, ai_model
        else :
            speak(f"Sorry,{honorific}.I faced some issues when trying to open the desired app")
    # Close active window specifically
    elif "close active" in query or "close current" in query:
        if app_manager_instance:
            app_manager_instance.close_active_window()
        else:
            active_appcloser(speak)
        return chat_history, ai_model
    # --- The repair system util commands ---
    elif "self repair" in query or "initiate repair" in query or "diagnose system" in query:
        speak(f"As you wish, {honorific}. Initiating the self-repair protocol.")
        try:
            from jarvis_modules.self_repair import self_repair
            
            result = self_repair(
                reason="User-initiated diagnostic and repair",
                details="Manual execution via voice command",
                speak=speak,
                input_getter=listen
            )
            # Handle result
            if result['user_declined']:
                speak(f"Repair sequence cancelled as per your instructions, {honorific}.")
            elif result['success']:
                if result['backup_created']:
                    speak(f"Self-repair completed successfully with backup safety net in place, {honorific}.")
                else:
                    speak(f"Self-repair completed successfully. All systems nominal, {honorific}.")
            else:
                speak(f"Self-repair encountered issues. Please review the diagnostic report, {honorific}.")
                if result['backup_created']:
                    speak(f"A pre-repair backup is available for rollback if needed, {honorific}.")
                
        except Exception as e:
            speak(f"Unable to execute self-repair, {honorific}. Error: {e}")
            print(f"[Self-Repair Error] {e}")
    elif "system diagnostics" in query or "check system health" in query or "system status" in query:
        speak(f"Running system diagnostics, {honorific}...")
        
        try:
            from jarvis_modules.self_repair import diagnose_only
            
            report = diagnose_only(speak=speak, input_getter=listen)
            
            # Provide detailed summary
            status = report['overall_status']
            
            if status == 'HEALTHY':
                speak(f"All systems are functioning optimally, {honorific}.")
                if report['backup_system']['backup_count'] > 0:
                    speak(f"Backup system operational with {report['backup_system']['backup_count']} backups available.")
            elif status == 'DEGRADED':
                speak(f"Minor issues detected. Self-repair recommended, {honorific}.")
                speak(f"Issues: {len(report['modules']['missing'])} missing modules, {len(report['config']['issues'])} config issues.")
            else:
                speak(f"Critical issues detected. Immediate repair required, {honorific}.")
                if report['files']['missing']:
                    speak(f"{len(report['files']['missing'])} critical files are missing.")
                if report['backup_system']['backup_count'] > 0:
                    speak(f"Backups are available for file restoration.")
                
        except Exception as e:
            speak(f"Diagnostic scan failed, Sir. Error: {e}")
            print(f"[Diagnostic Error] {e}")
    elif "create backup" in query or "backup system" in query or "make backup" in query:
        speak(f"Initiating backup creation, {honorific}.")
        
        try:
            from jarvis_modules.self_repair import create_backup_now
            
            success, backup_path = create_backup_now(speak=speak, input_getter=listen)
            
            if success:
                speak(f"Backup created successfully at {backup_path}, {honorific}.")
            else:
                speak(f"Backup creation failed, {honorific}. Please check system logs.")
                
        except Exception as e:
            speak(f"Unable to create backup, {honorific}. Error: {e}")
            print(f"[Backup Error] {e}")
    elif "restore from backup" in query or "rollback system" in query:
        speak(f"{honorific}, manual restoration requires specific file selection.")
        speak(f"Please use the self-repair system for automated restoration.")
        speak(f"Say 'self repair' to begin the diagnostic and restoration process.")
    elif "backup status" in query or "check backups" in query:
        speak(f"Checking backup system status, {honorific}...")
        
        try:
            from jarvis_modules.self_repair import check_backup_availability, get_backup_directory
            
            backup_available, backup_count, latest_backup = check_backup_availability(speak)
            
            if backup_available and backup_count > 0:
                speak(f"Backup system operational, Sir.")
                speak(f"{backup_count} backups are currently available.")
                if latest_backup:
                    speak(f"Most recent backup: {latest_backup.strftime('%B %d, %Y at %I:%M %p')}")
                backup_dir = get_backup_directory()
                speak(f"Backup location: {backup_dir}")
            elif backup_available and backup_count == 0:
                speak(f"Backup system is functional but no backups exist yet, {honorific}.")
                speak("I recommend creating a backup now for system safety.")
            else:
                speak(f"Backup system is not currently available, {honorific}.")
                speak("Please ensure the backup utility is properly configured.")
                
        except Exception as e:
            speak(f"Unable to check backup status, {honorific}. Error: {e}")
            print(f"[Backup Status Error] {e}")
    # --- System Notifications and time based prompts ---
    elif "disable time prompts" in query or "turn off reminders" in query:
        toggle_time_prompts(False)
        speak("Time-based prompts disabled, Sir.")
        return chat_history, ai_model
    elif "enable time prompts" in query or "turn on reminders" in query:
        toggle_time_prompts(True)
        speak("Time-based prompts enabled, Sir.")
        return chat_history, ai_model
    elif "notification cooldown" in query or "set notification interval" in query:
        speak("Please specify cooldown duration in minutes, Sir.")
        response = listen()
        try:
            minutes = int(''.join(filter(str.isdigit, response)))
            set_notification_cooldown(minutes)
            speak(f"Notification check interval set to {minutes} minutes, Sir.")
        except:
            speak("Invalid duration, Sir.")
        return chat_history, ai_model
    elif "list custom prompts" in query or "show my prompts" in query or "show custom reminders" in query:
            prompts = list_custom_prompts()
            if prompts:
                speak(f"You have {len(prompts)} custom prompts registered, Sir.")
                for prompt_id, message, enabled in prompts:
                    status = "enabled" if enabled else "disabled"
                    speak(f"{prompt_id}: {status}")
            else:
                speak("No custom prompts are currently registered, Sir.")
            return chat_history, ai_model
    # Schedule commands
    elif "review today" in query or "today's plans" in query or "what's today" in query:
        review_schedule(0)
    elif "review yesterday" in query or "yesterday's plans" in query or "what was yesterday" in query:
        review_schedule(-1)
    elif "review tomorrow" in query or "tomorrow's plans" in query or "what's tomorrow" in query:
        review_schedule(1)
    elif "schedule for today" in query or "plan for today" in query or "add today's plan" in query:
        add_schedule_interactive(0)
    elif "schedule for tomorrow" in query or "plan for tomorrow" in query or "add tomorrow's plan" in query:
        add_schedule_interactive(1)
    elif "modify today" in query or "change today's plan" in query or "update today" in query:
        modify_schedule(0)
    elif "modify tomorrow" in query or "change tomorrow's plan" in query or "update tomorrow" in query:
        modify_schedule(1)
    elif "clear today's schedule" in query or "delete today's plans" in query:
        date_key, day_name = get_schedule_date_key(0)
        data = load_data()
        if "schedule" in data and date_key in data["schedule"]:
            del data["schedule"][date_key]
            save_data(data)
            speak(f"Today's schedule has been cleared, {honorific}.")
        else:
            speak(f"There was no schedule to clear,{honorific}.")
    elif "create schedule" in query or "set schedule now" in query or "add schedule now" in query:
                force_schedule_prompt()
                return chat_history, ai_model
    # --- System Scans ---
    elif any(word in query for word in ["scan", "check disk", "cleanup", "flush dns"]):
        if "sfc" in query or "system file" in query:
                return system_scan("sfc")
        elif "disk" in query or "check" in query:
                return system_scan("chkdsk")
        elif "cleanup" in query:
                return system_scan("cleanup")
        elif "flush" in query or "dns" in query:
                return system_scan("flushdns")
        else:
                speak("Specify which system scan you want, Sir.")
                return
    # --- Commands For File Handler Modules ----
    elif "create file" in query:
        match = re.search(r"create file (.+)", query)
        if match:
            file_handler.create_file(match.group(1))
    elif "read file" in query:
        match = re.search(r"read file (.+)", query)
        if match:
            content = file_handler.read_file(match.group(1))
            if content:
                speak(content[:200])  # Read first 200 chars
    elif "delete file" in query:
        match = re.search(r"delete file (.+)", query)
        if match:
            file_handler.delete_file(match.group(1))
    elif "search files" in query:
        match = re.search(r"search files for (.+) in (.+)", query)
        if match:
            pattern, directory = match.groups()
            file_handler.search_files(directory, pattern)
    elif "organize files" in query or "organize directory" in query:
        directory = os.path.expanduser("~/Downloads")  # or detect from query
        file_handler.organize_directory(directory, dry_run=False)
    elif "file info" in query:
        match = re.search(r"file info (.+)", query)
        if match:
            file_handler.get_file_info(match.group(1))
    # --- Memory-Aware Conversation Layer ---
    elif "remind me what we discussed" in query or "last conversation" in query:
        recall_recent_conversations()
    elif "what do you remember" in query or "recall my topics" in query:
        recall_topics()
    elif "remember this" in query:
        topic = query.replace("remember this", "").strip()
        if topic:
            remember_topic(topic)
        else:
           speak("Please tell me what you'd like me to remember, Sir.")
    elif "focus for today" in query or "set focus" in query:
        speak("What would you like today's main focus to be, Sir?")
        focus = listen()
        if focus:
            update_memory_context("daily_focus", focus)
            speak(f"Understood, Sir. I’ll remind you to stay focused on {focus} today.")
    elif "how am i doing" in query or "summarize my progress" in query:
        summary = summarize_memory_snapshot()
        speak(f"Here’s your current overview, Sir: {summary}")
    elif "what did i say yesterday" in query or "what did we talk about" in query or "recall conversation" in query:
        recall_recent_conversations(days=1)
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
    # Record each conversation (query + generated response)
    try:
        if 'response' in locals():
            store_conversation_entry(query, response)
    except Exception as e:
        print(f"[Memory Logging Error] {e}")
    try:
        update_personality_context(True)
    except Exception as e:
        print(f"[Personality Update Error] {e}")
    
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

# --- Main Loop ---
# ------------------------------------
def main_loop(): 
    jarvis_boot_sequence("v17")
    check_tts_engine()
    setup_mute_hotkey()

    # Migration - Run once
    migrate_schedule_flag()
    
    print("Performing context and memory integrity check, Sir.")
    load_memory_context()
    load_personality()

    
    # Check if we need to prompt for preferences BEFORE greeting
    should_prompt = SETTINGS.get("prompt_user_preferences", True)
    already_configured = SETTINGS.get("preferences_configured", False)
    needs_setup = should_prompt and not already_configured
    
    # Initial greeting (generic or personalized based on setup status)
    if needs_setup:
        # Generic greeting for new users
        speak("I have indeed been successfully booted.")
        speak("Before we begin, let me configure a few preferences for you.")
        
        # NEW: Prompt for user preferences
        prompt_user_preferences()
        
        # Confirmation after setup
        speak("Excellent. Your preferences have been saved.")
        speak("Now, let's get started.")
    else:
        # Personalized greeting for configured users
        user_name = get_user_name()
        honorific = get_honorific()
        speak(f"I have indeed been successfully booted, {honorific}.")
        speak(f"Welcome back, {user_name}.")
    
    # Common continuation for all users
    speak(f"Though, valuing your preference {honorific}, I choose to run silently in standby mode unless you need me otherwise.")
    
    # ONE-TIME microphone calibration at startup
    if VOICE_AVAILABLE and not ACCESSIBILITY_MODE:
        try:
            r = sr.Recognizer()
            with sr.Microphone() as source:
                print("Calibrating microphone for ambient noise...")
                r.adjust_for_ambient_noise(source, duration=1.0)
                print("Calibration complete.")
        except Exception as e:
            print(f"Calibration failed: {e}")

    chat_history = []
    ai_model = SETTINGS.get("preferred_ai_model", "openrouter")
    slept = False
    
    while True:
        if not ACCESSIBILITY_MODE:
            print(f"\nListening for Voice Activation...")
            command = listen()
            # CRITICAL FIX: Only process if we actually got input
            if not command:
                time.sleep(0.5)  # Brief pause to prevent CPU spinning
                continue
            # Check for wake word
            if WAKE_WORD.lower() not in command.lower():
                continue
            if "go offline" in command:
                honorific = get_honorific()
                speak(f"Shutting down now, {honorific}. Farewell.")
                return
            if slept:
                try:
                    playsound.playsound(mp3_file_path)
                    slept = False
                except Exception:
                    honorific = get_honorific()
                    speak(f"Yes {honorific}.")
                    slept = False
            else:
                user_name = get_user_name()
                honorific = get_honorific()
                wish_me()
                speak(f"{honorific},now that I am active, feel free to tell me what can I assist you with?")
                
        if ACCESSIBILITY_MODE:
            print(f"\nWaiting for Text Activation...")
            command = listen()
            # Same for accessibility mode
            if not command:
                time.sleep(0.5)
                continue
            # When listen() returns empty string, we simply continue listening in background.
            if WAKE_WORD.lower() not in command.lower():
                continue
            if "go offline" in command:
                honorific = get_honorific()
                speak(f"Shutting down now, {honorific}. Farewell.")
                return
            if slept:
                honorific = get_honorific()
                speak(f"Yes {honorific}.")
                slept = False
            else:
                try:
                    user_name = get_user_name()
                    honorific = get_honorific()
                    wish_me()

                except:
                    user_name = get_user_name()
                    honorific = get_honorific()
                    speak(f"Hello {user_name}, Jarvis. Your virtual AI assistant is now online and ready to assist you, {honorific}. How may I help you today?")
                    speak(f"{honorific},now that I am active, feel free to tell me what can I assist you with?")
        # Main command processing loop
        while True:
            query = listen()

            # CRITICAL FIX: Handle empty responses
            if not query:
                time.sleep(0.3)  # Small delay to prevent spam
                continue

            if "go to sleep" in query:
                honorific = get_honorific()
                speak(f"Entering standby mode, {honorific}.")
                slept = True
                break
                
            if "go offline" in query or "shut down" in query or "power down" in query:
                jarvis_shutdown_sequence()
                honorific = get_honorific()
                speak(f"System shutting down, {honorific}.")
                return
                
            if "goodbye" in query or "bye" in query:
                jarvis_shutdown_sequence()
                return
                
            if "start web mode" in query:
                threading.Thread(target=start_web_interface, daemon=True).start()
                continue
                
            if "wake up" in query:
                honorific = get_honorific()
                speak(f"I am awake and at your service, {honorific}.")
                continue
                
            if "are you there" in query:
                honorific = get_honorific()
                speak(f"At your service, {honorific}.")
                speak("Would you like me to do anything now, or shall I remain on standby?")
                continue
                
            if "you up" in query:
                honorific = get_honorific()
                speak(f"For you, {honorific}, Always.")
                continue
                
            if "tell me the version" in query:
                honorific = get_honorific()
                speak(f"Alright {honorific}, checking my current version")
                get_jarvis_version()
                continue
            # Around line 2100, add this to process_command() before the schedule commands section:

                
            if "idle time" in query:
                honorific = get_honorific()
                speak(f"As your wish, {honorific}.")
                get_user_idle_time(speak)
                continue
                
            if "play the music" in query:
                try:
                    music_dir = os.path.join(script_dir, "Music")
                    if os.path.exists(music_dir):
                        for file in os.listdir(music_dir):
                            if query in file.lower():
                                song_path = os.path.join(music_dir, file)
                                honorific = get_honorific()
                                speak(f"Playing {file} from local storage, {honorific}.")
                                threading.Thread(target=playsound.playsound, args=(song_path,), daemon=True).start()
                                time.sleep(0.6)
                                speak(f"Okay. {honorific}, enjoy the music.")
                                speak(f"Do tell me if you need anything else, {honorific}!")
                                continue
                except Exception:   
                    honorific = get_honorific()
                    speak(f"Sorry, {honorific}. Playing music as you requested can't be done successfully.")
                    speak(f"{honorific}, please consider my apologies for inconvenience occurred")
                    continue
                    
            if "change ai model to" in query:
                new_model = query.replace("change ai model to", "").strip()
                if new_model in ["gemini", "gpt", "openrouter","mistral"]:
                    ai_model = new_model
                    honorific = get_honorific()
                    speak(f"AI model switched to {ai_model}, {honorific}.")
                else:
                    honorific = get_honorific()
                    speak(f"The specified model is not supported, {honorific}.")
                continue
                
            chat_history, ai_model = process_command(query, chat_history, ai_model)

if __name__ == "__main__":
    try:
        main_loop()
        #initialize_unified_monitor()
        # Start monitoring in background
        #threading.Thread(target=background_monitoring_loop, daemon=True).start()

    except KeyboardInterrupt:
        speak("Deactivating Jarvis now, Sir. Farewell.")
        print("\nDeactivating Jarvis... Goodbye, Sir.")