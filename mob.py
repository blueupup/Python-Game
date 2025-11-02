import pygame
from mobStats import MobStats
from mobStats import get_stats
import os
import sys
from particle import ParticleManager


def load_frames_from_folder(folder_path, scale):
    frames = []
    
    try:
        filenames = os.listdir(folder_path)
    except FileNotFoundError:
        print(f"--- FATAL ERROR (Folder Load) ---")
        print(f"Folder not found: {folder_path}")
        return []

    filenames.sort()

    for filename in filenames:
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            continue

        file_path = os.path.join(folder_path, filename)

        try:
            image = pygame.image.load(file_path).convert_alpha()
        except pygame.error as e:
            print(f"--- ERROR (Image Load) ---")
            print(f"Unable to load image: {file_path}")
            print(f"Pygame error: {e}")
            continue

        if scale != 1:
            new_width = int(image.get_width() * scale)
            new_height = int(image.get_height() * scale)
            image = pygame.transform.scale(image, (new_width, new_height))

        frames.append(image)

    if not frames:
        print(f"--- WARNING (Empty Folder) ---")
        print(f"No images were loaded from: {folder_path}")

    return frames

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, frames_folder_path, mob_type, scale, player_level, particle_manager, use_mask_collision=False, mask_path=None):
        super().__init__()

        # --- 1. Stats ---
        self.stats = get_stats(mob_type)
        if self.stats is None:
            raise ValueError(f"Failed to get stats for mob_type: {mob_type}")
        self.scale_to_player_level(player_level)
        self.particle_manager = particle_manager

        # --- 2. Animation ---
        self.frames = load_frames_from_folder(frames_folder_path, scale)
        if not self.frames:
            print(f"--- FATAL: No frames loaded for Enemy at {frames_folder_path} ---")
            fallback = pygame.Surface((32 * scale, 32 * scale))
            fallback.fill((255, 0, 0))
            self.frames = [fallback]
        
        self.frame_index = 0
        
        # --- STRUCTURAL FIX: Base vs. Drawn Image ---
        # self.base_image is the clean sprite.
        # self.image is the one that gets drawn (and modified by effects).
        self.base_image = self.frames[self.frame_index]
        self.image = self.base_image.copy() # .copy() is essential
        
        self.last_anim_update = pygame.time.get_ticks()
        self.anim_speed = self.stats.anim_speed

        # --- 3. Physics & Position ---
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        # self.rect is the VISUAL rect, used for drawing
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

        # --- 4. Collision ---
        # self.collision_box is the HITBOX rect, used for combat
        default_w = int(self.rect.width * 0.3)
        default_h = int(self.rect.height * 0.3)
        self.collision_box = pygame.Rect(0, 0, default_w, default_h)
        self.collision_box.center = self.rect.center
        
        self.use_mask_collision = use_mask_collision
        if use_mask_collision:
            # (Your mask logic was fine)
            if mask_path and os.path.exists(mask_path):
                mask_image = pygame.image.load(mask_path).convert_alpha()
                self.mask = pygame.mask.from_surface(mask_image)
            else:
                self.mask = pygame.mask.from_surface(self.frames[0])
        else:
            # We use the collision_box, so no mask is needed
            self.mask = None 

        # --- 5. State ---
        self.target = None
        self.state = 'idle'

        # --- 6. Combat ---
        self.touch_damage_cooldown = 1.0
        self.touch_damage_timer = 0.0 # Start ready to deal damage

        # --- 7. Hit Effect (NEW) ---
        self.isHit = False
        self.hit_stun_duration = 0.3   # How long the enemy flashes
        self.hit_stun_timer = 0.0
        self.flash_interval = 0.1  # How fast it flashes
        self.flash_timer = 0.0
        self.flash_toggle = True

    def scale_to_player_level(self, level):
        scale_factor = 1 + (level - 1) * 0.15
        self.stats.max_health = int(self.stats.max_health * scale_factor)
        self.stats.attack_power = int(self.stats.attack_power * scale_factor)
        self.stats.defense = int(self.stats.defense * scale_factor)
        self.stats.xp_reward = int(self.stats.xp_reward * scale_factor)
        self.stats.current_health = self.stats.max_health

    def take_damage(self, amount):
        # Prevent chain-stunning
        if self.isHit:
            return
            
        damage_taken = max(1, amount - self.stats.defense)
        self.stats.current_health -= damage_taken
        
        print(f"{self.stats.name} takes {damage_taken} damage, {self.stats.current_health} HP left.")
        
        # --- TRIGGER THE HIT EFFECT ---
        if self.stats.current_health > 0:
             self.isHit = True
             self.hit_stun_timer = 0.0  # Reset timers
             self.flash_timer = 0.0
             self.flash_toggle = True   # Start flash "on"

    def can_deal_touch_damage(self):
        return self.touch_damage_timer <= 0

    # --- BUG FIX: Deleted the duplicate deal_damage method ---
    def deal_damage(self, player_target):
        # 1. Reset the cooldown timer
        self.touch_damage_timer = self.touch_damage_cooldown
        
        # 2. Deal the damage
        damage = self.stats.attack_power
        print(f"[COMBAT] {self.stats.name} collides with player for {damage} damage!")
        player_target.take_damage(damage)
        
    def update(self, dt, player):
        # --- 1. Check for Death ---
        if self.stats.current_health <= 0:
            xp_drop = self.stats.xp_reward
            self.particle_manager.create_death_explosion(self.pos.x, self.pos.y)
            self.kill()
            return xp_drop
            
        self.image = self.base_image.copy()
            
        # --- 3. Update Timers ---
        if self.touch_damage_timer > 0:
            self.touch_damage_timer -= dt

        self.animate()

        # --- 5. Run AI Logic ---
        # BUG FIX: Deleted the redundant, duplicate AI block
        self.target = player.rect
        distance_to_target = self.pos.distance_to(self.target.center)

        if distance_to_target <= self.stats.aggro_range:
            self.state = 'chasing'
            try:
                direction = (pygame.math.Vector2(self.target.center) - self.pos).normalize()
                self.vel = direction * self.stats.speed
            except ValueError:
                self.vel = pygame.math.Vector2(0, 0) # On top of player
        else:
            self.state = 'idle'
            self.vel = pygame.math.Vector2(0, 0)
            
        self.pos += self.vel * dt
        self.rect.center = self.pos
        self.collision_box.center = self.rect.center

        # --- 7. Handle Hit-Stun / Flashing ---
        if self.isHit:
            self.hit_stun_timer += dt
            self.flash_timer += dt

            if self.hit_stun_timer >= self.hit_stun_duration:
                self.isHit = False
                self.hit_stun_timer = 0
                self.flash_timer = 0
            else:
                if self.flash_timer >= self.flash_interval:
                    self.flash_timer = 0
                    self.flash_toggle = not self.flash_toggle
                
                # Apply the white flash if toggled on
                if self.flash_toggle:
                    self.image.fill((150, 150, 150), special_flags=pygame.BLEND_RGB_ADD)

        return None

    def animate(self):
        # This method now updates self.base_image, not self.image
        now = pygame.time.get_ticks()
        
        if self.state == 'chasing': 
            if now - self.last_anim_update > self.anim_speed:
                self.last_anim_update = now
                self.frame_index = (self.frame_index + 1) % len(self.frames)
                self.base_image = self.frames[self.frame_index]
                
                # Flipping logic
                if self.vel.x < 0:
                   self.base_image = pygame.transform.flip(self.base_image, True, False)
        
        elif self.state == 'idle':
            self.frame_index = 0
            self.base_image = self.frames[self.frame_index]