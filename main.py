import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess

def is_apple_device_connected():
    try:
        # Check if an Apple device is connected with lsusb
        lsusb_result = subprocess.run(["lsusb"], capture_output=True, text=True, check=True)

        if "Apple" in lsusb_result.stdout:
            # If an Apple device is found, ensure pairing prompt is displayed to user and run ideviceinfo
            ensure_pairing()
            ideviceinfo_result = subprocess.run(["ideviceinfo"], capture_output=True, text=True, check=True)
            return ideviceinfo_result.stdout.strip()  # Return ideviceinfo output

    except subprocess.CalledProcessError:
        return None

def ensure_pairing():
    try:
        # Run debug and pairing commands (sudo usbmuxd; idevicepair pair)
        #subprocess.run(["sudo", "usbmuxd", "-f", "-d"], check=True)
        subprocess.run(["idevicepair", "pair"], check=True)

        print("Pairing started successfully")

    except subprocess.CalledProcessError as e:
        print(f"Error starting pairing: {e.stderr}")

def check_device_status():
    device_info = is_apple_device_connected()

    if device_info is not None:
        # If ideviceinfo returned valid data, then the iPhone is connected
        if "DeviceClass" in device_info:
            status_label.config(text="iPhone successfully connected")
        else:
            # Prompt the user again for pairing
            ensure_pairing()
    else:
        status_label.config(text="Please connect your iPhone")

    # Schedule the check to run again periodically
    root.after(5000, check_device_status)

def enable_backup_encryption():
    try:
        # Run idevicebackup2 to enable backup encryption
        subprocess.run(["idevicebackup2", "-i", "encryption", "on"], check=True)
        
        messagebox.showinfo("Success", "Backup encryption enabled successfully")
        
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error enabling backup encryption: {e.stderr}")

def create_backup(backup_path):
    try:
        # Create a full backup
        subprocess.run(["idevicebackup2", "backup", "--full", backup_path], check=True)
        messagebox.showinfo("Success", "Backup created successfully")

    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error creating backup: {e.stderr}")

def browse_path():
    # Select a backup path with a filedialog
    selected_path = filedialog.askdirectory()
    backup_path_entry.delete(0, tk.END)
    backup_path_entry.insert(0, selected_path)

# Main window creation
root = tk.Tk()
root.title("iPhone Connection Status")

# W x H of the window
root.geometry("600x400")

# Label to display the device connection status
status_label = tk.Label(root, text="")
status_label.pack(pady=10)

# Device detection loop
check_device_status()

# Backup Encryption Button
button = tk.Button(root, text="Enable Backup Encryption", command=enable_backup_encryption)
button.pack(pady=10)

# Entry field for backup path
backup_path_entry = tk.Entry(root, width=40)
backup_path_entry.pack(pady=10)

# Button to browse for a backup path
browse_button = tk.Button(root, text="Browse", command=browse_path)
browse_button.pack(pady=5)

# Button to create backup
create_backup_button = tk.Button(root, text="Create Backup", command=lambda: create_backup(backup_path_entry.get()))
create_backup_button.pack(pady=10)

# Tkinter event loop
root.mainloop()
