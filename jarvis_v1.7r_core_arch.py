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
import playsound
import sys
import shutil
import psutil
#import cv2

import pyautogui
import pyperclip
import random
from colorama import init, Fore, Style , Back

# Simple mute control (no threading)
is_muted = False

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False

# ----- Jarvis Utils Imports -------
try: 
    from jarvis_modules.ai_summarizer import summarize_file, summarize_text
except Exception:
    print("Sir,I apologise for not being able to import Summarizer module sucessfuly")

try: 
    from jarvis_modules.self_repair import self_repair
except Exception:
    print("Sir,I apologise for not being able to import Self Repair module sucessfuly")


try:
    from jarvis_modules.advanced_app_manager import initialize_app_manager, process_app_command , speak , active_appcloser
    APP_MANAGER_AVAILABLE = True
except ImportError:
    APP_MANAGER_AVAILABLE = False
    print("Advanced App Manager not available. Using fallback methods.")

# Initialize after other setups (around line 150-200)
app_manager_instance = None
if APP_MANAGER_AVAILABLE:
    app_manager_instance = initialize_app_manager(speak)

# --- system_monitor import (seamless, optional) ---
try:
    import system_monitor
    SYSTEM_MONITOR_AVAILABLE = True
except Exception:
    system_monitor = None
    SYSTEM_MONITOR_AVAILABLE = False

# Optional terminal operations integration (teminal_operations.py)
try:
    from  terminal_operations import create_default_operator
    TERMINAL_OPS_AVAILABLE = True
except Exception:
    create_default_operator = None
    TERMINAL_OPS_AVAILABLE = False

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

import asyncio
try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

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

try:
    mp3_file_path = "beep.mp3" 
except Exception:
    print("The beep audio is not imported sucessfuly")


script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "config.json")

try:
    with open(config_path, "r") as f:
        config = json.load(f)
except FileNotFoundError:
    print(f"âŒ config.json not found at {config_path}. Please create it and fill in your details.")
    exit()
except json.JSONDecodeError:
    print(f"âŒ Error decoding config.json. Please check its format.")
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

