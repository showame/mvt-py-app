import tkinter as tk
from tkinter import filedialog, messagebox, font
import subprocess
from mvtdesktop.mvt_utils import *

def configure_widget(widget, **kwargs):
    default_settings = {'bg': '#dddddd'}
    default_settings.update(kwargs)
    widget.configure(**default_settings)

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MVT Desktop App")
        self.geometry("1400x500")
        self.config(bg="#dddddd")
        self.create_widgets()

    def check_device_status(self):
        device_info = is_apple_device_connected()

        if device_info is not None:
            # If ideviceinfo returned valid data, then the iPhone is connected
            if "DeviceClass" in device_info:
                self.status_label.config(text="iPhone successfully connected")
            else:
                # Prompt the user again for pairing
                ensure_pairing()
        else:
            self.status_label.config(text="Please connect your iPhone")

        # Schedule the check to run again periodically
        self.after(5000, self.check_device_status)

    def create_widgets(self):
        # Insights frame
        self.insights_frame = tk.Frame(self, width=300, height=500)
        configure_widget(self.insights_frame)
        self.insights_frame.grid(row=0, column=0, rowspan=10, sticky="nsew")
        self.insights_frame.grid_propagate(False)
        # Insights header
        self.insights_header = tk.Label(self.insights_frame, text="Insights", font=('Helvetica', 16, 'bold'))
        configure_widget(self.insights_header)
        self.insights_header.grid(row=0, column=0, padx=12, pady=20, sticky="w")
        
        # Label for iPhone connection status
        self.status_label = tk.Label(self.insights_frame, text="iPhone connection status", font=('Helvetica', 12))
        configure_widget(self.status_label)
        self.status_label.grid(row=4, column=0, columnspan=2, padx=12, pady=20)

        # Device detection loop
        self.check_device_status()

        # Thin separator line
        separator = tk.Frame(self, width=1, bg="white") 
        separator.grid(row=0, column=1, rowspan=10, pady=10, sticky="ns")

        # Main Content Frame
        self.main_content_frame = tk.Frame(self, width=1000, height=500, padx=0)
        configure_widget(self.main_content_frame)
        self.main_content_frame.grid(row=0, column=2, rowspan=10, columnspan=6)
        self.main_content_frame.grid_propagate(False)
        # Main Content Header
        self.main_content_header = tk.Label(self.main_content_frame, text="Main Workspace", font=('Helvetica', 16, 'bold'))
        configure_widget(self.main_content_header)
        self.main_content_header.grid(row=0, column=0, padx=12, pady=30, sticky="w")

        self.active_font = font.Font(underline=0)
        self.inactive_font = font.Font(underline=0)
        self.active_color = "#efefef"
        self.inactive_color = "#dddddd"

        # Buttons to switch between frames
        self.backup_creator_button = tk.Button(self.main_content_frame, text="I want to create a backup                                      ", font=self.inactive_font, bg=self.inactive_color, relief='flat', command=lambda: self.show_frame("BackupCreatorFrame"))
        self.backup_creator_button.grid(row=1, column=0, columnspan=1, sticky="ew")

        self.backup_uploader_button = tk.Button(self.main_content_frame, text="I want to upload my backup                                         ", font=self.inactive_font, bg=self.inactive_color, relief='flat', command=lambda: self.show_frame("BackupUploaderFrame"))
        self.backup_uploader_button.grid(row=1, column=1, columnspan=1, sticky="ew")

        # Thin horizontal line
        first_horizontal_separator = tk.Frame(self.main_content_frame, height=1, width=1000, bg="white")
        first_horizontal_separator.grid(row=2, column=0, columnspan=5, sticky="ew")

        self.frames = {}
        for F in (BaseFrame, BackupCreatorFrame, BackupUploaderFrame):
            frame_name = F.__name__
            frame = F(parent=self.main_content_frame, controller=self)
            self.frames[frame_name] = frame
            frame.grid(row=3, column=0, columnspan=5, sticky="nsew")

        self.show_frame("BaseFrame")

        # Thin horizontal line
        second_horizontal_separator = tk.Frame(self.main_content_frame, height=1, width=1000, bg="white")
        second_horizontal_separator.grid(row=8, column=0, columnspan=5, sticky="ew")

        self.malware_analysis_header = tk.Label(self.main_content_frame, text="Malware Analysis", font=('Helvetica', 12, 'bold'))
        configure_widget(self.malware_analysis_header)
        self.malware_analysis_header.grid(row=9, column=0, columnspan=1, padx=12, pady=10, sticky="w")
        
        self.check_backup_button = tk.Button(self.main_content_frame, text="Run Malware analysis on Backup", command=check_backup)
        self.check_backup_button.grid(row=10, column=0, columnspan=1, padx=10, pady=20, sticky='w')

    def show_frame(self, frame_name):
        if frame_name == "BackupCreatorFrame":
            self.backup_creator_button.config(font=self.active_font, bg=self.active_color)
            self.backup_uploader_button.config(font=self.inactive_font, bg=self.inactive_color)
        elif frame_name == "BackupUploaderFrame":
            self.backup_creator_button.config(font=self.inactive_font, bg=self.inactive_color)
            self.backup_uploader_button.config(font=self.active_font, bg=self.active_color)
        frame = self.frames[frame_name]
        frame.tkraise()

