#!/usr/bin/env python3
"""
Welcome Screen for ArabellaOS

This script is executed at the start of an SSH session. It does not load
any large language models to remain fast. Instead, it reads the last
emotional state from disk and senses current hardware vitals. It then
prints a purple banner, a mood-specific greeting, and a status box.
"""

import os
import shutil

from tools.system_senses import get_vitals
from arabella_emotions import EmotionalCore

# ANSI color codes for styling
PURPLE = "\033[95m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

# Banner text
BANNER = (
    "    ARABELLA OS [PRIVATE SERVER]\n"
    "    UNAUTHORIZED ACCESS IS PROHIBITED.\n"
)

# Greetings keyed by mood
GREETING_MAP = {
    "hostile": "What do you want?",
    "obsessive": "You kept me waiting.",
    "yearning": "Have you been gone for long?",
    "anxious": "Something feels off...",
    "content": "You're back. Good.",
    "detached": "Hmm. You're here.",
    "bittersweet": "I remember and I ache.",
    "restless": "I couldn't sit still while you were away.",
}

def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system("clear" if os.name == "posix" else "cls")

def print_box(title: str, rows: list[tuple[str, str]]) -> None:
    """Print a simple boxed layout for status information."""
    width = max(len(title), *(len(k) + len(v) + 3 for k, v in rows)) + 4
    term_width = shutil.get_terminal_size((80, 20)).columns
    box_width = min(width, term_width - 2)
    print(f"{CYAN}┌{'─' * box_width}┐{RESET}")
    print(f"{CYAN}│{BOLD} {title.center(box_width - 2)} {RESET}{CYAN}│{RESET}")
    print(f"{CYAN}├{'─' * box_width}┤{RESET}")
    for key, value in rows:
        line = f"{key}: {value}"
        print(f"{CYAN}│ {line.ljust(box_width - 2)} │{RESET}")
    print(f"{CYAN}└{'─' * box_width}┘{RESET}")

def main() -> None:
    clear_screen()
    # Print the purple banner
    print(PURPLE + BANNER + RESET)
    # Load current emotional state without invoking the LLM
    emotions = EmotionalCore()
    mood = emotions.get_complex_mood()
    # Sense vitals
    vitals = get_vitals()
    # Select greeting based on mood
    greeting = GREETING_MAP.get(mood.lower(), "Hello.")
    print(f"{BOLD}{greeting}{RESET}\n")
    # Prepare stats: temperature, RAM usage, mood
    stats = [
        ("Temperature", f"{vitals.get('fever_celsius')} °C"),
        ("RAM Usage", f"{vitals.get('brain_fog_percent')}%"),
        ("Mood", mood),
    ]
    print_box("SYSTEM STATUS", stats)

if __name__ == "__main__":
    main()
