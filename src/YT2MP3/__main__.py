from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QLabel,
    QPushButton, QFileDialog, QTextEdit, QHBoxLayout
)
from PySide6.QtCore import Qt
from yt_dlp import YoutubeDL
import os
import socket
import sys


class DownloaderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube to MP3 Downloader")
        self.setMinimumSize(500, 400)

        self.layout = QVBoxLayout()

        self.url_label = QLabel("YouTube URL:")
        self.url_input = QLineEdit()

        self.folder_button = QPushButton("Select Download Folder")
        self.folder_button.clicked.connect(self.select_folder)
        self.download_folder = os.path.join(os.getcwd(), "downloads")
        self.folder_label = QLabel(self.download_folder)

        self.download_button = QPushButton("⬇ Download MP3")
        self.download_button.clicked.connect(self.download_mp3)

        self.status_box = QTextEdit()
        self.status_box.setReadOnly(True)

        self.layout.addWidget(self.url_label)
        self.layout.addWidget(self.url_input)

        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.folder_button)
        folder_layout.addWidget(self.folder_label)
        self.layout.addLayout(folder_layout)

        self.layout.addWidget(self.download_button)
        self.layout.addWidget(QLabel("Status:"))
        self.layout.addWidget(self.status_box)

        self.setLayout(self.layout)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.download_folder = folder
            self.folder_label.setText(folder)

    def has_internet(self):
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False

    def ffmpeg_installed(self):
        return os.system("which ffmpeg > /dev/null 2>&1") == 0

    def log(self, message):
        self.status_box.append(message)

    def download_mp3(self):
        url = self.url_input.text().strip()
        self.status_box.clear()
        self.log("⬇ Preparing to download...")

        if not url.startswith("http"):
            self.log("❌ Invalid URL")
            return

        if not os.path.isdir(self.download_folder):
            self.log("❌ Invalid download folder.")
            return

        if not self.has_internet():
            self.log("❌ No internet connection")
            return

        if not self.ffmpeg_installed():
            self.log("❌ FFmpeg is not installed or not in PATH.")
            return

        os.makedirs(self.download_folder, exist_ok=True)

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{self.download_folder}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': False,
            'no_warnings': True,
            'progress_hooks': [self.progress_hook]
        }

        try:
            self.log("⬇ Downloading...")
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.log("✅ Done! MP3 saved.")
        except Exception as e:
            if "HTTP Error 403" in str(e):
                self.log("❌ Download blocked — video may be age-restricted or region-locked.")
            else:
                self.log(f"❌ Error: {e}")

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            self.log("...downloading audio...")
        elif d['status'] == 'finished':
            self.log("🔁 Converting to MP3...")


def main():
    app = QApplication(sys.argv)
    window = DownloaderApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
