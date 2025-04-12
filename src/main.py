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

class Logic:
    def __init__(self, player, enemies):
        self.player = player
        self.enemies = enemies
        self.actions = Actions()
        self.turns = Turns(player, enemies)
        self.state = State()
    
    def game_loop(self):
        while True:
            current = self.turns.current_turn()
            
            if current == self.player:
                self.player_turn_manager()
            else:
                for enemy in self.enemies:
                    if enemy.health > 0:
                        self.enemy_turn_manager(enemy)

            self.turns.next_turn()

            if self.state.is_player_dead(self.player):
                print(f"смэрть")
                break

            if self.state.all_enemies_are_dead(self.enemies):
                print(f"победа")
                break
    
    def player_turn_manager(self):
        print(f"\n[Ход игрока {self.player.symbol}]")
        print(f"Здоровье: {self.player.health}/{self.player.max_health}")
        for enemy in self.enemies:
            if enemy.health > 0:
             self.actions.attack_character(self.player, enemy)
             break

    def enemy_turn_manager(self, enemy):
        print(f"\n[Ход врага {enemy.symbol}]")
        print(f"Здоровье врага: {enemy.health}")
        self.actions.attack_character(enemy, self.player)

class Turns:
    def __init__(self, player, enemies):
        self.player = player
        self.enemies = enemies
        self.is_player_turn = True

    def next_turn(self):
        self.is_player_turn = not self.is_player_turn

    def current_turn(self):
        if self.is_player_turn:
            return self.player
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
    def is_player_dead(self, hero):
        return hero.health <= 0
    
    def all_enemies_are_dead(self, enemies):
        return all(enemy.health <= 0 for enemy in enemies)