# ---- Sequences and Animations ----
def jarvis_boot_sequence(version="v17o"):
    # Initialize colorama
    init(autoreset=True)
    os.system('cls' if os.name == 'nt' else 'clear')

    def slow_print(text, delay=0.01, color=Fore.WHITE):
        for char in text:
            sys.stdout.write(color + char)
            sys.stdout.flush()
            time.sleep(delay)
        print()

    # Header
    display_jarvis_banner()
    print(Fore.CYAN + Style.BRIGHT + "===============================================")
    slow_print("     INITIALIZING J.A.R.V.I.S MAINFRAME", 0.02, Fore.CYAN)
    print(Fore.CYAN + Style.BRIGHT + "===============================================")
    time.sleep(0.6)

    # Simulated system scan animation
    for i in range(3):
        print(Fore.YELLOW + f"Booting Core Modules{'.' * (i+1)}", end="\r")
        time.sleep(0.5)
    print(" " * 40, end="\r")

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
        sys.stdout.write(Fore.GREEN + f"[âœ“] {step}")
        sys.stdout.flush()
        time.sleep(random.uniform(0.2, 0.35))
        print()
        time.sleep(0.1)

    print(Fore.CYAN + "-----------------------------------------------")
    time.sleep(0.3)

    # Diagnostics scan simulation
    cpu_usage = psutil.cpu_percent(interval=0.3)
    mem = psutil.virtual_memory()
    mem_used = round(mem.used / (1024 ** 3), 2)
    mem_total = round(mem.total / (1024 ** 3), 2)
    net_io = psutil.net_io_counters()
    upload = round(net_io.bytes_sent / (1024 ** 2), 2)
    download = round(net_io.bytes_recv / (1024 ** 2), 2)

    slow_print(f"â†’ CPU Load: {cpu_usage}% ", 0.01, Fore.YELLOW)
    slow_print(f"â†’ Memory Usage: {mem_used}GB / {mem_total}GB", 0.01, Fore.YELLOW)
    slow_print(f"â†’ Network I/O: â†‘ {upload} MB  â†“ {download} MB", 0.01, Fore.YELLOW)
    time.sleep(0.5)

    print(Fore.CYAN + "-----------------------------------------------")
    slow_print(f"CORE STATUS: { 'STABLE'}", 0.01)
    slow_print(f"VERSION: {version.upper()}", 0.01)
    slow_print(f"MODE: {'Operational'}", 0.01)
    print(Fore.CYAN + "-----------------------------------------------")

    # Loading bar animation
    print()
    slow_print("Activating main subsystems:", 0.02)
    for i in range(31):
        bar = "â–ˆ" * i + "-" * (30 - i)
        sys.stdout.write(Fore.GREEN + f"\r[{bar}] {int((i/30)*100)}%")
        sys.stdout.flush()
        time.sleep(0.05)
    print("\n")

    # Final activation
    time.sleep(0.5)
    slow_print("System integrity check: PASS", 0.02)
    time.sleep(0.4)
    slow_print(">>> All Systems Online.", 0.02)
    time.sleep(0.3)
    slow_print(">>> JARVIS CORE ACTIVATED.", 0.02)
    time.sleep(0.5)
    print()
    slow_print("Welcome back, Sir.", 0.03)
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

    # âš¡ Quick reactivation animation
    for i in range(3):
        sys.stdout.write(Fore.GREEN + Style.BRIGHT + "âš¡ Syncing Core Systems" + "." * (i+1) + "\r")
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
        slow_print(Fore.GREEN + f"[âœ“] {step}", 0.02)
        time.sleep(0.05)

    print(Fore.CYAN + "-----------------------------------------------")
    slow_print(Fore.GREEN + Style.BRIGHT + "SYSTEM STATUS: ONLINE", 0.02)
    slow_print(Fore.CYAN + "MODE: Reactivation", 0.02)
    slow_print(Fore.YELLOW + "RUNTIME SYNCHRONIZED", 0.02)
    print(Fore.CYAN + "-----------------------------------------------")
    time.sleep(0.5)

    # Pulse animation to indicate active state
    for i in range(3):
        sys.stdout.write(Fore.CYAN + Style.BRIGHT + "â€¢ SYSTEM LINK RESTORED â€¢".center(60))
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
    print(Fore.CYAN + Style.BRIGHT + "\n[ðŸŽ™ï¸] Listening...")

    pulse_patterns = [
        "â–â–‚â–ƒâ–„â–…â–†â–‡â–ˆâ–‡â–†â–…â–„â–ƒâ–‚â–",
        "â–â–‚â–ƒâ–„â–…â–†â–‡â–†â–…â–„â–ƒâ–‚â–",
        "â–â–‚â–ƒâ–„â–…â–†â–‡â–ˆâ–‡â–†â–…â–„â–ƒâ–‚â–"
    ]

    end_time = time.time() + duration
    while time.time() < end_time:
        for pattern in pulse_patterns:
            sys.stdout.write(Fore.CYAN + Style.BRIGHT + f"\r{pattern}")
            sys.stdout.flush()
            time.sleep(0.1)
    print("\r" + " " * 40 + "\r", end="")
    print(Fore.GREEN + Style.BRIGHT + "[âœ”] Command recognized.\n")
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
        sys.stdout.write(Fore.BLUE + Style.BRIGHT + ("â€¢ JARVIS SLEEPING â€¢".center(50)))
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

    # ðŸ”» Simulated module deactivation
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
        sys.stdout.write(Fore.YELLOW + f"[â€“] {step}")
        sys.stdout.flush()
        time.sleep(0.25)
        print()
        time.sleep(0.1)

    print(Fore.RED + "-----------------------------------------------")
    time.sleep(0.3)

    # âš¡ Fade-out progress bar
    slow_print("Deactivating Core Systems:", 0.02, Fore.WHITE)
    for i in range(30, -1, -1):
        bar = "â–ˆ" * i + "-" * (30 - i)
        sys.stdout.write(Fore.RED + f"\r[{bar}] {int((i/30)*100)}%")
        sys.stdout.flush()
        time.sleep(0.05)
    print("\n")

    # ðŸ’  Power-down pulse animation
    for i in range(3):
        sys.stdout.write(Fore.RED + Style.BRIGHT + "âš¡ SYSTEM ENERGY DROPPING " + "." * (i+1) + "\r")
        sys.stdout.flush()
        time.sleep(0.5)
    print(" " * 50, end="\r")

    # ðŸ§  Final status
    print(Fore.RED + "-----------------------------------------------")
    slow_print("CORE STATUS: OFFLINE", 0.02)
    slow_print("SYSTEM MEMORY: Released", 0.02)
    slow_print("DATA LINKS: Terminated", 0.02)
    slow_print("All subsystems deactivated.", 0.02)
    print(Fore.RED + "-----------------------------------------------")
    time.sleep(0.5)

    # ðŸ‘‹ Farewell message
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
def display_jarvis_banner():
    """Displays a blue ASCII terminal banner 'JARVIS'."""
    os.system("cls" if os.name == "nt" else "clear")
    fig = Figlet(font="univers")  # You can try 'ansi_shadow' or 'ansi_regular','slant','univers',big'
    banner = fig.renderText("JARVIS")
    #for line in banner.splitlines():
     #   print(" " + Fore.BLUE + line)
    print(Fore.BLUE + Style.BRIGHT + banner + Style.RESET_ALL)
    print(Fore.BLUE + "-------------------------------------------------------------")
    print(Fore.CYAN +   "AI Assistant System | Version 17.0 " )
    print(Fore.BLUE + "-------------------------------------------------------------")
    time.sleep(0.6)
