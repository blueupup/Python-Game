class CharacterStats:
    def __init__(self, level, base_health, base_attack):
        self.level = level
        self.base_health = base_health
        self.base_attack = base_attack
        
        self.xp = 0
        self.xp_to_next_level = 100 * level
        
        self.current_health = self.max_health

    @property
    def max_health(self):
        return self.base_health + (self.level * 20)

    @property
    def attack_power(self):
        return self.base_attack + (self.level * 5)

    def take_damage(self, amount):
        self.current_health -= amount
        if self.current_health <= 0:
            self.current_health = 0
            return True
        return False
    
    def heal(self, amount):
        self.current_health += amount
        if self.current_health > self.max_health:
            self.current_health = self.max_health

    def add_xp(self, amount):
        self.xp += amount
        while self.xp >= self.xp_to_next_level:
            # Leveled up!
            self.xp -= self.xp_to_next_level
            self.level_up()

    def character_points(self):
        pass

    def level_up(self):
        self.level += 1
        print(f"Ding! Reached Level {self.level}")
        
        self.xp_to_next_level = 100 * self.level
        
        self.current_health = self.max_health