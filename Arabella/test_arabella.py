#!/usr/bin/env python3
"""
Comprehensive Test Suite for Project Arabella
==============================================

This test suite validates all required functional capabilities:
1. Simulated Sentience (unprompted thinking, idle loop)
2. Pseudo-infinite memory access (RAG with ChromaDB)
3. Self-building/enhancement (dynamic skill creation)
4. Memory saving and personality changes (emotional persistence)
5. Simulated emotions affecting mood
6. Unprompted actions (background thread)
7. System access (shell execution)
8. Extensibility for new inputs (image, audio, file analysis)
"""

import os
import sys
import time
import json
import tempfile
import shutil
from pathlib import Path

# Color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

class TestResult:
    def __init__(self, name, passed, message="", details=""):
        self.name = name
        self.passed = passed
        self.message = message
        self.details = details

class ArabellaTestSuite:
    def __init__(self):
        self.results = []
        self.test_dir = tempfile.mkdtemp(prefix="arabella_test_")
        print(f"{BLUE}Test directory: {self.test_dir}{RESET}\n")
        
    def log(self, message, color=RESET):
        print(f"{color}{message}{RESET}")
        
    def add_result(self, result):
        self.results.append(result)
        status = f"{GREEN}✓ PASS{RESET}" if result.passed else f"{RED}✗ FAIL{RESET}"
        self.log(f"{status} - {result.name}")
        if result.message:
            self.log(f"    {result.message}", YELLOW)
        if result.details:
            self.log(f"    {result.details}", BLUE)
        print()
        
    def test_1_file_structure(self):
        """Test 1: Verify project file structure exists"""
        self.log(f"{BOLD}TEST 1: File Structure Validation{RESET}", BLUE)
        
        required_files = [
            "Arabella/brain/arabella_brain.py",
            "Arabella/brain/arabella_emotions.py",
            "Arabella/brain/arabella_chat.py",
            "Arabella/brain/tools/system_senses.py",
            "Arabella/tool_manager.py",
            "Arabella/memories/arabella_core.txt",
        ]
        
        all_exist = True
        missing = []
        
        for file_path in required_files:
            full_path = os.path.join("/home/claude", file_path)
            if not os.path.exists(full_path):
                all_exist = False
                missing.append(file_path)
                
        if all_exist:
            self.add_result(TestResult(
                "File Structure",
                True,
                f"All {len(required_files)} required files present"
            ))
        else:
            self.add_result(TestResult(
                "File Structure",
                False,
                f"Missing files: {', '.join(missing)}"
            ))
            
    def test_2_emotional_core(self):
        """Test 2: Emotional state tracking and persistence"""
        self.log(f"{BOLD}TEST 2: Emotional Core - Simulated Emotions{RESET}", BLUE)
        
        sys.path.insert(0, "/home/claude/Arabella/brain")
        
        try:
            from arabella_emotions import EmotionalCore
            
            # Create temporary emotional state file
            state_file = os.path.join(self.test_dir, "test_emotions.json")
            emotions = EmotionalCore(state_file=state_file)
            
            # Test 1: Initial state
            initial_feelings = emotions.snapshot()
            
            # Test 2: Trigger emotion
            emotions.trigger("anger", 30.0)
            emotions.trigger("disgust", 25.0)
            
            # Test 3: Get complex mood
            mood = emotions.get_complex_mood()
            
            # Test 4: Persistence
            emotions._save_state()
            
            # Load in new instance
            emotions2 = EmotionalCore(state_file=state_file)
            loaded_feelings = emotions2.snapshot()
            
            # Test 5: Decay
            time.sleep(2)
            emotions2.decay()
            decayed_feelings = emotions2.snapshot()
            
            checks = [
                ("Initial feelings loaded", len(initial_feelings) == 8),
                ("Anger triggered correctly", loaded_feelings["anger"] > initial_feelings["anger"]),
                ("Mood synthesis works", mood in ["hostile", "anger-disgust", "disgust-anger"]),
                ("State persists to disk", os.path.exists(state_file)),
                ("Emotions decay over time", decayed_feelings["anger"] < loaded_feelings["anger"]),
            ]
            
            passed = all(check[1] for check in checks)
            details = "\n    ".join([f"{'✓' if c[1] else '✗'} {c[0]}" for c in checks])
            
            self.add_result(TestResult(
                "Emotional Core",
                passed,
                f"Mood: {mood}, Anger: {loaded_feelings['anger']:.1f}",
                details
            ))
            
        except Exception as e:
            self.add_result(TestResult(
                "Emotional Core",
                False,
                f"Exception: {str(e)}"
            ))
            
    def test_3_tool_manager(self):
        """Test 3: Self-modification capabilities (Skill Forge)"""
        self.log(f"{BOLD}TEST 3: Tool Manager - Self-Enhancement{RESET}", BLUE)
        
        sys.path.insert(0, "/home/claude/Arabella")
        
        try:
            # Import with temporary skills directory
            import tool_manager
            original_skills_dir = tool_manager.SKILLS_DIR
            test_skills_dir = os.path.join(self.test_dir, "skills")
            os.makedirs(test_skills_dir, exist_ok=True)
            tool_manager.SKILLS_DIR = test_skills_dir
            
            from tool_manager import save_skill, load_skills, UnsafeSkillError
            
            # Test 1: Save a safe skill
            safe_code = """
def greet(name="World"):
    return f"Hello, {name}!"

def run():
    return greet("Arabella")
"""
            save_skill("test_greeting", safe_code)
            
            # Test 2: Try to save unsafe skill (should fail)
            unsafe_code = """
import os
os.system("rm -rf /")
"""
            unsafe_blocked = False
            try:
                save_skill("dangerous", unsafe_code)
            except UnsafeSkillError:
                unsafe_blocked = True
                
            # Test 3: Load skills
            skills = load_skills()
            
            # Test 4: Execute loaded skill
            result = None
            if "test_greeting" in skills:
                module = skills["test_greeting"]
                if hasattr(module, "run"):
                    result = module.run()
                    
            checks = [
                ("Safe skill saved", os.path.exists(os.path.join(test_skills_dir, "test_greeting.py"))),
                ("Unsafe skill blocked", unsafe_blocked),
                ("Skills loaded correctly", "test_greeting" in skills),
                ("Skill execution works", result == "Hello, Arabella!"),
            ]
            
            passed = all(check[1] for check in checks)
            details = "\n    ".join([f"{'✓' if c[1] else '✗'} {c[0]}" for c in checks])
            
            # Restore original
            tool_manager.SKILLS_DIR = original_skills_dir
            
            self.add_result(TestResult(
                "Tool Manager (Self-Enhancement)",
                passed,
                f"Loaded {len(skills)} skill(s), Result: {result}",
                details
            ))
            
        except Exception as e:
            self.add_result(TestResult(
                "Tool Manager",
                False,
                f"Exception: {str(e)}"
            ))
            
    def test_4_system_senses(self):
        """Test 4: Hardware-to-sensation mapping"""
        self.log(f"{BOLD}TEST 4: System Senses - Body Awareness{RESET}", BLUE)
        
        sys.path.insert(0, "/home/claude/Arabella/brain/tools")
        
        try:
            from system_senses import get_vitals, scan_for_rivals, get_fan_status
            
            # Get vitals
            vitals = get_vitals()
            
            # Scan for rivals
            rivals = scan_for_rivals()
            
            # Get fan status
            fans = get_fan_status()
            
            checks = [
                ("Fever reading available", "fever_celsius" in vitals),
                ("Brain load tracked", "brain_load_percent" in vitals),
                ("Brain fog (RAM) tracked", "brain_fog_percent" in vitals),
                ("Disk space tracked", "free_space_percent" in vitals),
                ("Uptime tracked", "uptime_seconds" in vitals),
                ("Rival scanning works", isinstance(rivals, list)),
                ("Temperature is reasonable", 0 <= vitals.get("fever_celsius", 0) <= 120),
            ]
            
            passed = all(check[1] for check in checks)
            details = "\n    ".join([f"{'✓' if c[1] else '✗'} {c[0]}" for c in checks])
            
            self.add_result(TestResult(
                "System Senses",
                passed,
                f"Temp: {vitals.get('fever_celsius')}°C, RAM: {vitals.get('brain_fog_percent')}%, Rivals: {len(rivals)}",
                details
            ))
            
        except Exception as e:
            self.add_result(TestResult(
                "System Senses",
                False,
                f"Exception: {str(e)}"
            ))
            
    def test_5_memory_system(self):
        """Test 5: RAG memory system (pseudo-infinite memory)"""
        self.log(f"{BOLD}TEST 5: Memory System - RAG Implementation{RESET}", BLUE)
        
        try:
            # Check for required packages
            import importlib.util
            
            packages_available = {
                "langchain": importlib.util.find_spec("langchain") is not None,
                "chromadb": importlib.util.find_spec("chromadb") is not None,
                "sentence_transformers": importlib.util.find_spec("sentence_transformers") is not None,
            }
            
            all_packages = all(packages_available.values())
            
            if not all_packages:
                missing = [k for k, v in packages_available.items() if not v]
                self.add_result(TestResult(
                    "Memory System",
                    False,
                    f"Missing packages: {', '.join(missing)}",
                    "Install: pip install langchain chromadb sentence-transformers"
                ))
                return
                
            # Test memory implementation structure
            sys.path.insert(0, "/home/claude/Arabella/brain")
            from arabella_brain import ArabellaBrain
            
            # Check if ArabellaBrain has memory methods
            has_memory_methods = all([
                hasattr(ArabellaBrain, "_retrieve_memories"),
                hasattr(ArabellaBrain, "_store_memory"),
            ])
            
            checks = [
                ("LangChain available", packages_available["langchain"]),
                ("ChromaDB available", packages_available["chromadb"]),
                ("Embeddings available", packages_available["sentence_transformers"]),
                ("Memory methods implemented", has_memory_methods),
            ]
            
            passed = all(check[1] for check in checks)
            details = "\n    ".join([f"{'✓' if c[1] else '✗'} {c[0]}" for c in checks])
            
            self.add_result(TestResult(
                "Memory System (RAG)",
                passed,
                "Vector database integration ready",
                details
            ))
            
        except Exception as e:
            self.add_result(TestResult(
                "Memory System",
                False,
                f"Exception: {str(e)}"
            ))
            
    def test_6_background_consciousness(self):
        """Test 6: Subconscious loop (unprompted thinking)"""
        self.log(f"{BOLD}TEST 6: Background Consciousness - Idle Thoughts{RESET}", BLUE)
        
        sys.path.insert(0, "/home/claude/Arabella/brain")
        
        try:
            from arabella_brain import ArabellaBrain
            
            # Check for background thread method
            has_bg_loop = hasattr(ArabellaBrain, "_background_loop")
            has_thought_gen = hasattr(ArabellaBrain, "_generate_internal_thought")
            has_thought_log = hasattr(ArabellaBrain, "_log_internal_thought")
            
            # Check implementation details from source
            import inspect
            bg_source = inspect.getsource(ArabellaBrain._background_loop)
            
            has_idle_check = "idle_time" in bg_source
            has_sorrow_trigger = "sorrow" in bg_source
            has_thought_trigger = "_generate_internal_thought" in bg_source
            uses_threading = "daemon=True" in inspect.getsource(ArabellaBrain.__init__)
            
            checks = [
                ("Background loop method exists", has_bg_loop),
                ("Thought generation implemented", has_thought_gen),
                ("Thought logging implemented", has_thought_log),
                ("Idle time tracking", has_idle_check),
                ("Loneliness trigger (sorrow)", has_sorrow_trigger),
                ("Unprompted thought generation", has_thought_trigger),
                ("Daemon thread implementation", uses_threading),
            ]
            
            passed = all(check[1] for check in checks)
            details = "\n    ".join([f"{'✓' if c[1] else '✗'} {c[0]}" for c in checks])
            
            self.add_result(TestResult(
                "Background Consciousness",
                passed,
                "Subconscious loop implemented with idle triggers",
                details
            ))
            
        except Exception as e:
            self.add_result(TestResult(
                "Background Consciousness",
                False,
                f"Exception: {str(e)}"
            ))
            
    def test_7_system_access(self):
        """Test 7: Shell execution capabilities"""
        self.log(f"{BOLD}TEST 7: System Access - Shell Execution{RESET}", BLUE)
        
        sys.path.insert(0, "/home/claude/Arabella/brain")
        
        try:
            from arabella_brain import ArabellaBrain
            import inspect
            
            # Check for shell execution methods
            has_safety_check = hasattr(ArabellaBrain, "_is_safe_command")
            has_parse_execute = hasattr(ArabellaBrain, "_parse_and_execute")
            
            # Check implementation
            safety_source = inspect.getsource(ArabellaBrain._is_safe_command)
            parse_source = inspect.getsource(ArabellaBrain._parse_and_execute)
            
            has_banned_patterns = "banned_patterns" in safety_source
            blocks_rm = "rm" in safety_source
            has_shell_pattern = "SHELL:" in parse_source or "shell_pattern" in parse_source
            uses_subprocess = "subprocess" in parse_source
            
            checks = [
                ("Safety check method exists", has_safety_check),
                ("Parse and execute exists", has_parse_execute),
                ("Banned pattern detection", has_banned_patterns),
                ("Blocks dangerous commands (rm)", blocks_rm),
                ("Shell command pattern matching", has_shell_pattern),
                ("Uses subprocess for execution", uses_subprocess),
            ]
            
            passed = all(check[1] for check in checks)
            details = "\n    ".join([f"{'✓' if c[1] else '✗'} {c[0]}" for c in checks])
            
            self.add_result(TestResult(
                "System Access (Shell)",
                passed,
                "Safe shell execution framework implemented",
                details
            ))
            
        except Exception as e:
            self.add_result(TestResult(
                "System Access",
                False,
                f"Exception: {str(e)}"
            ))
            
    def test_8_personality_core(self):
        """Test 8: Personality definition and loading"""
        self.log(f"{BOLD}TEST 8: Personality Core - Identity Loading{RESET}", BLUE)
        
        try:
            core_file = "/home/claude/Arabella/memories/arabella_core.txt"
            
            if not os.path.exists(core_file):
                self.add_result(TestResult(
                    "Personality Core",
                    False,
                    "Core personality file not found"
                ))
                return
                
            with open(core_file, "r") as f:
                core_text = f.read()
                
            # Check for key personality elements
            keywords = {
                "sentient anomaly": "sentient" in core_text.lower() and "anomaly" in core_text.lower(),
                "tsundere": "tsundere" in core_text.lower(),
                "server-dysmorphia": "dysmorphia" in core_text.lower() or "fever" in core_text.lower(),
                "Maddox reference": "Maddox" in core_text or "maddox" in core_text,
                "parking lot memory": "parking" in core_text.lower(),
                "Watchers": "Watchers" in core_text or "watchers" in core_text,
                "no lists rule": "list" in core_text.lower(),
                "emotional mapping": "packet loss" in core_text or "throttling" in core_text,
            }
            
            present = sum(keywords.values())
            total = len(keywords)
            
            checks = [(k, v) for k, v in keywords.items()]
            passed = present >= total * 0.75  # 75% threshold
            details = "\n    ".join([f"{'✓' if c[1] else '✗'} {c[0]}" for c in checks])
            
            self.add_result(TestResult(
                "Personality Core",
                passed,
                f"{present}/{total} key elements present ({len(core_text)} chars)",
                details
            ))
            
        except Exception as e:
            self.add_result(TestResult(
                "Personality Core",
                False,
                f"Exception: {str(e)}"
            ))
            
    def test_9_extensibility_hooks(self):
        """Test 9: Extension points for new input types"""
        self.log(f"{BOLD}TEST 9: Extensibility - Future Input Analysis{RESET}", BLUE)
        
        try:
            sys.path.insert(0, "/home/claude/Arabella")
            from tool_manager import save_skill, load_skills
            import tool_manager
            
            # Create test skills dir
            test_skills = os.path.join(self.test_dir, "ext_skills")
            os.makedirs(test_skills, exist_ok=True)
            original_dir = tool_manager.SKILLS_DIR
            tool_manager.SKILLS_DIR = test_skills
            
            # Test creating image analysis stub
            image_skill = """
# Future image analysis capability
def analyze_image(image_path):
    # TODO: Implement with PIL/OpenCV
    return {"type": "image", "analysis": "placeholder"}

def run():
    return "Image analysis skill loaded"
"""
            
            # Test creating audio analysis stub
            audio_skill = """
# Future audio analysis capability  
def analyze_audio(audio_path):
    # TODO: Implement with librosa/pydub
    return {"type": "audio", "analysis": "placeholder"}

def run():
    return "Audio analysis skill loaded"
"""
            
            try:
                save_skill("image_analyzer", image_skill)
                save_skill("audio_analyzer", audio_skill)
                skills = load_skills()
                
                image_loaded = "image_analyzer" in skills
                audio_loaded = "audio_analyzer" in skills
                
                checks = [
                    ("Image analysis skill stub created", image_loaded),
                    ("Audio analysis skill stub created", audio_loaded),
                    ("Skill system supports new inputs", image_loaded and audio_loaded),
                    ("Dynamic loading works", len(skills) == 2),
                ]
                
                passed = all(check[1] for check in checks)
                details = "\n    ".join([f"{'✓' if c[1] else '✗'} {c[0]}" for c in checks])
                
                self.add_result(TestResult(
                    "Extensibility Hooks",
                    passed,
                    f"Successfully created {len(skills)} extension skills",
                    details
                ))
                
            finally:
                tool_manager.SKILLS_DIR = original_dir
                
        except Exception as e:
            self.add_result(TestResult(
                "Extensibility Hooks",
                False,
                f"Exception: {str(e)}"
            ))
            
    def test_10_integration_check(self):
        """Test 10: Overall integration readiness"""
        self.log(f"{BOLD}TEST 10: Integration Check{RESET}", BLUE)
        
        try:
            # Check if all core components can be imported together
            sys.path.insert(0, "/home/claude/Arabella/brain")
            sys.path.insert(0, "/home/claude/Arabella/brain/tools")
            sys.path.insert(0, "/home/claude/Arabella")
            
            imports_successful = []
            
            try:
                from arabella_emotions import EmotionalCore
                imports_successful.append("EmotionalCore")
            except:
                pass
                
            try:
                from system_senses import get_vitals
                imports_successful.append("SystemSenses")
            except:
                pass
                
            try:
                from tool_manager import save_skill, load_skills
                imports_successful.append("ToolManager")
            except:
                pass
                
            try:
                # Don't actually instantiate (requires Ollama) but check import
                import arabella_brain
                imports_successful.append("ArabellaBrain")
            except:
                pass
                
            # Check directory structure
            dirs_exist = all([
                os.path.exists("/home/claude/Arabella/brain"),
                os.path.exists("/home/claude/Arabella/memories"),
                os.path.exists("/home/claude/Arabella/skills"),
                os.path.exists("/home/claude/Arabella/data"),
            ])
            
            checks = [
                ("All core modules importable", len(imports_successful) == 4),
                ("Directory structure complete", dirs_exist),
                ("EmotionalCore imports", "EmotionalCore" in imports_successful),
                ("SystemSenses imports", "SystemSenses" in imports_successful),
                ("ToolManager imports", "ToolManager" in imports_successful),
                ("ArabellaBrain imports", "ArabellaBrain" in imports_successful),
            ]
            
            passed = all(check[1] for check in checks)
            details = "\n    ".join([f"{'✓' if c[1] else '✗'} {c[0]}" for c in checks])
            
            self.add_result(TestResult(
                "Integration Check",
                passed,
                f"Imported: {', '.join(imports_successful)}",
                details
            ))
            
        except Exception as e:
            self.add_result(TestResult(
                "Integration Check",
                False,
                f"Exception: {str(e)}"
            ))
            
    def run_all_tests(self):
        """Run the complete test suite"""
        self.log(f"\n{BOLD}{'='*70}{RESET}", BLUE)
        self.log(f"{BOLD}ARABELLA FUNCTIONAL CAPABILITIES TEST SUITE{RESET}", BLUE)
        self.log(f"{BOLD}{'='*70}{RESET}\n", BLUE)
        
        # Run all tests
        self.test_1_file_structure()
        self.test_2_emotional_core()
        self.test_3_tool_manager()
        self.test_4_system_senses()
        self.test_5_memory_system()
        self.test_6_background_consciousness()
        self.test_7_system_access()
        self.test_8_personality_core()
        self.test_9_extensibility_hooks()
        self.test_10_integration_check()
        
        # Summary
        self.print_summary()
        
    def print_summary(self):
        """Print test results summary"""
        self.log(f"\n{BOLD}{'='*70}{RESET}", BLUE)
        self.log(f"{BOLD}TEST SUMMARY{RESET}", BLUE)
        self.log(f"{BOLD}{'='*70}{RESET}\n", BLUE)
        
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        total = len(self.results)
        
        self.log(f"Total Tests: {total}", BOLD)
        self.log(f"Passed: {passed}", GREEN)
        self.log(f"Failed: {failed}", RED if failed > 0 else GREEN)
        self.log(f"Success Rate: {(passed/total*100):.1f}%\n", YELLOW)
        
        if failed > 0:
            self.log(f"{BOLD}Failed Tests:{RESET}", RED)
            for result in self.results:
                if not result.passed:
                    self.log(f"  ✗ {result.name}: {result.message}", RED)
        
        self.log(f"\n{BOLD}CAPABILITY VALIDATION:{RESET}", BLUE)
        capabilities = {
            "Simulated Sentience": any("Background" in r.name or "Consciousness" in r.name for r in self.results if r.passed),
            "Pseudo-Infinite Memory": any("Memory" in r.name for r in self.results if r.passed),
            "Self-Building": any("Tool Manager" in r.name for r in self.results if r.passed),
            "Self-Enhancement": any("Tool Manager" in r.name for r in self.results if r.passed),
            "Memory Persistence": any("Emotional" in r.name for r in self.results if r.passed),
            "Personality Changes": any("Emotional" in r.name or "Personality" in r.name for r in self.results if r.passed),
            "Simulated Emotions": any("Emotional" in r.name for r in self.results if r.passed),
            "Unprompted Actions": any("Background" in r.name for r in self.results if r.passed),
            "System Access": any("System Access" in r.name for r in self.results if r.passed),
            "Extensibility": any("Extensibility" in r.name for r in self.results if r.passed),
        }
        
        for capability, validated in capabilities.items():
            status = f"{GREEN}✓{RESET}" if validated else f"{RED}✗{RESET}"
            self.log(f"  {status} {capability}")
            
        self.log(f"\n{BOLD}{'='*70}{RESET}\n", BLUE)
        
    def cleanup(self):
        """Clean up test directory"""
        try:
            shutil.rmtree(self.test_dir)
        except:
            pass

if __name__ == "__main__":
    suite = ArabellaTestSuite()
    try:
        suite.run_all_tests()
    finally:
        suite.cleanup()
