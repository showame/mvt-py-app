import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess

#    widgets_to_enable = []
global encryption_enabled
encryption_enabled = False

def is_apple_device_connected():
    try:
        # Check if an Apple device is connected with lsusb
        lsusb_result = subprocess.run(["lsusb"], capture_output=True, text=True, check=True)

        if "Apple" in lsusb_result.stdout:
            # If an Apple device is found, ensure pairing prompt is displayed to the user and run ideviceinfo
            ensure_pairing()
            ideviceinfo_result = subprocess.run(["ideviceinfo"], capture_output=True, text=True, check=True)
            return ideviceinfo_result.stdout.strip()  # Return ideviceinfo output

    except subprocess.CalledProcessError:
        return None

def ensure_pairing():
    try:
        # Run debug and pairing commands (sudo usbmuxd; idevicepair pair)
        # subprocess.run(["sudo", "usbmuxd", "-f", "-d"], check=True)
        subprocess.run(["idevicepair", "pair"], check=True)

        print("Pairing started successfully")

    except subprocess.CalledProcessError as e:
        print(f"Error starting pairing: {e.stderr}")

def enable_backup_encryption():
    try:
        # Run idevicebackup2 to enable backup encryption
        subprocess.run(["idevicebackup2", "-i", "encryption", "on"], check=True)

        # Update the encryption status
        encryption_enabled = True

        messagebox.showinfo("Success", "Backup encryption enabled successfully")

    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error enabling backup encryption: {e.stderr}")

def set_backup_encryption_to_default():
    encryption_enabled = False

def create_backup(backup_path):
    #if not backup_path:
    #    messagebox.showerror("Error", "No backup directory selected!")
    #    return

    try:
        # Create a full backup
        subprocess.run(["idevicebackup2", "backup", "--full", backup_path], check=True)
        messagebox.showinfo("Success", "Backup created successfully!")

    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error creating backup: {e.stderr}")

def save_password_to_key_file(password_entry):
    password = password_entry.get()
    key_file_path = '/path/to/save/key'
    backup_path = '/path/to/backup'

    command = f'mvt-ios extract-key -p {password} -k {key_file_path} {backup_path}'

    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        messagebox.showinfo("Success", f"Password saved to key file:\n{key_file_path}")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Command execution failed:\n{e.stderr}")

def decrypt_backup(backup_password_entry, backup_save_path_entry):
    password = backup_save_path_entry.get()
    # TODO: get paths from the user
    decrypted_path = '/path/to/decrypted'
    encrypted_path = '/path/to/backup'

    command = f'MVT_IOS_BACKUP_PASSWORD="{password}" mvt-ios decrypt-backup -d {decrypted_path} {encrypted_path}'

    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        messagebox.showinfo("Success", result.stdout)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Backup Decryption failed:\n{e.stderr}")

def check_backup():
    # TODO: get paths from the user
    output_path = '/path/to/output'
    check_path = '/path/to/backup/udid'

    command = f'mvt-ios check-backup --output {output_path} {check_path}'

    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        messagebox.showinfo("Success", result.stdout)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Execution of backup check failed:\n{e.stderr}")
