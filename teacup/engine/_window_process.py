import pygame
import warnings
import sys
from .window import get_default_window_data, _translate_window_data

pygame.init()

window_data = {}

if len(sys.argv) >= 2:
    binary_data = sys.argv[1]
    window_data = _translate_window_data(binary_data)
else:
    warnings.warn("No window_data passed, resorting to default")
    window_data = get_default_window_data()


screen = pygame.display.set_mode(window_data["size"])
pygame.display.set_caption(window_data["title"])

icon = pygame.image.load(window_data["icon"])
pygame.display.set_icon(icon)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((30, 30, 30))
    pygame.display.flip()

pygame.quit()
