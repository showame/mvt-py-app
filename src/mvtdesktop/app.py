import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess

def main():
    widgets_to_enable = []
    
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

    def check_device_status():
        device_info = is_apple_device_connected()

        if device_info is not None:
            # If ideviceinfo returned valid data, then the iPhone is connected
            if "DeviceClass" in device_info:
                status_label.config(text="iPhone successfully connected")
                enable_widgets(widgets_to_enable)
            else:
                # Prompt the user again for pairing
                ensure_pairing()
                disable_widgets(widgets_to_enable)
        else:
            status_label.config(text="Please connect your iPhone")
            disable_widgets(widgets_to_enable)

        # Schedule the check to run again periodically
        root.after(5000, check_device_status)

    def enable_widgets(widget_list):
        for widget in widget_list:
            widget['state'] = 'normal'

    def disable_widgets(widget_list):
        for widget in widget_list:
            widget['state'] = 'disabled'

    def enable_backup_encryption():
        global encryption_enabled
        try:
            # Run idevicebackup2 to enable backup encryption
            subprocess.run(["idevicebackup2", "-i", "encryption", "on"], check=True)

            # Update the encryption status and labels
            encryption_enabled = True
            update_encryption_labels()

            messagebox.showinfo("Success", "Backup encryption enabled successfully")

        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Error enabling backup encryption: {e.stderr}")

    def update_encryption_labels():
        if encryption_enabled:
            # Encryption is enabled
            encryption_label.config(text="\u2713 Backup encryption enabled")  # Use checkmark symbol
        else:
            # Encryption is disabled
            encryption_label.config(text="\u2717 Backup encryption disabled")  # Use cross symbol

    def create_backup(backup_path):
        try:
            # Create a full backup
            subprocess.run(["idevicebackup2", "backup", "--full", backup_path], check=True)
            messagebox.showinfo("Success", "Backup created successfully!")

        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Error creating backup: {e.stderr}")

    def browse_path():
        # Select a backup path with a file dialog
        selected_path = filedialog.askdirectory()
        backup_save_path_entry.delete(0, tk.END)
        backup_save_path_entry.insert(0, selected_path)

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

    def decrypt_backup_command(backup_password_entry):
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

    # Main window
    root = tk.Tk()
    root.title("iPhone Connection Status")

    # W x H of the window
    root.geometry("700x500")

    # Label to display the device connection status
    status_label = tk.Label(root, text="")
    status_label.grid(row=0, column=0, columnspan=2, pady=10)

    # Device detection loop
    check_device_status()

    encryption_enabled = False

    # Create the label for encryption status
    encryption_label = tk.Label(root, text="")
    update_encryption_labels()
    encryption_label.grid(row=1, column=1, pady=10)

    # Backup Encryption Button
    button = tk.Button(root, text="Enable Backup Encryption", command=enable_backup_encryption)
    button.grid(row=1, column=0, pady=10)
    widgets_to_enable.append(button)

    # Entry field for backup save path
    backup_save_path_entry = tk.Entry(root, width=40)
    backup_save_path_entry.grid(row=2, column=0, padx=2, pady=10)
    widgets_to_enable.append(backup_save_path_entry)

    # Button to browse for a backup path
    browse_button = tk.Button(root, text="Browse", command=browse_path)
    browse_button.grid(row=2, column=1, padx=2, pady=10)
    widgets_to_enable.append(browse_button)

    # Backup Encryption password entry widget
    backup_password_label = tk.Label(root, text="Enter Backup Encryption Password:")
    backup_password_label.grid(row=3, column=0, padx=5, pady=10)

    backup_password_entry = tk.Entry(root, show="*")
    backup_password_entry.grid(row=3, column=1, columnspan=3, pady=10)
    widgets_to_enable.append(backup_password_entry)

    # Button to create backup
    create_backup_button = tk.Button(root, text="Create Backup", command=lambda: create_backup(backup_save_path_entry.get()))
    create_backup_button.grid(row=4, column=0, padx=3, pady=10, columnspan=3)
    widgets_to_enable.append(create_backup_button)

    # Button to save password to key file
    # TODO: manage securely the lifecycle of key file
    key_file_save_button = tk.Button(root, text="Save Password to Key File", command=lambda: save_password_to_key_file(backup_password_entry))
    key_file_save_button.grid(row=5, column=0, columnspan=3, pady=10)
    widgets_to_enable.append(key_file_save_button)

    # Decryption backup button
    # TODO: add support for decryption with a key file
    run_decrypt_backup_button = tk.Button(root, text="Decrypt Backup", command=lambda: decrypt_backup_command(backup_password_entry))
    run_decrypt_backup_button.grid(row=6, column=0, columnspan=3, pady=20)
    widgets_to_enable.append(run_decrypt_backup_button)

    # Button to run the backup check
    backup_check_button = tk.Button(root, text="Check Backup for Malware", command=check_backup)
    backup_check_button.grid(row=7, column=0, columnspan=3, pady=10)
    widgets_to_enable.append(backup_check_button)

    # Disable all widgets initially
    disable_widgets(widgets_to_enable)

    # Tkinter event loop
    root.mainloop()
