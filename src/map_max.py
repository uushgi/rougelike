import curses
import random
from enum import Enum, auto

class TileType():
    WALL = 1
    FLOOR = 2
    CORRIDOR = 3

class Room:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h
        self.center = (x + w // 2, y + h // 2)

    def intersects(self, other):
        return (self.x1  <= other.x2  and self.x2  >= other.x1    and
                self.y1  <= other.y2  and self.y2  >= other.y1  )
    def is_too_close(self, other, min_distance = 5):
        return (self.x1 - other.x2 < min_distance and  
            other.x1 - self.x2 < min_distance and  
            self.y1 - other.y2 < min_distance and 
            other.y1 - self.y2 < min_distance)     

class DungeonGenerator:
    def __init__(self, width, height, max_rooms=7, room_min_size=7, room_max_size=15):
        self.width = width
        self.height = height
        self.max_rooms = max_rooms
        self.room_min_size = room_min_size
        self.room_max_size = room_max_size
        self.tiles = [[TileType.WALL for _ in range(height)] for _ in range(width)]
        self.rooms = []
        self.connected_centers = []

    def generate(self):
        for _ in range(self.max_rooms):
            w = random.randint(self.room_min_size, self.room_max_size)
            h = random.randint(self.room_min_size, self.room_max_size)
            x = random.randint(1, self.width - w - 1)
            y = random.randint(1, self.height - h - 1)

            new_room = Room(x, y, w, h)
            if any(new_room.intersects(other) for other in self.rooms)  :
                continue

            self.create_room(new_room)
            self.rooms.append(new_room)

            if len(self.rooms) > 1:
                self.connect_rooms(new_room, self.rooms[-2])

    def create_room(self, room):
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.tiles[x][y] = TileType.FLOOR

    def connect_rooms(self, room1, room2):
        x1, y1 = room1.center
        x2, y2 = room2.center

        if random.random() < 0.5:
            self.create_h_tunnel(x1, x2, y1)
            self.create_v_tunnel(y1, y2, x2)
        else:
            self.create_v_tunnel(y1, y2, x1)
            self.create_h_tunnel(x1, x2, y2)

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y] = TileType.CORRIDOR

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y] = TileType.CORRIDOR
            

class DungeonGame:
    def __init__(self):
        self.screen = curses.initscr()
        curses.cbreak()
        curses.noecho()
        self.screen.keypad(True)
        curses.curs_set(0)
        
        self.height, self.width = self.screen.getmaxyx()
        self.dungeon = DungeonGenerator(self.width - 2, self.height - 2)
        self.dungeon.generate()
        
    def draw_map(self):
        for x in range(self.dungeon.width):
            for y in range(self.dungeon.height):
                try:
                    if self.dungeon.tiles[x][y] == TileType.WALL:
                        self.screen.addch(y, x, ' ')
                    elif self.dungeon.tiles[x][y] == TileType.FLOOR:
                        self.screen.addch(y, x, '*')
                    elif self.dungeon.tiles[x][y] == TileType.CORRIDOR:
                        self.screen.addch(y, x, '+')
                except curses.error:
                    pass
        self.screen.refresh()

    def run(self):
        self.draw_map()
        self.screen.getch()
        curses.endwin()

if __name__ == "__main__":
    game = DungeonGame()
    game.run()