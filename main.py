from PyQt6.QtWidgets import QApplication
from ui import WholesomeMP3
import sys
import pygame

if __name__ == "__main__":
    pygame.init()
    app = QApplication(sys.argv)
    window = WholesomeMP3()
    window.show()
    sys.exit(app.exec())