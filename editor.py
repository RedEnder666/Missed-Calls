import json
from spritesheets import *

# Инициализируем Pygame
pygame.init()

# Определяем размер окна
WINDOW_SIZE = (1200, 750)

# Создаем окно
screen = pygame.display.set_mode(WINDOW_SIZE)

# Загружаем карту из файла JSON
with open('Hotline-Miami-clone/data/levels/test_1/main.dat', 'r') as file:
    map_data = file.read()
    map_data = eval(map_data)

# Загружаем тайлы
tiles = {}
for layer in map_data['layers']:
    for tile_data in layer:
        if tile_data[0] == 'Tile':
            tile_image = pygame.image.load(tile_data[3])
            tile_rect = pygame.Rect(tile_data[4])
            tiles[tuple(tile_data[1:3])] = (tile_image, tile_rect)

# Создаем сетку
grid_size = 16
grid_width = WINDOW_SIZE[0] // grid_size
grid_height = (WINDOW_SIZE[1] - 32) // grid_size
grid = [[(0, 0, 0) for y in range(grid_height)] for x in range(grid_width)]
SMODIFIER = 3
# Основной цикл игры
running = True
while running:
    # Обрабатываем события
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Если нажата левая кнопка мыши, добавляем тайл на карту
            if event.button == 1:
                x, y = event.pos
                x //= grid_size
                y = (y - 32) // grid_size
                # Сюда добавить код на установку тайлов

    # Рисуем карту
    for layer in map_data['layers']:
        for i, tile in enumerate(layer):
            if tile != 0:
                m = SMODIFIER
                tile_image = spritesheet(tile[3]).image_at(tile[4])
                tile_image = pygame.transform.scale(tile_image, list(map(lambda x: x*m, tile[4][2:4])))
                x,y = list(map(lambda x: x*m, tile[1:3]))
                screen.blit(tile_image, (x, y))

    # Рисуем UI
    #pygame.draw.rect(screen, (200, 200, 200), pygame.Rect(0, 0, WINDOW_SIZE[0], 32))
    pygame.display.flip()

# Сохраняем карту в файл
with open('Hotline-Miami-clone/map.json', 'w') as file:
    json.dump(map_data, file)
pygame.quit()
