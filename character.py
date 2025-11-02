import pygame
from CharacterStats import CharacterStats 
from OrbitalNode import OrbitalNode
from particle import ParticleManager
from meeleehitbox import MeleeHitbox 
from meleesprite import MeleeWeaponSprite
import math

def load_sprite_sheet(sheet_path, frame_width, frame_height, scale):
    try:
        sheet = pygame.image.load(sheet_path).convert_alpha()
    except pygame.error as e:
        print(f"--- FATAL ERROR (Sprite Sheet) ---")
        print(f"Unable to load sprite sheet image: {sheet_path}")
        print(f"Pygame error: {e}")
        return []

    sheet_width, sheet_height = sheet.get_size()
    frames = []

    for y in range(0, sheet_height, frame_height):
        for x in range(0, sheet_width, frame_width):
            frame_surface = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            frame_surface.blit(sheet, (0, 0), pygame.Rect(x, y, frame_width, frame_height))
            
            if scale != 1:
                frame_surface = pygame.transform.scale(
                    frame_surface, 
                    (frame_width * scale, frame_height * scale)
                )
            frames.append(frame_surface)

    return frames

class Character(pygame.sprite.Sprite):
    def __init__(self, x, y):
        
        super().__init__()

        self.pos = pygame.math.Vector2(x, y)

        self.stats = CharacterStats(level=1, base_health=50, base_attack=10)
        
        self.all_sprites_group = None 
        self.enemy_group = None
        self.particle_manager = None

        self.orbitals = pygame.sprite.Group()
        self.melee_hitboxes = pygame.sprite.Group() # Holds active swings
        self.visible_weapon_sprites = pygame.sprite.Group()
        self.active_weapon = None
        self.attack_timer = 0.0 # Cooldown for melee attackse

        self.is_iframes = False
        self.iframe_duration = 1.0
        self.iframe_timer = 0.0

        self.flash_interval = 0.2
        self.flash_timer = 0.0


        SPRITE_FRAME_W, SPRITE_FRAME_H, SPRITE_SCALE = 32, 32, 1.5
        self.FRAME_WIDTH = SPRITE_FRAME_W * SPRITE_SCALE
        self.FRAME_HEIGHT = SPRITE_FRAME_H * SPRITE_SCALE
        self.frame_speed = 0.15

        self.frame_index = 0
        self.frame_timer = 0.0
        self.flash_toggle = True


        self.idle_frames = load_sprite_sheet("Images\standing.png", SPRITE_FRAME_W, SPRITE_FRAME_H, SPRITE_SCALE)
        self.moving_frames = load_sprite_sheet("Images\moving.png", SPRITE_FRAME_W, SPRITE_FRAME_H, SPRITE_SCALE)


        if not self.idle_frames:
            print("--- CHARACTER ERROR ---")
            print("Idle frames failed to load. Using fallback red block.")
            self.idle_frames = [pygame.Surface((self.FRAME_WIDTH, self.FRAME_HEIGHT))]
            self.idle_frames[0].fill((255, 0, 0))
        
        if not self.moving_frames:
            self.moving_frames = self.idle_frames

        self.image = self.idle_frames[self.frame_index]
        self.rect = self.image.get_rect(center=(int(self.pos.x), int(self.pos.y)))

        self.mask = pygame.mask.from_surface(self.image)

        shadow_width = int(self.rect.width * 0.6)
        shadow_height = int(self.rect.height * 0.2)
        if shadow_width > 0 and shadow_height > 0:
            # 1. Create the base ellipse
            shadow_surf = pygame.Surface((shadow_width, shadow_height), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surf, (0, 0, 0, 100), (0, 0, shadow_width, shadow_height))
            
            # 2. Rotate it ONCE and save it
            self.shadow_image = pygame.transform.rotate(shadow_surf, 20)
            
            # 3. Store the shadow's offsets (your magic numbers)
            # This pre-calculates the offset from the sprite's position
            self.shadow_offset_x = self.rect.width // 2 - self.shadow_image.get_width() / 4.8
            self.shadow_offset_y = self.rect.height - self.shadow_image.get_height() / 0.75
        else:
            self.shadow_image = None
    

        self.collision_box = pygame.Rect(
            0, 0, 
            self.FRAME_WIDTH * 0.5,
            self.FRAME_HEIGHT * 0.5
        )
        self.collision_box.center = self.rect.center

        # --- State Data ---
        self.speed = 100 # Pixels per second
        self.is_moving = False
        self.facing_right = True

    def get_player_collision_box(self):
        self.collision_box.center = self.rect.center
        return self.collision_box
    
    def set_particle_manager(self, manager):
        self.particle_manager = manager

    def set_groups(self, all_sprites, enemy_group):
        self.all_sprites_group = all_sprites
        self.enemy_group = enemy_group

    def equip_weapon(self, weapon_blueprint):

        print(f"[EQUIP] Equipping {weapon_blueprint.name}")
        
        for node in self.orbitals:
            node.kill()
        for hitbox in self.melee_hitboxes:
            hitbox.kill()
        for sprite in self.visible_weapon_sprites:
            sprite.kill()

        self.active_weapon = weapon_blueprint
        self.attack_timer = 0.0 # Ready to attack
        
        if self.active_weapon.weapon_type == "orbital":
            self.setup_orbital_weapon() 
        
        elif self.active_weapon.weapon_type == "melee":
            self.attack_timer = self.active_weapon.hit_cooldown
            print(f"Equipped melee: {self.active_weapon.name}")

    def setup_orbital_weapon(self):
        if self.enemy_group is None or self.all_sprites_group is None:
            print("--- FATAL (Character): Cannot setup orbitals, groups not set!")
            return
            
        # Load the graphic
        try:
            image = pygame.image.load(self.active_weapon.image_path).convert_alpha()
            w, h = image.get_size()
            scale = self.active_weapon.scale
            image = pygame.transform.scale(image, (int(w * scale), int(h * scale)))
        except Exception as e:
            print(f"--- WEAPON ERROR: Failed to load image {self.active_weapon.image_path} ---")
            print(e)
            image = pygame.Surface((10, 10))
            image.fill((255, 0, 255))

        count = self.active_weapon.count
        angle_step = (2 * math.pi) / count 
        
        for i in range(count):
            start_angle = i * angle_step
            node = OrbitalNode(
                player=self,
                radius=self.active_weapon.radius,
                rotation_speed=self.active_weapon.rotation_speed,
                weapon_damage=self.active_weapon.weapon_damage,
                hit_cooldown=self.active_weapon.hit_cooldown,
                image=image,
                start_angle=start_angle,
                particle_manager=self.particle_manager, # Pass refs
                enemy_group=self.enemy_group           # Pass refs
            )
            self.orbitals.add(node)
            self.all_sprites_group.add(node) # Add to main draw group!
            
        print(f"Equipped {self.active_weapon.name} with {count} nodes.")

    def attack(self):
        if self.active_weapon is None or self.enemy_group is None:
            return

        if self.active_weapon.weapon_type == "melee":
            # Reset cooldown
            self.attack_timer = self.active_weapon.hit_cooldown
            
            # Create the hitbox
            hitbox = MeleeHitbox(
                self, 
                self.active_weapon, 
                self.enemy_group, 
                self.particle_manager
            )
            
            self.melee_hitboxes.add(hitbox)
            if self.all_sprites_group is not None:
                self.all_sprites_group.add(hitbox)
                
            weapon_sprite = MeleeWeaponSprite(
                self, 
                self.active_weapon
            )
            self.visible_weapon_sprites.add(weapon_sprite)
            if self.all_sprites_group is not None:
                self.all_sprites_group.add(weapon_sprite)


    def draw_shadow(self, surface, screen_x, screen_y):
        if self.shadow_image:
            shadow_x = int(screen_x + self.shadow_offset_x)
            shadow_y = int(screen_y + self.shadow_offset_y)
            
            surface.blit(self.shadow_image, (shadow_x, shadow_y))

    def take_damage(self, amount):
            if self.is_iframes:
                return
            
            if self.particle_manager:
                self.particle_manager.create_player_damage_effect(self.pos.x, self.pos.y)

            is_dead = self.stats.take_damage(amount)

            if is_dead:
                self.kill()
            else:
                self.is_iframes = True
                self.iframe_timer = 0.0
                self.flash_timer = 0.0
                self.flash_toggle = True
    
    def special_effect():
        pass

    def update(self, dt, keys):
    
        # --- 1. Handle Movement Input ---
        move_x = (1 if keys[pygame.K_d] else 0) - (1 if keys[pygame.K_a] else 0)
        move_y = (1 if keys[pygame.K_s] else 0) - (1 if keys[pygame.K_w] else 0)

        move_vector = pygame.Vector2(move_x, move_y)
        self.is_moving = move_vector.length_squared() > 0
        move_amount = self.speed * dt 

        if self.is_moving:
            move_vector = move_vector.normalize()

            self.pos += move_vector * move_amount
            
            # Update the integer rect from the float vector
            self.rect.center = self.pos 
            # --- END OF MOVEMENT LOGIC ---

            # Update facing direction
            if move_vector.x > 0:
                self.facing_right = True
            elif move_vector.x < 0:
                self.facing_right = False
        
        # --- 4. Handle Animation ---
        self.frame_timer += dt
        if self.frame_timer >= self.frame_speed:
            self.frame_timer = 0
            self.frame_index += 1

        frames = self.moving_frames if self.is_moving else self.idle_frames

        self.rect.center = (int(self.pos.x), int(self.pos.y))

        self.collision_box.center = self.rect.center

        # Make sure we don't crash if an animation list is empty
        if not frames:
            self.image = pygame.Surface((32, 32)) # Placeholder
            self.image.fill((255, 0, 255)) # Bright pink error color
        else:
            self.frame_index %= len(frames)
            self.image = frames[self.frame_index].copy() # .copy() is vital

        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

        if self.is_iframes:
            # Increment timers
            self.iframe_timer += dt
            self.flash_timer += dt

            # Check if it's time to end invincibility
            if self.iframe_timer >= self.iframe_duration:
                self.is_iframes = False
                self.iframe_timer = 0
                self.flash_timer = 0
                self.flash_toggle = True  # Reset toggle
                self.image.set_alpha(255) # Ensure visibility is reset
            
            # Handle flashing *only if* duration is not over
            else:
                if self.flash_timer >= self.flash_interval:
                    self.flash_timer = 0
                    # Flip the flash state
                    self.flash_toggle = not self.flash_toggle
                
                if not self.flash_toggle:
                    self.image.fill((170, 170, 170), special_flags=pygame.BLEND_RGB_ADD)
                
                # (If self.flash_toggle is True, we do nothing,
                #  letting the normal sprite from section 4 draw)

        else:
            if self.image.get_alpha() != 255:
                self.image.set_alpha(255)
        
        if self.active_weapon:
            self.attack_timer -= dt
            
            # Check if we should auto-attack
            if self.attack_timer <= 0:
                self.attack() # Call the new attack method
        

        self.orbitals.update(dt)
        self.melee_hitboxes.update(dt)
        self.visible_weapon_sprites.update(dt)

