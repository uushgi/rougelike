import curses
import random

class TileType():
    SPACE = 0
    FLOOR = 1
    CORRIDOR = 2
    WALL = 4


class Room:
    def __init__(self, x , y , w , h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.a = (x, y)
        self.b = (x+w, y)
        self.c = (x+w, y+h)
        self.d = (x, y+h)
        self.door_up = (x + (w//2), y)
        self.door_right = (x + w , y + (h//2))
        self.door_down = (x + (w//2), y + h)
        self.door_left = (x, y + (h//2))
    
    def intersects(self, other):
        if (self.a[0] <= other.c[0]) and (self.c[0] >= other.a[0]) and (self.a[1] <= other.c[1]) and (self.c[1] >= other.a[1]) :
            return True
        return False
    
    def too_close(self, other, min_distance=2):
   
        expanded = Room(
            self.x - min_distance,
            self.y - min_distance,
            self.w + 2 * min_distance,
            self.h + 2 * min_distance
        )
        return expanded.intersects(other)
    

class DungeonGenerator:
    def __init__(self, width, height, min_rooms = 6, max_rooms = 9, min_size_room = 10, max_size_room = 20):
        self.width = width
        self.height = height
        self.max_rooms = max_rooms
        self.min_rooms = min_rooms
        self.min_size_room = min_size_room
        self.max_size_room = max_size_room
        self.rooms = []
        

    def generator(self):
        while True:
            # Сбрасываем состояние при каждой новой попытке
            self.tiles = [[TileType.SPACE for _ in range(self.width)] for _ in range(self.height)]
            self.rooms = [Room(2, 2, 10, 6), Room(self.width - 16, self.height - 8, 10, 6)]  
            for room in self.rooms:
                self.create_room(room)

            attempts = 0
            self.count_rooms = random.randint(self.min_rooms, self.max_rooms)
            
            while len(self.rooms) < self.count_rooms:
                # Генерация параметров комнаты с проверкой на минимальный размер
                w = random.randint(self.min_size_room, self.max_size_room)
                h = random.randint(max(3, self.min_size_room - 6), self.max_size_room - 6)  # Не меньше 3
                
                x = random.randint(1, self.width - w - 1)
                y = random.randint(1, self.height - h - 1)

                new_room = Room(x, y, w, h)
                attempts += 1  # Увеличиваем счетчик при каждой попытке

                if any(new_room.intersects(other) for other in self.rooms) or any(new_room.too_close(other) for other in self.rooms):
                    if attempts >= 1000:
                        break  # Начинаем генерацию заново
                    continue

                self.rooms.append(new_room)
                self.create_room(new_room)
                attempts = 0  # Сбрасываем счетчик после успешного размещения

            if len(self.rooms) >= self.min_rooms:
                break 

    
    def create_room(self, room):
        # Заполняем всю комнату стенами
        for y in range(room.y, min(room.y + room.h, self.height)):
            for x in range(room.x, min(room.x + room.w, self.width)):
                self.tiles[y][x] = TileType.WALL
        
        # Заполняем внутреннюю часть комнаты полом (оставляя 1 клетку по краям для стен)
        for y in range(room.y + 1, min(room.y + room.h - 1, self.height - 1)):
            for x in range(room.x + 1, min(room.x + room.w - 1, self.width - 1)):
                self.tiles[y][x] = TileType.FLOOR


class Map():
    def __init__(self):
        self.screen = curses.initscr()
        curses.cbreak()
        curses.noecho()
        self.screen.keypad(True)
        curses.curs_set(0)

        self.height, self.width = self.screen.getmaxyx()
        # Смещение вниз и влево (настраиваемые значения)
        self.offset_x = 5  # Сдвиг вправо (чем больше, тем левее)
        self.offset_y = 3  # Сдвиг вниз
        # Уменьшаем размер поля с учетом смещения
        self.dungeon = DungeonGenerator(self.width - 2 - self.offset_x, 
                                      self.height - 2 - self.offset_y)
        self.dungeon.generator()

    def draw_map(self):
        self.screen.clear()
        for y in range(self.dungeon.height):
            for x in range(self.dungeon.width):
                try:
                    # Применяем смещение к координатам отрисовки
                    draw_y = y + self.offset_y
                    draw_x = x + self.offset_x
                    
                    if draw_y >= self.height or draw_x >= self.width:
                        continue  # Не выходим за границы экрана
                        
                    if self.dungeon.tiles[y][x] == TileType.SPACE:
                        self.screen.addch(draw_y, draw_x, '█')
                    elif self.dungeon.tiles[y][x] == TileType.FLOOR:
                        self.screen.addch(draw_y, draw_x, ' ')  
                    elif self.dungeon.tiles[y][x] == TileType.WALL:
                        self.screen.addch(draw_y, draw_x, ' ')  
                except curses.error:
                    pass
        self.screen.refresh()
    def run(self):
        self.draw_map()
        self.screen.getch()
        curses.endwin()

if __name__ == "__main__":
    game = Map()
    game.run()


