import os
import sys
import pygame
import requests


COORDS = [133.795393, -25.6947768]
SPN = [1, 1]
map_api_server = "http://static-maps.yandex.ru/1.x/"
map_file = "map.png"
map_types = ['map', 'sat', 'sat,skl']
type_ind = 0


def load_file(COORDS, SPN):
    map_params = {
        "ll": ','.join(list(map(str, COORDS))),
        "spn": ','.join(list(map(str, SPN))),
        "l": map_types[type_ind]
    }
    response = requests.get(map_api_server, params=map_params)
    with open(map_file, "wb") as file:
        file.write(response.content)


load_file(COORDS, SPN)

pygame.init()
screen = pygame.display.set_mode((600, 450))
screen.blit(pygame.image.load(map_file), (0, 0))
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_PAGEUP:
                SPN = list(map(lambda x: str(float(x) + 0.5), SPN))
            elif event.key == pygame.K_PAGEDOWN:
                SPN = list(map(lambda x: str(float(x) - 0.5), SPN))
            elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                type_ind = [pygame.K_1, pygame.K_2, pygame.K_3].index(event.key)
            load_file(COORDS, SPN)
    screen.blit(pygame.image.load(map_file), (0, 0))
    pygame.display.flip()

pygame.quit()
