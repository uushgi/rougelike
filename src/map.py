import curses
import random

class TileType(): #типы полей
    SPACE = 0
    FLOOR = 1

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
    
    def intersects(self, other): #проверка на 
        if (self.a[0] <= other.c[0]) and (self.c[0] >= other.a[0]) and (self.a[1] <= other.c[1]) and (self.c[1] >= other.a[1]) :
            return True
        return False
    
    def too_close(self, other, min_distance=3):
   
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
                self.connect_rooms()
                break 

    
    def create_room(self, room):
        for y in range(room.y, min(room.y + room.h, self.height)):
            for x in range(room.x, min(room.x + room.w, self.width)):
                self.tiles[y][x] = TileType.FLOOR
    
    def connect_rooms(self):
        for i in range(len(self.rooms) - 1):
            room1 = self.rooms[i]
            room2 = self.rooms[i + 1]
            
            # Выбираем случайные точки в каждой комнате
            x1 = random.randint(room1.x + 1, room1.x + room1.w - 2)
            y1 = random.randint(room1.y + 1, room1.y + room1.h - 2)
            x2 = random.randint(room2.x + 1, room2.x + room2.w - 2)
            y2 = random.randint(room2.y + 1, room2.y + room2.h - 2)
            
            # Соединяем коридором (50% вероятность сначала по горизонтали)
            if random.random() < 0.5:
                self.create_h_tunnel(x1, x2, y1)
                self.create_v_tunnel(y1, y2, x2)
            else:
                self.create_v_tunnel(y1, y2, x1)
                self.create_h_tunnel(x1, x2, y2)
    
    def create_h_tunnel(self, x1: int, x2: int, y: int):
        """Горизонтальный коридор"""
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if self.tiles[y][x] == TileType.SPACE:
                self.tiles[y][x] = TileType.FLOOR

    
    def create_v_tunnel(self, y1: int, y2: int, x: int):
        """Вертикальный коридор"""
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if self.tiles[y][x] == TileType.SPACE:
                self.tiles[y][x] = TileType.FLOOR


class Map():
    def __init__(self):
        self.screen = curses.initscr()
        curses.cbreak()
        curses.noecho()
        self.screen.keypad(True)
        curses.curs_set(0)

        curses.start_color()  # Включаем цветной режим
        curses.use_default_colors()  # Используем цвета терминала
        

        curses.init_pair(1,0, 0)    # SPACE
        curses.init_pair(2, 8, 0)  # FLOOR

 
        self.offset_y = 3
        self.offset_x = 5
        self.height, self.width = 30,100
        self.dungeon = DungeonGenerator(self.width - 3 - self.offset_x , self.height - 3 - self.offset_y  )
        self.dungeon.generator()

    def draw_map(self):
        self.screen.clear()
        for y in range(self.dungeon.height):
            for x in range(self.dungeon.width):
                try:

                    if self.dungeon.tiles[y][x] == TileType.SPACE:
                        self.screen.addch(y + self.offset_y, x + self.offset_x, '█', curses.color_pair(1))
                    else:
                        self.screen.addch(y + self.offset_y, x + self.offset_x, '█', curses.color_pair(2))  
                except curses.error:
                    pass

    def run(self):
        self.draw_map()
        self.screen.getch()
        curses.endwin()


game = Map()
game.run()


