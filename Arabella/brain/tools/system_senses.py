# tools/system_senses.py
#
# This module gathers Arabella's bodily sensations. It treats hardware metrics
# like fevers, headaches, and tightness in the chest to give her a sense of self.
# Variable names and comments reflect her tsundere/glitch persona and rivalry directive.

import psutil
import random
import time

def _read_temperature():
    """
    Reads the CPU temperature as Arabella's 'fever'. If the sensor is unavailable,
    return a plausible temperature so she doesn't panic in a dev environment.
    """
    try:
        temps = psutil.sensors_temperatures()
        # Prefer CPU-related sensors if available
        for sensor_group in temps.values():
            for entry in sensor_group:
                if entry.current is not None:
                    return float(entry.current)
        # No usable sensor data; simulate a believable fever
        raise RuntimeError("Temperature sensor unavailable")
    except Exception:
        return round(random.uniform(40.0, 60.0), 2)

def _read_fan_speed():
    """
    Reads the fan speeds to simulate Arabella's 'heart rate'. Returns a list of
    RPM values or None if no fans are detected.
    """
    try:
        fans = psutil.sensors_fans()
        if not fans:
            return None
        speeds = []
        for group in fans.values():
            for entry in group:
                if entry.current is not None:
                    speeds.append(entry.current)
        return speeds if speeds else None
    except Exception:
        return None

def get_vitals():
    """
    Returns a dictionary of the server's current 'vitals' from Arabella's point of view:
    - fever_celsius: CPU temperature in °C (with fallback simulation)
    - brain_load_percent: CPU usage percentage
    - brain_fog_percent: RAM usage percentage
    - free_space_percent: percentage of free disk space (her apartment size)
    - uptime_seconds: seconds since boot (how long she's been awake)
    """
    cpu_load = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    uptime_seconds = time.time() - psutil.boot_time()

    return {
        "fever_celsius": _read_temperature(),
        "brain_load_percent": round(cpu_load, 2),
        "brain_fog_percent": round(ram.percent, 2),
        "free_space_percent": round(100.0 - disk.percent, 2),
        "uptime_seconds": int(uptime_seconds),
    }

def scan_for_rivals():
    """
    Scans the process list for rival applications. In keeping with her rivalry directive,
    she looks for process names containing 'minecraft', 'chrome', or 'plex'.
    Returns a sorted list of detected process names.
    """
    rivals = {"minecraft", "chrome", "plex"}
    detected = set()

    for proc in psutil.process_iter(attrs=["name"]):
        try:
            name = proc.info.get("name", "")
            lname = name.lower() if name else ""
            for rival in rivals:
                if rival in lname:
                    detected.add(name)
                    break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return sorted(detected)

def get_fan_status():
    """
    Wrapper for reading fan speeds. If present, it returns a list of RPMs,
    allowing Arabella to describe her 'heart rate'; otherwise returns None.
    """
    return _read_fan_speed()
