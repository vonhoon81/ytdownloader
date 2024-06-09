import tkinter as tk
from tkinter import ttk, messagebox
from pytube import YouTube
import json
import os
import re

def sanitize_filename(filename):
    # Remove invalid characters from the filename
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
    return sanitized

def download_video():
    url = url_entry.get()
    try:
        # Show the progress label
        progress_label.pack()
        # Create a YouTube object
        video = YouTube(url, on_progress_callback=on_progress)

        # Get the highest resolution stream
        stream = video.streams.get_highest_resolution()

        # Sanitize the video title to create a valid filename
        filename = sanitize_filename(video.title) + ".mp4"

        # Download the video
        print(f"Downloading: {filename}")
        stream.download(filename=filename)
        print("Download completed!")

        # Hide the progress label after download completion
        progress_label.pack_forget()

        # Add the video to the history
        add_to_history(filename)

        # Clear the URL entry
        url_entry.delete(0, tk.END)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        progress_label.pack_forget()  # Hide the label if an error occurs
        messagebox.showerror("Error", str(e))  # Show error message as a popup

def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    progress_percent = (bytes_downloaded / total_size) * 100
    progress_label.config(text=f"Download Progress: {progress_percent:.2f}%")
    window.update()

def add_to_history(filename):
    # Load the existing history from the JSON file
    if os.path.exists("download_history.json"):
        with open("download_history.json", "r") as file:
            history = json.load(file)
    else:
        history = []

    # Add the new video to the history
    history.append(filename)

    # Save the updated history to the JSON file
    with open("download_history.json", "w") as file:
        json.dump(history, file)

    # Update the history listbox
    history_listbox.delete(0, tk.END)
    for video in history:
        history_listbox.insert(tk.END, video)

def open_video(event):
    selected_video = history_listbox.get(history_listbox.curselection())
    if os.path.exists(selected_video):
        os.startfile(selected_video)
    else:
        history_listbox.itemconfig(history_listbox.curselection(), bg='red')

# Create the main window
window = tk.Tk()
window.title("YouTube Downloader")

# URL input field
url_label = ttk.Label(window, text="Video URL:")
url_label.pack()
url_entry = ttk.Entry(window, width=50)
url_entry.pack()

# Download button
download_button = ttk.Button(window, text="Download", command=download_video)
download_button.pack()

# Progress label
progress_label = ttk.Label(window, text="Download Progress: 0%")
progress_label.pack()
progress_label.pack_forget()  # Hide the label initially

# History label
history_label = ttk.Label(window, text="Download History:")
history_label.pack()

# History listbox
history_listbox = tk.Listbox(window, height=10)
history_listbox.pack(fill=tk.BOTH, expand=True)
history_listbox.bind('<Double-Button-1>', open_video)

# Load the download history from the JSON file
if os.path.exists("download_history.json"):
    with open("download_history.json", "r") as file:
        history = json.load(file)
        for video in history:
            history_listbox.insert(tk.END, video)

# Start the Tkinter event loop
window.mainloop()