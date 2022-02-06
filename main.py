import os
import sys

import pygame
import requests


ll = input("Введите координаты:").split()
spn = input("Введите масштаб карты:").split()
map_api_server = "http://static-maps.yandex.ru/1.x/"
map_params = {
    "ll": ",".join(ll),
    "spn": ",".join(spn),
    "l": "map"
}
response = requests.get(map_api_server, params=map_params)

if not response:
    print("Ошибка выполнения запроса")
    sys.exit(1)

map_file = "map.png"
with open(map_file, "wb") as file:
    file.write(response.content)

pygame.init()
screen = pygame.display.set_mode((600, 450))
screen.blit(pygame.image.load(map_file), (0, 0))
pygame.display.flip()
while pygame.event.wait().type != pygame.QUIT:
    pass
pygame.quit()

os.remove(map_file)