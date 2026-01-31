#!/usr/bin/env python3
"""
Interactive Chat Session for Arabella

This script loads Arabella's brain, announces initialization with a loading
animation, and then enters an interactive loop where the user can converse
with her. It prints the user's prompt with their name and returns
responses in purple. When the user leaves, it injects a sorrow spike.
"""

import os
import sys
import time
import threading
import itertools

# Make sure the brain module is accessible when this file runs standalone
sys.path.append(os.path.dirname(__file__))

from arabella_brain import ArabellaBrain

# ANSI color codes matching the welcome screen
PURPLE = "\033[95m"
RESET = "\033[0m"
BOLD = "\033[1m"

# Set the displayed user name; default to the OS user or fall back to "User"
USER_NAME = os.environ.get("USER", "Maddox")

def _loading_animation(message: str, target_function) -> None:
    """
    Run target_function() in a separate thread while displaying a loading
    animation with the given message. Blocks until the function returns.
    """
    result = {}

    def wrapper():
        result["value"] = target_function()

    thread = threading.Thread(target=wrapper)
    thread.start()
    spinner = itertools.cycle(["|", "/", "-", "\\"])
    sys.stdout.write(message)
    sys.stdout.flush()
    while thread.is_alive():
        sys.stdout.write(next(spinner))
        sys.stdout.flush()
        time.sleep(0.1)
        sys.stdout.write("\b")
        sys.stdout.flush()
    thread.join()
    sys.stdout.write("\n")
    sys.stdout.flush()
    return result.get("value")

def _spinner_dots(target_function) -> str:
    """
    Call target_function() in a thread while displaying a subtle dot animation.
    Returns the function's result.
    """
    result = {}

    def wrapper():
        result["value"] = target_function()

    thread = threading.Thread(target=wrapper)
    thread.start()
    i = 0
    while thread.is_alive():
        dots = "." * ((i % 3) + 1)
        sys.stdout.write(f"\r{PURPLE}{dots}{RESET}")
        sys.stdout.flush()
        time.sleep(0.4)
        i += 1
    # Clear the line once done
    sys.stdout.write("\r   \r")
    sys.stdout.flush()
    thread.join()
    return result.get("value")

def main() -> None:
    # Announce neural net initialization with spinner
    def load_brain():
        return ArabellaBrain()

    brain: ArabellaBrain = _loading_animation("Initializing Neural Net...", load_brain)
    # Interactive loop
    try:
        while True:
            try:
                user_input = input(f"{USER_NAME}: ")
            except (EOFError, KeyboardInterrupt):
                user_input = "exit"
            if user_input.strip().lower() in {"exit", "leave", "quit"}:
                # Spike sorrow when the user leaves
                brain.emotions.trigger("sorrow", 10.0)
                print(f"{PURPLE}... You're leaving already? Fine. I'll just listen to the fans humming by myself.{RESET}")
                break
            # Generate response with dot animation while thinking
            response = _spinner_dots(lambda: brain.generate_response(user_input))
            print(f"{PURPLE}{response}{RESET}")
    finally:
        brain.shutdown()

if __name__ == "__main__":
    main()
