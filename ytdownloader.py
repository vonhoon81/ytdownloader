import tkinter as tk
from tkinter import messagebox, messagebox, filedialog
import yt_dlp
import re
import os
import json
import ttkbootstrap as ttk
import webbroswer

def sanitize_filename(filename):
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
    return sanitized

def download_video():
    url = url_entry.get()
    download_dir = download_dir_entry.get()
    selected_video_format = video_format_var.get()
    selected_audio_format = audio_format_var.get()

    video_format_code = selected_video_format.split(":")[0].strip() # Get just ID before colon
    audio_format_code = selected_audio_format.split(":")[0].strip()

    try:

        ydl_opts = {
            'format': f"{video_format_code}+{audio_format_code}/best[ext=mp4]/best",
            'outtmpl': f"{download_dir}/%(title)s.%(ext)s",  # Download dir
            'noplaylist': True,
            'progress_hooks': [on_progress_ytdlp],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            progress_label.config(text=f"Download Progress: Starting...")
            progress_label.pack()

            info_dict = ydl.extract_info(url, download=True) # Download happens here with all postprocessing
            filename = ydl.prepare_filename(info_dict) # Get the final filename after all postprocessing is done by ytdlp

            print("Download completed!")
            progress_label.pack_forget()
            add_to_history(filename)  # Add to history
            url_entry.delete(0, tk.END)  # Clear URL entry

    except yt_dlp.utils.DownloadError as e:
        print(f"An error occurred: {str(e)}")
        progress_label.pack_forget()
        messagebox.showerror("Error", str(e))


def on_progress_ytdlp(d):
    if d['status'] == 'downloading':
        progress_percent = d['_percent_str']
        progress_label.config(text=f"Download Progress: {progress_percent}")
        window.update()

def browse_directory():
    download_dir = filedialog.askdirectory(initialdir=os.getcwd())
    if download_dir:
        download_dir_entry.delete(0, tk.END)
        download_dir_entry.insert(0, download_dir)

def add_to_history(filename):
    if os.path.exists("download_history.json"):
        with open("download_history.json", "r") as file:
            history = json.load(file)
    else:
        history = []

    history.append(filename)

    with open("download_history.json", "w") as file:
        json.dump(history, file)

    history_listbox.delete(0, tk.END)
    for video in history:
        history_listbox.insert(tk.END, video)

def check_formats():
    url = url_entry.get()
    try:
        with yt_dlp.YoutubeDL({'noplaylist': True}) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            available_formats = info_dict['formats']

            video_formats = []
            audio_formats = []

            for fmt in available_formats:
                if fmt.get('vcodec') != 'none':
                    format_note = fmt.get('format_note', "N/A") 
                    filesize = fmt.get('filesize') # get filesize to display to the user, might not be available so we need to handle the case
                    filesize_approx = f" (~{filesize_to_human_readable(filesize)})" if filesize else ""
                    video_formats.append(f"{fmt['format_id']}: {format_note} {filesize_approx}") # append format to list

                if fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':
                    format_note = fmt.get('format_note', "N/A") # Default for audio as well
                    filesize = fmt.get('filesize')
                    filesize_approx = f" (~{filesize_to_human_readable(filesize)})" if filesize else ""

                    audio_formats.append(f"{fmt['format_id']}: {format_note} {filesize_approx}")

            if video_formats:
                default_video = next((fmt for fmt in video_formats if "248" in fmt), video_formats[0])
                video_format_var.set(default_video)
                video_format_dropdown['values'] = video_formats
            else:
                print("no video format found!")

            if audio_formats:
                default_audio = next((fmt for fmt in audio_formats if "251" in fmt), audio_formats[0])
                audio_format_var.set(default_audio)
                audio_format_dropdown['values'] = audio_formats
            else:
                print("no video format found!")
                
    except yt_dlp.utils.DownloadError as e:
        messagebox.showerror("Error Checking Formats", str(e))

def filesize_to_human_readable(filesize_bytes): #helper function to better display the filesize to the user in the comboboxes
    if filesize_bytes < 1024:
        return f"{filesize_bytes}B"
    elif filesize_bytes < 1024 * 1024:
        return f"{filesize_bytes / 1024:.2f}KB"
    elif filesize_bytes < 1024 * 1024 * 1024:
        return f"{filesize_bytes / (1024 * 1024):.2f}MB"
    else:
        return f"{filesize_bytes / (1024 * 1024 * 1024):.2f}GB"


def open_video(event):
    selected_video = history_listbox.get(history_listbox.curselection())
    if os.path.exists(selected_video):
        webbrowser.open(selected_video) # Or use webbrowser.open if needed
    else:
        history_listbox.itemconfig(history_listbox.curselection(), bg='red')


# --- GUI Setup (using tkbootstrap) ---
window = ttk.Window(themename="litera")
window.title("ytdownloader")
window.update_idletasks()
window.geometry(f"{int(window.winfo_screenwidth() * 0.5)}x{int(window.winfo_screenheight() * 0.5)}") # make window bigger


url_frame = ttk.Frame(window)
url_frame.pack(pady=5)

url_label = ttk.Label(url_frame, text="Enter YouTube URL:")
url_label.pack(side=tk.LEFT)

url_entry = ttk.Entry(url_frame, width=50)
url_entry.pack(side=tk.LEFT, padx=(5,0))

check_formats_button = ttk.Button(url_frame, text="Check Formats", command=check_formats)
check_formats_button.pack(side=tk.LEFT, padx=5) # check button next to url input

# Download Directory
download_dir_frame = ttk.Frame(window)
download_dir_frame.pack(pady=5)

download_dir_label = ttk.Label(download_dir_frame, text="Download Directory:")
download_dir_label.pack(side=tk.LEFT)

# Format Dropdowns
format_frame = ttk.Frame(window)
format_frame.pack(pady=5)

video_format_var = tk.StringVar()
video_format_dropdown = ttk.Combobox(format_frame, textvariable=video_format_var, state="readonly", width = 20) #read only so user can't type in the dropdowns
video_format_dropdown.pack(side=tk.LEFT)

audio_format_var = tk.StringVar()
audio_format_dropdown = ttk.Combobox(format_frame, textvariable=audio_format_var, state="readonly", width = 20)
audio_format_dropdown.pack(side=tk.LEFT, padx = 5)

download_dir_entry = ttk.Entry(download_dir_frame, width=50)
download_dir_entry.insert(0, os.getcwd())  # Default download directory
download_dir_entry.pack(side=tk.LEFT, padx=5)

browse_button = ttk.Button(download_dir_frame, text="Browse", command=browse_directory)
browse_button.pack(side=tk.LEFT)

# Checkboxes (Added back)
checkbox_frame = ttk.Frame(window)
checkbox_frame.pack(pady=5)

mp4_var = tk.IntVar() # No longer necessary since output is mp4 by default
mp3_var = tk.IntVar()
mp3_checkbox = ttk.Checkbutton(checkbox_frame, text="Save as MP3", variable=mp3_var)
mp3_checkbox.pack(side=tk.LEFT)  # Place checkbox in frame

download_button = ttk.Button(window, text="Download", command=download_video)
download_button.pack(pady=5)

progress_label = ttk.Label(window, text="")

history_label = ttk.Label(window, text="Download History:")
history_label.pack()

history_listbox = tk.Listbox(window, width=50)
history_listbox.pack()
history_listbox.bind("<Double-Button-1>", open_video)  # Double-click to open

window.mainloop()
