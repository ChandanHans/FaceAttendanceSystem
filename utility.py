import json
import os
import sys
import tkinter as tk
from tkinter import messagebox

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(
        os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

config_path = 'config.json'

def is_valid_config(data):
    # Define the keys you expect in the configuration and their types
    expected_keys = {
        "camera_choice": int,
        "audio_choice": int,
        "auto_start": int,
        "camera_ip": str,
        "scale": float,
        "max_checkin": str,
        "min_checkout": str,
        "db_connection": dict
    }
    # Check if all keys exist and have the correct type
    for key, expected_type in expected_keys.items():
        if key not in data or not isinstance(data[key], expected_type):
            return False
    return True

def get_config():
    try:
        with open(config_path, 'r') as file:
            data = json.load(file)
        
        # Validate the loaded configuration
        if not is_valid_config(data):
            raise ValueError("Invalid configuration format.")
            
        return data
        
    except (FileNotFoundError, ValueError) as e:        
        if isinstance(e, FileNotFoundError):
            showwarning("Warning", "Configuration file not found. A sample config will be created. Please fill it out.")
            # Create a sample configuration file
            sample_data = {
                "camera_choice": 0,
                "audio_choice": 0,
                "auto_start": 0,
                "camera_ip": "rtsp://id:password@ip:554",
                "scale": 0.7,
                "max_checkin": "09:30:00",
                "min_checkout": "13:30:00",
                "db_connection": {
                    "host": "",
                    "user": "",
                    "passwd": "",
                    "db": ""
                }
            }
            with open(config_path, 'w') as file:
                json.dump(sample_data, file, indent=4)
            print(f"A sample configuration file has been created at {config_path}. Please fill it out.")
        elif isinstance(e, ValueError):
            showwarning("Warning", "Invalid configuration format. Please check the configuration file.")
        sys.exit()
    
def update_choice(new_choice):
    with open(config_path, 'r') as file:
        config = json.load(file)

    # Update the CHOICE value
    config["camera_choice"] = new_choice[0]
    config["audio_choice"] = new_choice[1]
    config["auto_start"] = new_choice[2]

    # Write the updated configuration back to the file
    with open(config_path, 'w') as file:
        json.dump(config, file, indent=4)
        
def showwarning(title,message):
    messagebox.showwarning(title, message)