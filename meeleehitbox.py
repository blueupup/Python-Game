import pygame

class MeleeHitbox(pygame.sprite.Sprite):
    def __init__(self, player, weapon, enemy_group, particle_manager):
        super().__init__()
        
        self.player = player
        self.weapon = weapon
        self.enemy_group = enemy_group
        self.particle_manager = particle_manager
        
        self.hit_enemies = set() # Enemies we've already hit
        self.life_timer = 0.15   # How long the hitbox lasts (in seconds)
        
        # --- Create the hitbox rect ---
        width = int(self.weapon.attack_range * 0.75)
        height = int(self.weapon.attack_range * 1.5)
        
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        
        self.rect = self.image.get_rect()
        
        # --- Position the hitbox in front of the player ---
        if self.player.facing_right:
            self.rect.midleft = self.player.rect.midright
        else:
            self.rect.midright = self.player.rect.midleft
            
        print(f"[ATTACK] Melee hitbox created for {self.weapon.name}")

    def update(self, dt):
        # 1. Tick down lifetime
        self.life_timer -= dt
        if self.life_timer <= 0:
            self.kill() # Destroy self
            return
            
        # 2. Check for collisions
        self.check_collisions()
        
    def check_collisions(self):
        # Find all enemies that are touching this hitbox
        collided_list = pygame.sprite.spritecollide(self, self.enemy_group, False)
        
        for enemy in collided_list:
            # Check if we've already hit this enemy
            if enemy not in self.hit_enemies:
                
                # 1. Add to "hit list" to prevent double-hits
                self.hit_enemies.add(enemy)
                
                # 2. Calculate damage
                damage = self.player.stats.attack_power + self.weapon.weapon_damage
                print(f"[COMBAT] {self.weapon.name} hit {enemy.stats.name} for {damage} damage!")
                
                # 3. Deal damage
                enemy.take_damage(damage)
                
                # 4. Create particle effect
                if self.particle_manager:
                    self.particle_manager.create_hit_effect(enemy.pos.x, enemy.pos.y)
