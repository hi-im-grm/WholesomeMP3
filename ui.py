import os
import pygame
import sys
import shutil
from PyQt6.QtWidgets import QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QSlider, QMenuBar, QFileDialog
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPixmap, QIcon
from player import MP3Player


class WholesomeMP3(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WholesomeMP3")
        self.setFixedSize(400, 600)
        self.setWindowIcon(QIcon(self.resource_path("assets/icons/sound-mixer.ico")))

        # Initialize MP3 player
        self.player = MP3Player()

        # Initialize attributes
        self.songs = []
        self.current_song_index = 0
        self.song_length = 0
        self.is_paused = True

        # Timer for updating progress
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)

        # Timer for checking song end
        self.song_end_timer = QTimer(self)
        self.song_end_timer.timeout.connect(self.check_song_end)
        self.song_end_timer.start(500)  # Check every 500ms

        # Set up pygame end-of-song event
        self.SONG_END_EVENT = pygame.USEREVENT + 1
        pygame.mixer.music.set_endevent(self.SONG_END_EVENT)

        # Apply light theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffebd2;
            }
            QLabel {
                color: #333333;
                font-size: 16px;
                font-family: Arial, sans-serif;
            }
            QLabel#songLabel {
                background-color: #c79a83;
                border-radius: 5px;
                padding: 5px;
                color: #333333;
                font-size: 18px;
                font-weight: bold;
                text-align: center;
            }
            QSlider::groove:horizontal {
                background: #e0e0e0;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #c79a83;
                width: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
            QPushButton {
                background-color: #c79a83;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
            QMenuBar {
                background-color: #ffebd2;
                color: #ffffff;
            }
            QMenuBar::item {
                background-color: #ffebd2;
                color: #ffffff;
            }
            QMenuBar::item:selected {
                background-color: #e0e0e0;
            }
        """)

        # Create menu
        self.create_menu()

        # Main widget and layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)

        # Song label
        self.song_label = QLabel("No songs available", self)
        self.song_label.setObjectName("songLabel")  # Assign a unique object name
        self.song_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.song_label)

        # Album image
        self.image_label = QLabel(self)
        self.image_label.setPixmap(QPixmap(self.resource_path("assets/images/default.jpg")).scaled(350, 350, Qt.AspectRatioMode.KeepAspectRatio))
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image_label)

        # Progress slider
        self.progress_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.progress_slider.setRange(0, 100)
        self.progress_slider.setEnabled(False)  # Make the slider read-only
        layout.addWidget(self.progress_slider)

        # Control buttons
        controls_layout = QHBoxLayout()
        self.add_control_button(controls_layout, "previous.png", self.previous_song)
        self.start_stop_button = self.add_control_button(controls_layout, "play.png", self.toggle_playback)
        self.add_control_button(controls_layout, "next.png", self.next_song)
        layout.addLayout(controls_layout)

        # Volume slider
        volume_layout = QHBoxLayout()
        self.volume_icon = QLabel(self)
        self.volume_icon.setPixmap(QPixmap(self.resource_path("assets/icons/volume-up.png")).scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio))
        volume_layout.addWidget(self.volume_icon)
        self.volume_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.set_volume)
        volume_layout.addWidget(self.volume_slider)
        layout.addLayout(volume_layout)

        # Load songs from assets/music
        self.songs = self.load_songs("assets/music")
        if not self.songs:
            self.song_label.setText("No songs available")
        else:
            self.current_song_index = 0
            self.load_and_prepare_song(self.songs[self.current_song_index])

    def create_menu(self):
        """Create the menu bar."""
        menu_bar = QMenuBar(self)

        # File menu
        file_menu = menu_bar.addMenu("File")

        # Add MP3 action
        add_mp3_action = file_menu.addAction("Add MP3")
        add_mp3_action.triggered.connect(self.add_mp3)

        # Exit action
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)

        self.setMenuBar(menu_bar)

    def add_mp3(self):
        """Add an MP3 file to the playlist and save it to the assets/music folder."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select MP3 File", "", "Audio Files (*.mp3)")
        if file_path:
            # Get the file name and destination path
            file_name = os.path.basename(file_path)
            destination_path = self.resource_path(os.path.join("assets/music", file_name))

            # Check if the file already exists in the destination folder
            if not os.path.exists(destination_path):
                try:
                    shutil.copy(file_path, destination_path)  # Copy the file to assets/music
                    print(f"Copied {file_name} to {destination_path}")
                except Exception as e:
                    print(f"Error copying file: {e}")
                    return

            # Add the song to the playlist
            self.songs.append(destination_path)
            if len(self.songs) == 1:  # If it's the first song, load it
                self.current_song_index = 0
                self.load_and_prepare_song(self.songs[self.current_song_index])

    def add_control_button(self, layout, icon_name, callback):
        button = QPushButton(self)
        button.setIcon(QIcon(self.resource_path(f"assets/icons/{icon_name}")))
        button.setIconSize(QSize(32, 32))
        button.clicked.connect(callback)
        layout.addWidget(button)
        return button

    def load_and_prepare_song(self, song_path):
        """Load and prepare the selected song."""
        song_name = os.path.splitext(os.path.basename(song_path))[0]
        self.song_label.setText(song_name)

        # Load the song
        self.player.load_song(song_path)
        self.song_length = self.player.get_length(song_path)
        self.progress_slider.setValue(0)

    def toggle_playback(self):
        """Play or pause the current song."""
        print(f"Playback position: {pygame.mixer.music.get_pos()} ms")
        print(f"Is paused: {self.is_paused}")
        if self.is_paused:
            if pygame.mixer.music.get_pos() > 0:  # If the song is paused, resume it
                print("Resuming playback...")
                pygame.mixer.music.unpause()
            else:  # If the song is not playing, start it
                print("Starting playback...")
                self.player.play()
            self.is_paused = False
            self.timer.start(1000)  # Start the timer to update the progress slider
            self.start_stop_button.setIcon(QIcon(self.resource_path("assets/icons/pause.png")))
        else:
            print("Pausing playback...")
            pygame.mixer.music.pause()  # Pause the song
            self.is_paused = True
            self.timer.stop()  # Stop the timer to pause progress updates
            self.start_stop_button.setIcon(QIcon(self.resource_path("assets/icons/play.png")))

    def previous_song(self):
        """Play the previous song."""
        if self.songs:
            self.current_song_index = (self.current_song_index - 1) % len(self.songs)
            self.load_and_prepare_song(self.songs[self.current_song_index])

            # Automatically start playback
            self.player.play()
            self.is_paused = False
            self.timer.start(1000)
            self.start_stop_button.setIcon(QIcon(self.resource_path("assets/icons/pause.png")))  # Use resource_path

    def next_song(self):
        """Play the next song."""
        if self.songs:
            self.current_song_index = (self.current_song_index + 1) % len(self.songs)
            self.load_and_prepare_song(self.songs[self.current_song_index])

            # Automatically start playback
            self.player.play()
            self.is_paused = False
            self.timer.start(1000)
            self.start_stop_button.setIcon(QIcon(self.resource_path("assets/icons/pause.png")))  # Use resource_path

    def set_volume(self):
        """Set the volume and update the volume icon."""
        volume = self.volume_slider.value() / 100
        self.player.set_volume(volume)

        # Update the volume icon based on the volume level
        if volume == 0:
            self.volume_icon.setPixmap(QPixmap(self.resource_path("assets/icons/no-sound.png")).scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio))
        else:
            self.volume_icon.setPixmap(QPixmap(self.resource_path("assets/icons/volume-up.png")).scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio))

    def update_progress(self):
        """Update the progress slider."""
        if self.song_length > 0:
            current_position = self.player.get_position()
            progress = int((current_position / self.song_length) * 100)
            self.progress_slider.setValue(progress)

    def load_songs(self, folder):
        """Load all MP3 files from the specified folder."""
        folder = self.resource_path(folder)
        if os.path.exists(folder) and os.path.isdir(folder):
            return [os.path.join(folder, file) for file in os.listdir(folder) if file.lower().endswith(".mp3")]
        return []

    def check_song_end(self):
        """Check if the current song has ended and play the next song."""
        for event in pygame.event.get():
            if (event.type == self.SONG_END_EVENT):
                self.next_song()

    def resource_path(self, relative_path):
        """Get the absolute path to a resource, works for dev and for PyInstaller."""
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        return os.path.join(base_path, relative_path)