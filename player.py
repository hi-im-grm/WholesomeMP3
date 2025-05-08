import pygame

class MP3Player:
    def __init__(self):
        pygame.mixer.init()

    def load_song(self, song_path):
        pygame.mixer.music.load(song_path)

    def play(self):
        pygame.mixer.music.play()

    def pause(self):
        pygame.mixer.music.pause()

    def stop(self):
        pygame.mixer.music.stop()

    def set_volume(self, volume):
        pygame.mixer.music.set_volume(volume)

    def get_length(self, song_path):
        return pygame.mixer.Sound(song_path).get_length()

    def get_position(self):
        return pygame.mixer.music.get_pos() / 1000  # Convert milliseconds to seconds

    def set_position(self, position):
        pygame.mixer.music.set_pos(position)