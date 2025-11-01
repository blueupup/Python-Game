import pygame
from mobStats import MobStats
from mobStats import get_stats
import os
import sys

def load_frames_from_folder(folder_path, scale):
    frames = []
    
    try:
        # Get all filenames in the folder
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
    def __init__(self, x, y, frames_folder_path, mob_type, scale, player_level):
        super().__init__()
        
        try:
            # Call your new factory function directly
            self.stats = get_stats(mob_type)
            
            # This check is critical.
            # get_stats() returns None if the mob_type is invalid.
            if self.stats is None:
                # This will be caught by the except block
                raise ValueError(f"Failed to get stats for mob_type: {mob_type}")

        except Exception as e:
            print(f"--- FATAL: Failed to initialize stats for {mob_type} ---")
            print(e)
            raise

        self.scale_to_player_level(player_level) 

        self.frames = load_frames_from_folder(frames_folder_path, scale)
        if not self.frames:
            print(f"--- FATAL: No frames loaded for Enemy at {frames_folder_path} ---")
            self.kill()
            return
            
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.last_anim_update = pygame.time.get_ticks()
        self.anim_speed = self.stats.anim_speed
        
        # --- 4. Physics & Position ---
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)

        self.collision_box = pygame.Rect(
            0, 0, 
            self.FRAME_WIDTH * 0.5,
            self.FRAME_HEIGHT * 0.5
        )
        self.collision_box.center = self.rect.center

        # --- 5. AI & State ---
        self.target = None
        self.state = 'idle'

    def scale_to_player_level(self, level):
        scale_factor = 1 + (level - 1) * 0.15

        self.stats.max_health = int(self.stats.max_health * scale_factor)
        self.stats.attack_power = int(self.stats.attack_power * scale_factor)
        self.stats.defense = int(self.stats.defense * scale_factor)
        self.stats.xp_reward = int(self.stats.xp_reward * scale_factor)

        self.stats.current_health = self.stats.max_health


    def update(self, dt, player):
        """
        The "brain" of the enemy. Handles animation, AI, and movement.
        - dt: Delta time (time since last frame) for framerate-independent movement.
        - player_rect: The rect of the player, for AI targeting.
        - collision_objects: A list/group of rects to collide with (e.g., walls).
        """

        #Check for Death
        if self.stats.current_health <= 0:
            xp_drop = self.stats.xp_reward
            self.kill()
            return xp_drop
            
        self.animate()

        self.rect.center = (int(self.pos.x), int(self.pos.y))

        self.collision_box.center = self.rect.center


        # --- 3. Run AI Logic ---
        # This is a simple state machine.
        self.target = player.rect
        distance_to_target = self.pos.distance_to(self.target.center)

        # State: Chasing
        if distance_to_target <= self.stats.aggro_range and distance_to_target > self.stats.attack_range:
            self.state = 'chasing'
            
            # Calculate direction vector to player
            direction = (pygame.math.Vector2(self.target.center) - self.pos).normalize()
            self.vel = direction * self.stats.speed
        
        # State: Attacking (close enough)
        elif distance_to_target <= self.stats.attack_range:
            self.state = 'attacking'
            self.vel = pygame.math.Vector2(0, 0) # Stop moving
            # --- TODO: Add attack logic here (e.g., start an attack timer) ---
            # print(f"{self.stats.name} attacks!")

        # State: Idle (too far)
        else:
            self.state = 'idle'
            self.vel = pygame.math.Vector2(0, 0) # Stop moving
            
        # --- 4. Apply Movement ---
        self.pos += self.vel * dt
        self.rect.center = self.pos
        
        return None

    def animate(self):
        now = pygame.time.get_ticks()
        if self.state == 'chasing': 
            if now - self.last_anim_update > self.anim_speed:
                self.last_anim_update = now
                self.frame_index = (self.frame_index + 1) % len(self.frames)
                self.image = self.frames[self.frame_index]
                # if self.vel.x < 0:
                #    self.image = pygame.transform.flip(self.image, True, False)
        
        # If idle, you might set it to the first frame
        elif self.state == 'idle':
            self.frame_index = 0
            self.image = self.frames[self.frame_index]