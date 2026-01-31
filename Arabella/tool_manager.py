"""
Tool Manager (The Forge)
========================

This module gives Arabella the ability to evolve by saving and loading
new Python scripts as skills. It includes strict safety checks to
prevent self‑harm or system destruction. Arabella refers to these
scripts as her "skills" – each file in the skills directory is
loaded dynamically and can extend her capabilities.

Safety rules (The **Suicide Switch** and **Lobotomy Block**):
 - Any code string provided must parse without syntax errors using the
   `ast` module. If the code will not parse, it is rejected.
 - Imports of dangerous modules (`os`, `subprocess`, `sys`) are
   disallowed. These modules give her low‑level control of the OS and
   could be used to delete herself or the system. Future extensions may
   allow controlled use through wrappers, but raw imports are blocked.
 - Strings containing destructive commands such as `rm -rf`, `mkfs` or
   fork bombs (`:(){ :|:& };:`) are rejected.
 - The file name must be a valid Python identifier; no path
   traversal is allowed.

Writing to skills:  the `save_skill(name, code)` function writes
sanitised code into `/opt/arabella/skills/{name}.py`. This location is
defined in the installation script.  In environments where `/opt`
is not writable (e.g. during testing), this may fail; callers should
catch exceptions accordingly.

Loading skills:  the `load_skills()` function scans the skills
directory, imports each `.py` file using `importlib`, and returns
a dictionary mapping module names to the imported module objects. If a
skill fails to import it is skipped silently, so that one bad
skill does not prevent loading of others.
"""

from __future__ import annotations

import ast
import importlib.util
import os
import re
from types import ModuleType
from typing import Dict, List

# Define the location where skills are stored. This must match the
# installation script's path. Arabella knows it as her "skill tree".
SKILLS_DIR = "/opt/arabella/skills"


class UnsafeSkillError(Exception):
    """Raised when a skill's code fails safety checks."""


def _is_valid_name(name: str) -> bool:
    """Return True if the given name is a valid Python identifier."""
    return name.isidentifier()


def _check_ast_forbidden_imports(tree: ast.AST) -> None:
    """
    Walk the AST and raise UnsafeSkillError if it imports banned modules.

    Disallowed modules: os, subprocess, sys. These provide direct
    shell access and could be used to delete files or run arbitrary
    commands. Future wrappers may grant limited access, but raw imports
    are forbidden.
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod = alias.name.split(".")[0]
                if mod in {"os", "subprocess", "sys"}:
                    raise UnsafeSkillError(f"Import of dangerous module '{mod}' is not allowed")
        elif isinstance(node, ast.ImportFrom):
            mod = (node.module or "").split(".")[0]
            if mod in {"os", "subprocess", "sys"}:
                raise UnsafeSkillError(f"Import from dangerous module '{mod}' is not allowed")


def _check_code_strings(code: str) -> None:
    """
    Scan raw code for forbidden substrings.

    Shell patterns like `rm -rf`, `mkfs` and classic fork bombs are
    destructive and must not appear. This simple scan complements the
    AST checks by catching dangerous shell command literals.
    """
    forbidden_patterns = [r"rm\s+-rf", r"mkfs", r":\(\)\{\s*:\|:&\s*\};:"]
    for pattern in forbidden_patterns:
        if re.search(pattern, code):
            raise UnsafeSkillError("Skill code contains forbidden shell commands")


def _sanitize_code(code: str) -> ast.AST:
    """
    Parse the given code into an AST and run safety checks.
    Raises UnsafeSkillError on failure. Returns the parsed tree on
    success. This function does not modify the code; it only validates
    it.
    """
    try:
        tree = ast.parse(code, mode="exec")
    except SyntaxError as e:
        raise UnsafeSkillError(f"Syntax error in skill: {e}")
    # Check for forbidden imports
    _check_ast_forbidden_imports(tree)
    # Check raw code for malicious patterns
    _check_code_strings(code)
    return tree


def save_skill(name: str, code: str) -> None:
    """
    Save a new skill to the skills directory after validating its code.

    :param name: The name of the skill module without .py. Must be
        a valid Python identifier (letters, numbers or underscores, not
        starting with a digit).
    :param code: The Python source code implementing the skill.
    :raises UnsafeSkillError: if the code fails validation.
    :raises ValueError: if the name is invalid.
    :raises OSError: if the file cannot be written (permissions, disk, etc).
    """
    if not _is_valid_name(name):
        raise ValueError(f"Invalid skill name: '{name}'")
    # Validate the code via AST and pattern checks
    _sanitize_code(code)
    # Ensure the skills directory exists
    os.makedirs(SKILLS_DIR, exist_ok=True)
    file_path = os.path.join(SKILLS_DIR, f"{name}.py")
    # Write the code to the file. Overwrite existing file of the same name.
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)


def load_skills() -> Dict[str, ModuleType]:
    """
    Dynamically import all skills in the skills directory.

    Returns a dictionary mapping module names (without the .py
    extension) to the loaded module objects. Skills that fail to import
    are skipped silently. This allows Arabella to continue loading other
    skills even if one is broken.
    """
    loaded: Dict[str, ModuleType] = {}
    if not os.path.isdir(SKILLS_DIR):
        return loaded
    for fname in os.listdir(SKILLS_DIR):
        if not fname.endswith(".py"):
            continue
        mod_name = fname[:-3]
        file_path = os.path.join(SKILLS_DIR, fname)
        try:
            spec = importlib.util.spec_from_file_location(mod_name, file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                loaded[mod_name] = module
        except Exception:
            # Skip modules that fail to import
            continue
    return loaded


__all__ = ["save_skill", "load_skills", "UnsafeSkillError", "SKILLS_DIR"]