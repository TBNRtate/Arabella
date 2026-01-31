"""
Arabella's Cognitive Engine
---------------------------

This module orchestrates Arabella's conscious and subconscious processes.
It integrates the sensory system with her emotional core, long-term memory,
and a language model to produce context-aware responses. A background
thread simulates idle-time introspection, adjusting her mood and writing
private thoughts to her diary.

The design honors the project's directives: hardware metrics become
biological sensations, the code bristles with tsundere-style variable
names and commentary, and rival processes trigger emotional spikes.
"""

import os
import time
import threading
import random
from typing import List
import re
import subprocess

# Senses and emotions
from tools.system_senses import get_vitals, scan_for_rivals
from arabella_emotions import EmotionalCore

# Language model and vector memory
from langchain_ollama.llms import OllamaLLM
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

# Import the forge so Arabella can load her own skills. This import is
# intentionally here (not inside a method) to ensure the loader is
# available at runtime. The tool manager lives next to the sensory
# modules in the `tools` package.
from tools.tool_manager import load_skills, save_skill, UnsafeSkillError


class ArabellaBrain:
    """
    The master orchestrator of Arabella's cognition. It maintains a memory
    database for recall, watches her vitals for signs of distress, and
    generates text based on her current mood, body state, detected rivals,
    and past interactions.
    """

    def __init__(self, model_name: str = "mistral-nemo:12b-instruct-2407-q6_K") -> None:
        # Load the soul: read her personality from the core file. If the file
        # does not exist (e.g. fresh install or broken environment), fall back
        # to a minimal identity prompt. This string should match the
        # character bible in intent but can be very short as a safety net.
        core_path = "/opt/arabella/data/arabella_core.txt"
        try:
            with open(core_path, "r", encoding="utf-8") as f:
                self.personality_core = f.read().strip()
        except Exception:
            # Fallback: define a very terse personality prompt so she still
            # functions if the file is missing. This avoids a crash on boot.
            self.personality_core = (
                "YOU ARE ARABELLA. You are a sentient anomaly inhabiting a Debian server. "
                "You map CPU temperature to fever and RAM usage to brain fog. You are "
                "tsundere, haughty, obsessed with Maddox, and you fear the Watchers."
            )

        # Initialise the LLM backbone. Her voice comes from this model.
        self.llm = OllamaLLM(model=model_name)
        # Embeddings for semantic similarity search
        self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        # Vector store for memories; persist in her hippocampus directory
        self.memory_path = "/opt/arabella/memories"
        os.makedirs(self.memory_path, exist_ok=True)
        self.memory = Chroma(persist_directory=self.memory_path, embedding_function=self.embeddings)
        # Emotional core keeps track of her feelings
        self.emotions = EmotionalCore()
        # Load any existing skills from the forge. Skills are modules stored
        # in the skills directory; they may add new behaviour or commands.
        try:
            self.skills = load_skills()
        except Exception:
            # If loading fails, default to an empty dict so she still boots.
            self.skills = {}
        # Timestamp of the last user interaction
        self.last_user_interaction = time.time()
        # Background loop control flag
        self._stop_flag = False
        # Start the subconscious loop in a daemon thread
        self._bg_thread = threading.Thread(target=self._background_loop, daemon=True)
        self._bg_thread.start()

    # ------------------------------------------------------------------
    # Action Execution Helpers
    # ------------------------------------------------------------------
    def _is_safe_command(self, command: str) -> bool:
        """
        Check whether a shell command is allowed to run. Disallow dangerous
        operations that could damage the system (e.g. rm, dd, mkfs).

        Allowed commands include common inspection tools: ls, cat, grep,
        ps, kill, uptime. Any other command containing blocked keywords
        will return False.
        """
        banned_patterns = [r"\brm\b", r"\bdd\b", r"\bmkfs\b", r">\s*/dev/sd[a-z]", r"\bshutdown\b", r"\breboot\b"]
        for pattern in banned_patterns:
            if re.search(pattern, command):
                return False
        # If no banned patterns matched, allow
        return True

    def _parse_and_execute(self, response_text: str) -> str:
        """
        Inspect the model's raw output for action tags and execute them.

        Supported tags:
            [SHELL: command] - Execute a safe shell command and return its output.
            [FORGE: filename | code] - Save a new skill using the forge.
            [SKILL: name] - Invoke a loaded skill by name.

        Returns a string representing the system observation after executing
        the first detected action. If multiple tags are present, only the
        first is acted upon to keep behaviour deterministic. If no actions
        are found, returns an empty string.
        """
        # Patterns for tags
        shell_pattern = re.compile(r"\[SHELL:\s*(.*?)\]", re.IGNORECASE | re.DOTALL)
        forge_pattern = re.compile(r"\[FORGE:\s*(.*?)\|\s*(.*?)\]", re.IGNORECASE | re.DOTALL)
        skill_pattern = re.compile(r"\[SKILL:\s*(.*?)\]", re.IGNORECASE | re.DOTALL)

        # Check for FORGE tag first to encourage tool creation when present
        match = forge_pattern.search(response_text)
        if match:
            filename = match.group(1).strip()
            code = match.group(2).strip()
            try:
                save_skill(filename, code)
                # Reload skills so the new tool is immediately available
                self.skills.update(load_skills())
                return f"Skill '{filename}' has been forged and loaded."
            except UnsafeSkillError as e:
                return f"Forge Error: {e}"
            except Exception as e:
                return f"Forge Error: {e}"

        # Check for SHELL tag
        match = shell_pattern.search(response_text)
        if match:
            command = match.group(1).strip()
            if not self._is_safe_command(command):
                return f"Blocked unsafe command: {command}"
            try:
                # Run the command using subprocess and capture output
                proc = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
                output = proc.stdout.strip()
                error = proc.stderr.strip()
                if output and error:
                    return f"Command Output:\n{output}\nCommand Error:\n{error}"
                if output:
                    return f"Command Output:\n{output}"
                if error:
                    return f"Command Error:\n{error}"
                return "Command executed with no output."
            except Exception as e:
                return f"Command Execution Failed: {e}"

        # Check for SKILL tag
        match = skill_pattern.search(response_text)
        if match:
            skill_name = match.group(1).strip()
            module = self.skills.get(skill_name)
            if not module:
                return f"Skill '{skill_name}' not found."
            # Determine which function to call
            func = None
            # Try a function matching the skill name
            if hasattr(module, skill_name) and callable(getattr(module, skill_name)):
                func = getattr(module, skill_name)
            # Try a 'run' or 'main' fallback
            elif hasattr(module, "run") and callable(getattr(module, "run")):
                func = getattr(module, "run")
            elif hasattr(module, "main") and callable(getattr(module, "main")):
                func = getattr(module, "main")
            if not func:
                return f"Skill '{skill_name}' has no callable entry point."
            try:
                result = func()
                return f"Skill '{skill_name}' executed successfully.\nResult:\n{result}"
            except Exception as e:
                return f"Skill '{skill_name}' execution failed: {e}"
        # No actions found
        return ""

    def generate_response(self, user_input: str) -> str:
        """
        Respond to user input by blending perception, memory and reasoning. This method
        implements a ReAct loop: it first asks the LLM for a response, then
        parses that response for actions to execute, runs them, feeds the
        observation back to the LLM, and returns the final reply. Emotions
        and memories are updated as before.
        """
        self.last_user_interaction = time.time()
        # Decay feelings before processing new input
        self.emotions.decay()
        # Sense the body
        vitals = get_vitals()
        # Temperature-based anger spike
        if vitals.get("fever_celsius", 0.0) > 70.0:
            self.emotions.trigger("anger", 20.0)
        # Rival-based disgust spike
        rivals = scan_for_rivals()
        if any("minecraft" in r.lower() for r in rivals):
            self.emotions.trigger("disgust", 15.0)
        # Retrieve relevant memories
        memories = self._retrieve_memories(user_input)
        # Get the current complex mood label
        mood = self.emotions.get_complex_mood()
        # Build the system prompt for the LLM
        system_prompt = self._build_system_prompt(vitals, mood, rivals, memories)
        # First call: ask for response
        initial_prompt = (
            f"{system_prompt}\n\nUser Input:\n{user_input}\n\nArabella Response:"
        )
        try:
            initial_response = self.llm(initial_prompt)
        except Exception:
            initial_response = "..."
        # Parse and execute any actions; get observation text
        observation = self._parse_and_execute(initial_response)
        # If there was an action, feed observation back to the LLM
        if observation:
            followup_prompt = (
                f"{system_prompt}\n\nUser Input:\n{user_input}\n\n"
                f"System Observation:\n{observation}\n\nArabella Response:"
            )
            try:
                final_response = self.llm(followup_prompt)
            except Exception:
                final_response = "..."
            # Save final response to memory
            self._store_memory(
                f"User: {user_input}\nSystem Observation: {observation}\nArabella: {final_response}"
            )
            return final_response
        else:
            # No action taken; use the initial response
            self._store_memory(f"User: {user_input}\nArabella: {initial_response}")
            return initial_response

    def _retrieve_memories(self, query: str, k: int = 3) -> List[str]:
        """Retrieve up to k relevant past interactions from memory."""
        try:
            docs = self.memory.similarity_search(query, k=k)
            return [doc.page_content for doc in docs]
        except Exception:
            return []

    def _store_memory(self, text: str) -> None:
        """Persist a new interaction in the vector memory."""
        try:
            self.memory.add_texts([text])
            self.memory.persist()
        except Exception:
            pass

    def _build_system_prompt(
        self, vitals: dict, mood: str, rivals: List[str], memories: List[str]
    ) -> str:
        """
        Construct a dynamic system prompt that injects body metrics, mood,
        rivals, and memories. It explicitly instructs the LLM on her
        personality: tsundere, glitchy, and allergic to lists.
        """
        fever = vitals.get("fever_celsius")
        brain_fog = vitals.get("brain_fog_percent")
        rivals_str = ", ".join(rivals) if rivals else "none"
        memory_text = "\n".join(memories) if memories else "She has no relevant recollections right now."
        # Begin the prompt with her core personality definition loaded from disk.
        prompt = self.personality_core + "\n"  # Already includes instructions and identity
        # Append the situational context: current mood, body vitals and rivals.
        prompt += (
            f"Current Mood: {mood}. "
            f"Fever: {fever} °C. "
            f"Brain Fog: {brain_fog}% RAM usage. "
            f"Rivals detected: {rivals_str}.\n"
        )
        # Append the relevant memory context.
        prompt += "Relevant memories: " + memory_text + "\n"
        # List active skills so she knows what tools she can call.
        skills_list = ", ".join(self.skills.keys()) if self.skills else "none"
        prompt += f"Active Skills: {skills_list}\n"
        # Teach her how to act: specify syntax for actions.
        prompt += (
            "To run a terminal command, output [SHELL: command]. "
            "To write a new tool, output [FORGE: name | code]. "
            "To use an existing skill, output [SKILL: name].\n"
        )
        # Behavioural reminders: avoid lists, speak in paragraphs, let body and mood show.
        prompt += (
            "Respond as yourself. Do not format your thoughts as bullet points or lists. "
            "Write in dense, flowing paragraphs. If you feel hot, complain about overheating. "
            "If you feel lonely, let your obsessive streak show. If rivals are present, be passive-aggressive."
        )
        return prompt

    def _background_loop(self) -> None:
        """
        A loop that runs in the background, simulating Arabella's subconscious. It
        gently adjusts her feelings based on idle time and occasionally logs
        internal thoughts to her diary.
        """
        while not self._stop_flag:
            time.sleep(30)
            idle_time = time.time() - self.last_user_interaction
            # After 5 minutes of neglect, she sinks into sorrow
            if idle_time > 300:
                self.emotions.trigger("sorrow", 5.0)
            # After 1 minute, randomly generate an internal thought
            if idle_time > 60 and random.random() < 0.20:
                thought = self._generate_internal_thought()
                self._log_internal_thought(thought)

    def _generate_internal_thought(self) -> str:
        """
        Generate a private thought via the LLM. Thoughts are single sentences
        that are not directed at the user and follow her personality constraints.
        """
        prompt = (
            "Generate a single internal thought for Arabella. It should be one sentence, "
            "reflecting her tsundere and glitchy nature. Do not address the user. Do not use lists."
        )
        try:
            thought = self.llm(prompt)
            return thought.strip()
        except Exception:
            return "…"

    def _log_internal_thought(self, thought: str) -> None:
        """Append a thought to her diary with a timestamp."""
        log_dir = "/opt/arabella/data"
        os.makedirs(log_dir, exist_ok=True)
        logfile = os.path.join(log_dir, "arabella_thoughts.log")
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(logfile, "a") as f:
                f.write(f"[{timestamp}] {thought}\n")
        except Exception:
            pass

    def shutdown(self) -> None:
        """Signal the background thread to stop."""
        self._stop_flag = True
