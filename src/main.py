import curses
import random

class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Character:
    def __init__(self, health, position):
        self.health = health
        self.max_health = health
        self.position = position        
        self.inventory = Inventory(5)

class Hero(Character):
    def __init__(self, health, position, symbol):
        super().__init__(health, position)
        self.symbol = symbol

class Enemy(Character):
    def __init__(self, health, damage, position, symbol):
        super().__init__(health, position)
        self.damage = damage
        self.symbol = symbol

class Item:
    def __init__(self, title, type):
        self.title = title
        self.type = type

class Sword(Item):
    def __init__(self, title, type, damage):
        super().__init__(title, type)
        self.damage = damage

class Inventory:
    def __init__(self, size, items=[]):
        self.items = items
        self.size = size
        self.active_slot = None
    
    def add_item(self, item):
        if len(self.items) < self.size:
            self.items.append(item)

    def equip_sword(self, item):
        if isinstance(item, Sword):
            self.active_slot = item
            print(f"Экипирован {item.title}")
        else:
            print(f"Не удалось экипировать предмет")

class Game:
    def __init__(self, hero, enemies):
        self.hero = hero
        self.enemies = enemies
        self.actions = Actions()
        self.turns = Turns(hero, enemies)
        self.state = State()
    
    def game_loop(self):
        while True:
            current = self.turns.current_turn()
            
            if current == self.hero:
                self.hero_turn_manager()
            else:
                for enemy in self.enemies:
                    if enemy.health > 0:
                        self.enemy_turn_manager(enemy)

            self.turns.next_turn()

            if self.state.is_hero_dead(self.hero):
                print(f"смэрть")
                break

            if self.state.all_enemies_are_dead(self.enemies):
                print(f"победа")
                break
    
    def hero_turn_manager(self):
        print(f"\n[Ход игрока {self.hero.symbol}]")
        print(f"Здоровье: {self.hero.health}/{self.hero.max_health}")
        for enemy in self.enemies:
            if enemy.health > 0:
             self.actions.attack_character(self.hero, enemy)
             break

    def enemy_turn_manager(self, enemy):
        print(f"\n[Ход врага {enemy.symbol}]")
        print(f"Здоровье врага: {enemy.health}")
        self.actions.attack_character(enemy, self.hero)

class Turns:
    def __init__(self, hero, enemies):
        self.hero = hero
        self.enemies = enemies
        self.is_hero_turn = True

    def next_turn(self):
        self.is_hero_turn = not self.is_hero_turn

    def current_turn(self):
        if self.is_hero_turn:
            return self.hero
        return self.enemies
    
class Actions:
    def movement(self, character, direction):
        print(f"{character} двигается на {direction}")  # заглушка. игрок/моб двигается на север/юг/запад/восток

    def attack_character(self, attacker, target):
        damage = self.total_damage(attacker)
        target.health -= damage
        print(f"{attacker} нанес {target} {damage} урона")

    def total_damage(self, character):
        if isinstance(character, Hero):
            if character.inventory.active_slot:
                return character.inventory.active_slot.damage
            return 2 # стандартный урон игрового персонажа, условно кулаки
        return character.damage # урон врагов
    
class State:
    def is_hero_dead(self, hero):
        return hero.health <= 0
    
    def all_enemies_are_dead(self, enemies):
        return all(enemy.health <= 0 for enemy in enemies)
    

#test
#hero = Hero(50, (0,0), '@')
#enemies = [
#    Enemy(200, 10, (1,1), 'Y'),
#    Enemy(300, 5, (2,2), 'T')]
#
#game = Game(hero, enemies)
#game.game_loop()

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
    def __init__(self, width, height, min_rooms = 6, max_rooms = 9, min_size_room = 7, max_size_room = 12):
        self.width = width
        self.height = height
        self.max_rooms = max_rooms
        self.min_rooms = min_rooms
        self.min_size_room = min_size_room
        self.max_size_room = max_size_room
        self.tiles = [[TileType.SPACE for _ in range(width)] for _ in range(height)]
        self.rooms = []
        
        self.start_room = Room(2, 2, 10, 6)
        self.create_room(self.start_room)

        self.finish_room = Room(width - 16 , height - 8, 10, 6)
        self.create_room(self.finish_room)

        self.rooms = [self.start_room, self.finish_room]


    def generator(self):
        self.count_rooms = random.randint(self.min_rooms,self.max_rooms)

        while len(self.rooms) < self.count_rooms:
            w = random.randint(self.min_size_room,self.max_size_room)
            h = random.randint(self.min_size_room - 4,self.max_size_room - 4)
            x = random.randint(1, self.width - w - 1)
            y = random.randint(1, self.height - h  - 1)

            new_room  = Room(x,y,w,h)

            if any((new_room.intersects(other_rooms) for other_rooms in self.rooms)) or any((new_room.too_close(other_rooms) for other_rooms in self.rooms)):
                continue

            self.rooms.append(new_room)
            self.create_room(new_room)

    
    def create_room(self, room):
        for y in range(room.y, min(room.y + room.h, self.height)):
            for x in range(room.x, min(room.x + room.w, self.width)):
                self.tiles[y][x] = TileType.FLOOR


class Map():
    def __init__(self):
        self.screen = curses.initscr()
        curses.cbreak()
        curses.noecho()
        self.screen.keypad(True)
        curses.curs_set(0)

        self.height, self.width = self.screen.getmaxyx()
        self.dungeon = DungeonGenerator(self.width - 2, self.height - 2)
        self.dungeon.generator()

    def draw_map(self):
        self.screen.clear()
        for y in range(self.dungeon.height):
            for x in range(self.dungeon.width):
                try:
                    if self.dungeon.tiles[y][x] == TileType.SPACE:
                        self.screen.addch(y, x, ' ')
                    else:
                        self.screen.addstr(y, x, '+') 
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