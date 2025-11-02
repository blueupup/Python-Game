import pygame
import math

class OrbitalNode(pygame.sprite.Sprite):
    def __init__(self, player, radius, rotation_speed, weapon_damage, hit_cooldown, image, start_angle,particle_manager, enemy_group):
        super().__init__()
        
        # --- Core Properties ---
        self.player = player
        self.radius = radius
        self.rotation_speed = rotation_speed
        self.angle = start_angle  # Its starting position on the circle (in radians)

        self.enemy_group = enemy_group
        self.particle_manager = particle_manager
        
        # --- Image / Rect ---
        self.base_image = image  # The "clean" loaded image
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect()
        
        # --- Combat ---
        self.weapon_damage = weapon_damage
        self.hit_cooldown = hit_cooldown
        self.hit_timer = 0.0 # Starts ready to hit
        
        # --- Hit Flash Effect (stolen from your Enemy) ---
        self.is_flashing = False
        self.flash_duration = 0.1
        self.flash_timer = 0.0

    def can_attack(self):
        return self.hit_timer <= 0

    def deal_damage(self, enemy_target):
        if not self.can_attack():
            return
            
        # 1. Reset timer
        self.hit_timer = self.hit_cooldown
        
        # 2. Trigger flash
        self.is_flashing = True
        self.flash_timer = 0.0
    
        if self.particle_manager:
                    self.particle_manager.create_hit_effect(self.rect.centerx, self.rect.centery)

        total_damage = self.player.stats.attack_power + self.weapon_damage

        print(f"[COMBAT] OrbitalNode hit {enemy_target.stats.name} for {total_damage} damage!")
        enemy_target.take_damage(total_damage)

    def update(self, dt):
        if self.hit_timer > 0:
            self.hit_timer -= dt
            
        self.angle += self.rotation_speed * dt
        
        # Keep angle from getting huge (optional, but clean)
        self.angle %= (2 * math.pi) 
        
        # Calculate position relative to the player's *float vector* position
        center_x = self.player.pos.x
        center_y = self.player.pos.y
        
        self.pos_x = center_x + self.radius * math.cos(self.angle)
        self.pos_y = center_y + self.radius * math.sin(self.angle)
        
        self.rect.center = (int(self.pos_x), int(self.pos_y))
        if self.can_attack():
            # Use collide_rect_ratio for a smaller hitbox
            collided_list = pygame.sprite.spritecollide(
                self, self.enemy_group, False, 
                collided=pygame.sprite.collide_rect_ratio(0.8)
            )
            if collided_list:
                # Hit the first enemy in the list
                self.deal_damage(collided_list[0])

        self.image = self.base_image.copy() 
        
        if self.is_flashing:
            self.flash_timer += dt
            if self.flash_timer >= self.flash_duration:
                self.is_flashing = False
            else:
                # Add a white flash
                self.image.fill((150, 150, 150), special_flags=pygame.BLEND_RGB_ADD)