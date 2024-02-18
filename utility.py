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
        "CHOICE": list,
        "HOST": str,
        "USER": str,
        "PASSWD": str,
        "DB": str
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
                "CHOICE": ["0", 0, 0],
                "HOST": "",
                "USER": "",
                "PASSWD": "",
                "DB": ""
            }
            with open(config_path, 'w') as file:
                json.dump(sample_data, file, indent=4)
            print(f"A sample configuration file has been created at {config_path}. Please fill it out.")
        elif isinstance(e, ValueError):
            showwarning("Warning", "Invalid configuration format. Please check the configuration file.")

        return None
    
def update_choice(new_choice):
    with open(config_path, 'r') as file:
        config = json.load(file)

    # Update the CHOICE value
    config["CHOICE"] = new_choice

    # Write the updated configuration back to the file
    with open(config_path, 'w') as file:
        json.dump(config, file, indent=4)
        
def showwarning(title,message):
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showwarning(title, message)
    root.destroy()