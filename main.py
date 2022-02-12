import os
import sys
import pprint
import pygame
import requests
import math

COORDS = [49.106414, 55.796127]
SPN = [0.01, 0.01]
map_api_server = "http://static-maps.yandex.ru/1.x/"
map_file = "map.png"
map_types = ['map', 'sat', 'sat,skl']
type_ind = 0


def change_ll(ind):
    if ind == 0:
        COORDS[0] -= 0.1
    elif ind == 1:
        COORDS[0] += 0.1
    elif ind == 2:
        COORDS[1] += 0.1
    else:
        COORDS[1] -= 0.1


POINTS = []


def load_file(COORDS, SPN):
    map_params = {
        "ll": ','.join(list(map(str, COORDS))),
        "spn": ','.join(list(map(str, SPN))),
        "l": map_types[type_ind],
        "pt": '~'.join(POINTS)

    }
    response = requests.get(map_api_server, params=map_params)
    with open(map_file, "wb") as file:
        file.write(response.content)


load_file(COORDS, SPN)

pygame.init()
screen = pygame.display.set_mode((600, 450))
screen.blit(pygame.image.load(map_file), (0, 0))
running = True
search_text = ''
API_KEY = '40d1649f-0493-4b70-98ba-98533de7710b'


def geocode(address):
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {
        "apikey": API_KEY,
        "geocode": address,
        "format": "json"}

    response = requests.get(geocoder_request, params=geocoder_params)

    if response:

        json_response = response.json()
    else:
        raise RuntimeError(
            f"""Ошибка выполнения запроса:
            {geocoder_request}
            Http статус: {response.status_code} ({response.reason})""")

    features = json_response["response"]["GeoObjectCollection"]["featureMember"]
    return features[0]["GeoObject"] if features else None


def get_coordinates(address):
    toponym = geocode(address)
    if not toponym:
        return None, None

    toponym_coodrinates = toponym["Point"]["pos"]

    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
    return toponym_longitude, toponym_lattitude


def screen_to_geo(pos):
    dy = 225 - pos[1]
    dx = pos[0] - 300
    lx = lon + dx * coord_to_geo_x * math.pow(2, 15 - zoom)
    ly = lat + dy * coord_to_geo_y * math.cos(math.radians(lat)) * math.pow(2, 15 - zoom)
    return lx, ly


def get_pos_name(geocoder_request):
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode=" \
                       f"{geocoder_request}&format=json"
    response = requests.get(geocoder_request)
    if response:
        json_response = response.json()

        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]

        toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]

        toponym_coodrinates = toponym["Point"]["pos"].split()[::-1]
        return toponym_address


def get_postal_code(geocoder_request):
    try:
        geocoder_request = get_pos_name(geocoder_request)
        geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey=40d1649f-0493-4b70-98ba-98533de7710b&geocode=" \
                           f"{geocoder_request}&format=json"
        response = requests.get(geocoder_request)
        res_dict = response.json()
        info = res_dict["response"]["GeoObjectCollection"]['featureMember'][0]['GeoObject']
        postal_code = info['metaDataProperty']['GeocoderMetaData']['Address']['postal_code']
        return postal_code
    except KeyError:
        pass


coord_to_geo_x = 0.0000428
coord_to_geo_y = 0.0000428
lat = 55.796127
lon = 49.106414
zoom = 15

add_postal_code = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            # починить появление -- already fixed
            POINTS.append(','.join(list(map(str, screen_to_geo(pos)))) + ',pm2ywl')
            load_file(COORDS, SPN)
            if add_postal_code:
                pygame.display.set_caption(
                    f"{get_pos_name(screen_to_geo(pos))} почтовый индекс: "
                    f"{get_postal_code(screen_to_geo(pos))}")
            else:
                pygame.display.set_caption(get_pos_name(screen_to_geo(pos)))

        if event.type == pygame.KEYDOWN:
            char = event.unicode
            if event.key == pygame.K_DELETE:
                search_text = ''
                POINTS = []
            if event.key == pygame.K_BACKSPACE:
                search_text = search_text[:-1]
            if char.isalpha() or char.isnumeric() or char == ' ':
                search_text += char
            if event.key == pygame.K_RETURN:
                COORDS = list(map(float, get_coordinates(search_text)))
            if event.key == pygame.K_SPACE:
                add_postal_code = not add_postal_code

            pygame.display.set_caption(search_text)
            try:
                if event.key == pygame.K_PAGEUP:
                    print(True)
                    SPN[0] = round(SPN[0] + 0.02, 3)
                    SPN[1] = round(SPN[1] + 0.02, 3)
                    print(SPN)
                elif event.key == pygame.K_PAGEDOWN:

                    SPN[0] = round(SPN[0] - 0.02, 3)
                    SPN[1] = round(SPN[1] - 0.02, 3)
                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    type_ind = [pygame.K_1, pygame.K_2, pygame.K_3].index(event.key)
                elif event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                    change_ll([pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN].index(event.key))
                load_file(COORDS, SPN)
                # screen.blit(pygame.image.load(map_file), (0, 0))
            except Exception as e:
                if event.key == pygame.K_PAGEDOWN:
                    print(True)
                    SPN[0] = round(SPN[0] + 0.02, 3)
                    SPN[1] = round(SPN[1] + 0.02, 3)
                    print(SPN)
                elif event.key == pygame.K_PAGEUP:

                    SPN[0] = round(SPN[0] - 0.02, 3)
                    SPN[1] = round(SPN[1] - 0.02, 3)

    screen.blit(pygame.image.load(map_file), (0, 0))
    pygame.display.flip()

pygame.quit()