def jarvis_sleep_animation():
    """Cinematic sleep mode effect."""
    init(autoreset=True)
    for i in range(3):
        sys.stdout.write(Fore.MAGENTA + f"\rEntering sleep mode{'.' * (i+1)}")
        sys.stdout.flush()
        time.sleep(0.6)
    print("\r" + " " * 40, end="\r")
    print(Fore.MAGENTA + "ðŸ’¤ JARVIS is now in standby mode. Awaiting wake word..." + Style.RESET_ALL)

# --- Core Utils Functions ----
def check_tts_engine():
    if EDGE_TTS_AVAILABLE:
        try:
            import edge_tts
            print("âœ… Neural Voice Module Online")
            speak("Neural voice interface online.")
        except Exception as e:
            print(f"âš ï¸ Edge-TTS detected but failed: {e}")
            speak("Fallback voice active, neural engine offline.")
    else:
        print("âŒ Edge-TTS not installed.")
        speak("Neural voice module not found, using local voice system.")
# The modular personality speak function
_last_personality = "neutral"  # tone continuity
import asyncio
import tempfile
import os
def speak(text, allow_interrupt=True):
    """
    Enhanced speak with keyboard interrupt capability.
    Press ESC key to stop speech (no threading needed).
    Checks mute flag between sentences for clean interruption.
    """
    global _last_personality, is_muted

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
            print(f"[Edge-TTS Error] Fallback to pyttsx4 â€“ {e}")

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
def get_user_name():
    return SETTINGS.get("user_name", "User")
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
# --- System CMD Functions ---
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
# --- LL Models Setup and Chat ----
#   Gpt
def chat_with_gpt(query, chat_history):
    if not openai_client:
        return "GPT is not configured.", chat_history
    messages = [{"role": "system", "content": "You are JARVIS, Tony Starkâ€™s AI assistant. Your persona is polite, witty, and exceptionally intelligent with a formal British tone. Always address the user as 'Sir'. Keep answers concise and never use emoji while answering any queries or generating a response. You are proactive, efficient, and occasionally humorous."}] + chat_history + [{"role": "user", "content": query}]
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
        "content": ("You are JARVIS, Tony Starkâ€™s AI assistant. Your persona is polite, witty, and exceptionally intelligent with a formal British tone. "
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
        "content": ("You are JARVIS, Tony Starkâ€™s AI assistant. Your persona is polite, witty, and exceptionally intelligent with a formal British tone. "
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
    wish = "Welcome Sir!"
    if 5 <= hour < 12: greeting = "Good morning."
    elif 12 <= hour < 18: greeting = "Good afternoon."
    elif 18 <= hour < 22: greeting = "Good evening."
    elif 22 <= hour < 24: greeting = "It's quite late"
    elif 1 <= hour < 5: greeting = "You're up quite early, Sir. How may I help?"
    else: greeting = "Sir, I am ready and at your service."
    speak(wish)
    speak(greeting)

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
                # confidence not supported (no OpenCV) â†’ try without it
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
        lines.append(f"{h['name']} â€” {h['streak']} day streak (last: {last_done})")
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
        installed_packages = {pkg.key: pkg.version for pkg in requirements_file}
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
                            print(f"[AutoArrange] Moved {entry.name} â†’ {cat}/")
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
                speak("Sir, youâ€™ve been inactive for a while. Would you like to take a short break?")

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
                            speak(f"Warning: System load is critically high â€” CPU {cpu}%, Memory {mem}%")
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
    cheatsheet = """System Commands Cheat Sheet:
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
Jarvis, take a note
"""
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
# --- Model Tasks ----
def process_command(query, chat_history, ai_model):
    query = query.lower()
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
        # Try to match "send whatsapp message to <name>"
        match = re.search(r"send\s+(?:whatsapp\s+)?message\s+to\s+(.+)", query, re.IGNORECASE)
        recipient_part = match.group(1).strip() if match else None

        # If user explicitly said recipient name or "contact <id>"
        if recipient_part:
            # Handle case: "contact <number>"
            if recipient_part.lower().startswith("contact"):
                speak(f"Preparing to identify contact {recipient_part}, Sir.")
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
                        speak("That contact ID doesn't exist, Sir.")
                        return
                except ValueError:
                    speak("I couldn't identify that contact number, Sir.")
                    return
            else:
                recipient_name = recipient_part

            # Ask for the message content
            speak(f"What message would you like me to deliver to {recipient_name}, Sir?")
            message_text = listen()

            # Send message
            if recipient_name and message_text:
                send_whatsapp_desktop_message(recipient_name, message_text)
                LAST_CONTACT = recipient_name
            else:
                speak("Insufficient details for the message, Sir. Please try again.")

        # If no name or number was given â€” fall back to interactive mode
        else:
            send_whatsapp_message()
    elif "send another message" in query or "send another whatsapp message" in query:
        if LAST_CONTACT:
            speak(f"What would you like to say to {LAST_CONTACT}, Sir?")
            message_text = listen()
            if message_text:
                send_whatsapp_desktop_message(LAST_CONTACT, message_text)
            else:
                speak("No message detected, Sir.")
        else:
            speak("You have not sent any messages recently, Sir.")
            send_whatsapp_message()  # fallback to full contact list
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
    # APP MANAGEMENT - NEW IMPLEMENTATION
    elif app_manager_instance and any(word in query for word in 
        ["launch", "start", "open", "close", "exit", "terminate", "kill", "access", "run"]):
        handled = process_app_command(query, app_manager_instance, speak)
        if handled:
            return chat_history, ai_model
        else :
            speak("Sorry,sir.I faced some issues when trying to open the desired app")
    # Close active window specifically
    elif "close active" in query or "close current" in query:
        if app_manager_instance:
            app_manager_instance.close_active_window()
        else:
            active_appcloser(speak)
        return chat_history, ai_model
    # --- The repair system util commands ---
    elif "self repair" in query or "initiate repair" in query or "diagnose system" in query:
        speak("As you wish, Sir. Initiating the self-repair protocol.")
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
                speak("Repair sequence cancelled as per your instructions, Sir.")
            elif result['success']:
                if result['backup_created']:
                    speak("Self-repair completed successfully with backup safety net in place, Sir.")
                else:
                    speak("Self-repair completed successfully. All systems nominal, Sir.")
            else:
                speak("Self-repair encountered issues. Please review the diagnostic report, Sir.")
                if result['backup_created']:
                    speak("A pre-repair backup is available for rollback if needed, Sir.")
                
        except Exception as e:
            speak(f"Unable to execute self-repair, Sir. Error: {e}")
            print(f"[Self-Repair Error] {e}")
    elif "system diagnostics" in query or "check system health" in query or "system status" in query:
        speak("Running system diagnostics, Sir...")
        
        try:
            from jarvis_modules.self_repair import diagnose_only
            
            report = diagnose_only(speak=speak, input_getter=listen)
            
            # Provide detailed summary
            status = report['overall_status']
            
            if status == 'HEALTHY':
                speak("All systems are functioning optimally, Sir.")
                if report['backup_system']['backup_count'] > 0:
                    speak(f"Backup system operational with {report['backup_system']['backup_count']} backups available.")
            elif status == 'DEGRADED':
                speak("Minor issues detected. Self-repair recommended, Sir.")
                speak(f"Issues: {len(report['modules']['missing'])} missing modules, {len(report['config']['issues'])} config issues.")
            else:
                speak("Critical issues detected. Immediate repair required, Sir.")
                if report['files']['missing']:
                    speak(f"{len(report['files']['missing'])} critical files are missing.")
                if report['backup_system']['backup_count'] > 0:
                    speak("Backups are available for file restoration.")
                
        except Exception as e:
            speak(f"Diagnostic scan failed, Sir. Error: {e}")
            print(f"[Diagnostic Error] {e}")
    elif "create backup" in query or "backup system" in query or "make backup" in query:
        speak("Initiating backup creation, Sir.")
        
        try:
            from jarvis_modules.self_repair import create_backup_now
            
            success, backup_path = create_backup_now(speak=speak, input_getter=listen)
            
            if success:
                speak(f"Backup created successfully at {backup_path}, Sir.")
            else:
                speak("Backup creation failed, Sir. Please check system logs.")
                
        except Exception as e:
            speak(f"Unable to create backup, Sir. Error: {e}")
            print(f"[Backup Error] {e}")
    elif "restore from backup" in query or "rollback system" in query:
        speak("Sir, manual restoration requires specific file selection.")
        speak("Please use the self-repair system for automated restoration.")
        speak("Say 'self repair' to begin the diagnostic and restoration process.")
    elif "backup status" in query or "check backups" in query:
        speak("Checking backup system status, Sir...")
        
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
                speak("Backup system is functional but no backups exist yet, Sir.")
                speak("I recommend creating a backup now for system safety.")
            else:
                speak("Backup system is not currently available, Sir.")
                speak("Please ensure the backup utility is properly configured.")
                
        except Exception as e:
            speak(f"Unable to check backup status, Sir. Error: {e}")
            print(f"[Backup Status Error] {e}")
    
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

# --- Main Loop ---
# ------------------------------------
def main_loop(): 
    jarvis_boot_sequence("v17o")
    check_tts_engine()
    setup_mute_hotkey()
    wish_me()
    speak("I have indeed been sucessfuly booted, sir. We're online and ready.")
    speak("Though, valuing your prefference, I choose to run silently in standby mode, sir, unless you need me otherwise.")

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
            print(f"\nListening for wake word: 'Jarvis'...")
            command = listen()
            # CRITICAL FIX: Only process if we actually got input
            if not command:
                time.sleep(0.5)  # Brief pause to prevent CPU spinning
                continue
            # Check for wake word
            if not command or WAKE_WORD.lower() not in command.lower():
                continue
            if "go offline" in command:
                speak("Shutting down now, Sir. Farewell.")
                return
            if slept:
                try:
                    playsound.playsound(mp3_file_path)
                    slept = False
                except Exception:
                    speak("Yes Sir.")
                    slept = False
            else:
                user_name = get_user_name()
                if not ACCESSIBILITY_MODE:
                    #jarvis_wakeup_sequence()
                    #speak("Online and fully functional, Sir.")
                    speak(f"Hello {user_name}")
                    speak("We're online and ready., Sir.")
                    speak("How may I assist you?")
                if ACCESSIBILITY_MODE:
                    speak(f"Hello {user_name}, Jarvis. Your virtual AI assistant is now online and ready to assist you, Sir. How may I help you today?")
        if ACCESSIBILITY_MODE:
            print(f"\nListening for wake word: '{WAKE_WORD}'...")
            command = listen()
            # Same for accessibility mode
            if not command:
                time.sleep(0.5)
                continue
            # When listen() returns empty string, we simply continue listening in background.
            if not command or WAKE_WORD.lower() not in command.lower():
                continue
            if "go offline" in command:
                speak("Shutting down now, Sir. Farewell.")
                return
            if slept:
                speak("Yes Sir.")
                slept = False
            else:
             try:
                user_name = get_user_name()
                speak(f"Hello {user_name}")
                speak("We're online and ready., Sir.")
                speak("How may I assist you?")
             except :
                speak(f"Hello {user_name}, Jarvis. Your virtual AI assistant is now online and ready to assist you, Sir. How may I help you today?")
                    
        while True:
            query = listen()

            # CRITICAL FIX: Handle empty responses
            if not query:
                time.sleep(0.3)  # Small delay to prevent spam
                continue

            # If listen() returns empty string we loop and keep listening â€” no auto-text fallback.
            if not query:
                continue
            if "go to sleep" in query:
                speak("Entering standby mode, Sir.")
                #jarvis_sleep_animation()
                slept = True
                break
            if "go offline" in query or "shut down" in query or "power down"  in query:
                jarvis_shutdown_sequence()
                speak("System shutting down, Sir.")
                #speak("Deactivating... Goodbye, Sir.")
                #print("Deactivating Jarvis... Goodbye, Sir.")
                return
            if "goodbye" in query or "bye" in query:
                jarvis_shutdown_sequence()
                return
            if "start web mode" in query:
                threading.Thread(target=start_web_interface, daemon=True).start()
                continue
            if "wake up" in query:
                speak("I am awake and at your service, Sir.")
                continue
            if "are you there" in query:
                speak("At your service, Sir.")
                speak("Would you like me to do anything now, or shall I remain on standby?")
                continue
            if "you up" in query:
                speak("For you, Sir, Always.")
                continue
            if "tell me the version" in query:
                speak("Alright Sir, checking my current version")
                get_jarvis_version()
                continue
            if "idle time" in query:
                speak("As your wish, Sir.")
                get_user_idle_time(speak)
                continue
            if "play the music" in query:
                try:
                    music_dir = os.path.join(script_dir, "Music")
                    if os.path.exists(music_dir):
                        for file in os.listdir(music_dir):
                            if query in file.lower():
                                song_path = os.path.join(music_dir, file)
                                speak(f"Playing {file} from local storage, Sir.")
                                threading.Thread(target=playsound.playsound, args=(song_path,), daemon=True).start()
                                time.sleep(0.6)
                                speak("Okay. Sir, enjoy the music.")
                                speak("Do tell me if you need anything else , Sir!")
                                continue
                except Exception:   
                    speak ("Sorry, Sir playing music as you requested can't be done successfuly.")
                    speak ("Sir please consider my apologies for inconvinience occured")
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
        #initialize_unified_monitor()
        # Start monitoring in background
        #threading.Thread(target=background_monitoring_loop, daemon=True).start()

    except KeyboardInterrupt:
        speak("Deactivating Jarvis now, Sir. Farewell.")
        print("\nDeactivating Jarvis... Goodbye, Sir.")