class BaseFrame(tk.Frame):
    global selected_path
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        configure_widget(self)
        self.create_widgets()

    def create_widgets(self):
        pass

    def browse_path(self):
        selected_path = filedialog.askdirectory()
        if selected_path:
            self.backup_save_path_entry.delete(0, tk.END)
            self.backup_save_path_entry.insert(0, selected_path)

class BackupCreatorFrame(BaseFrame):
    def create_widgets(self):
        self.backup_creator_header = tk.Label(self, text="Backup Creator", font=('Helvetica', 12, 'bold'))
        configure_widget(self.backup_creator_header)
        self.backup_creator_header.grid(row=0, column=0, columnspan=1, padx=12, pady=10, sticky="w")
        
        # Create the label for encryption status
        self.encryption_label = tk.Label(self, text="")
        self.encryption_label.grid(row=1, column=0, padx=12, pady=10)
        self.update_encryption_label()

        # Backup Encryption Button
        button = tk.Button(self, text="Enable Backup Encryption", command=enable_backup_encryption)
        button.grid(row=1, column=1, pady=10)

        # Entry field for backup save path
        self.backup_save_path_entry = tk.Entry(self, width=40)
        self.backup_save_path_entry.grid(row=2, column=0, padx=5, pady=10)
        self.backup_save_path_entry['state'] = 'normal'

        # Button to browse for a backup path
        browse_button = tk.Button(self, text="Browse backup save path", command=self.browse_path)
        browse_button.grid(row=2, column=1, padx=5, pady=10)

        # Backup Encryption password entry widget
        backup_password_label = tk.Label(self, text="Enter Backup Encryption Password:")
        backup_password_label.grid(row=3, column=0, padx=30, pady=10)

        backup_password_entry = tk.Entry(self, show="*")
        backup_password_entry.grid(row=3, column=1, columnspan=3, pady=10)

        # Button to create backup
        create_backup_button = tk.Button(self, text="Create Backup", command=lambda: create_backup(self.backup_save_path_entry.get()))
        create_backup_button.grid(row=4, column=0, padx=3, pady=10, columnspan=3)

    def update_encryption_label(self):
        # Update the label based on the encryption status
        if encryption_enabled:
            # Encryption is enabled -> checkmark symbol
            self.encryption_label.config(text="\u2713 Backup encryption enabled")
        else:
            # Encryption is disabled -> cross symbol
            self.encryption_label.config(text="\u2717 Backup encryption disabled")

class BackupUploaderFrame(BaseFrame):
    def create_widgets(self):
        self.backup_uploader_header = tk.Label(self, text="Backup Uploader", font=('Helvetica', 12, 'bold'))
        configure_widget(self.backup_uploader_header)
        self.backup_uploader_header.grid(row=0, column=0, columnspan=1, padx=12, pady=10, sticky="w")

        #self.upload_path_label = tk.Label(self, text="Backup upload path:")
        self.upload_path_entry = tk.Entry(self, width=40)
        self.upload_path_entry.grid(row=1, column=0, padx=5, pady=10)
        self.upload_path_entry['state'] = 'normal'
        
        self.upload_browse_button = tk.Button(self, text="Browse", command=self.browse_path)
        self.upload_browse_button.grid(row=1, column=1, padx=5, pady=10)
        self.upload_browse_button['state'] = 'normal'

        backup_password_label = tk.Label(self, text="Enter Backup Encryption Password:")
        backup_password_label.grid(row=2, column=0, padx=5, pady=10, sticky='w')

        self.backup_password_entry = tk.Entry(self, show="*")
        self.backup_password_entry.grid(row=2, column=1, columnspan=2, pady=10, sticky='w')
        
        self.save_password_button = tk.Button(self, text="Save Password to Key File", command=lambda: save_password_to_key_file(self.backup_password_entry))
        self.save_password_button.grid(row=2, column=4, padx=5, pady=10)

        self.decrypt_backup_button = tk.Button(self, text="Decrypt Backup", command=lambda: decrypt_backup(self.backup_password_entry, self.upload_path_entry))
        self.decrypt_backup_button.grid(row=3, column=0, padx=5, pady=20)

def main():
    app = Application()
    app.mainloop()