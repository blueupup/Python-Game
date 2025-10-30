import pygame
from CharacterStats import CharacterStats

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

        self.stats = CharacterStats(level=1, base_health=100, base_attack=10)
        
        SPRITE_FRAME_W, SPRITE_FRAME_H, SPRITE_SCALE = 32, 32, 1.5
        self.FRAME_WIDTH = SPRITE_FRAME_W * SPRITE_SCALE
        self.FRAME_HEIGHT = SPRITE_FRAME_H * SPRITE_SCALE
        self.frame_speed = 0.15

        self.idle_frames = load_sprite_sheet("C:\\Users\\User\\Desktop\\Python-Game\\Images\\standing.png", SPRITE_FRAME_W, SPRITE_FRAME_H, SPRITE_SCALE)
        self.moving_frames = load_sprite_sheet("C:\\Users\\User\\Desktop\\Python-Game\\Images\\moving.png", SPRITE_FRAME_W, SPRITE_FRAME_H, SPRITE_SCALE)

        if not self.idle_frames:
            print("--- CHARACTER ERROR ---")
            print("Idle frames failed to load. Using fallback red block.")
            self.idle_frames = [pygame.Surface((self.FRAME_WIDTH, self.FRAME_HEIGHT))]
            self.idle_frames[0].fill((255, 0, 0))
        
        if not self.moving_frames:
            self.moving_frames = self.idle_frames

        self.frame_index = 0
        self.frame_timer = 0.0
        
        self.image = self.idle_frames[self.frame_index]
        
        self.rect = self.image.get_rect(center=(x,y))

        self.collision_box = pygame.Rect(
            0, 0, 
            self.FRAME_WIDTH * 0.5,
            self.FRAME_HEIGHT * 0.2
        )
        self.collision_box.midbottom = self.rect.midbottom

        # --- State Data ---
        self.speed = 200 # Pixels per second
        self.is_moving = False
        self.facing_right = True

    def get_player_collision_box(self):
        self.collision_box.midbottom = self.rect.midbottom
        return self.collision_box


    def update(self, dt, keys, collision_objects):
        
        # --- 1. Handle Movement & Collisions ---
        move_x = (1 if keys[pygame.K_d] else 0) - (1 if keys[pygame.K_a] else 0)
        move_y = (1 if keys[pygame.K_s] else 0) - (1 if keys[pygame.K_w] else 0)

        move_vector = pygame.Vector2(move_x, move_y)
        self.is_moving = move_vector.length_squared() > 0
        move_amount = self.speed * dt 

        if self.is_moving:
            move_vector = move_vector.normalize()

            # --- X-axis collision ---
            current_col_box = self.get_player_collision_box()
            new_box_x = current_col_box.move(move_vector.x * move_amount, 0)
            
            self.rect.x += move_vector.x * move_amount

            # --- Y-axis collision ---
            current_col_box = self.get_player_collision_box() # Get updated position
            new_box_y = current_col_box.move(0, move_vector.y * move_amount)
            
            # if not self.check_collision_with_objects(new_box_y, collision_objects):
            self.rect.y += move_vector.y * move_amount

            # Update facing direction
            if move_vector.x > 0:
                self.facing_right = True
            elif move_vector.x < 0:
                self.facing_right = False
        
        # --- 2. Handle Animation ---
        self.frame_timer += dt
        if self.frame_timer >= self.frame_speed:
            self.frame_timer = 0
            self.frame_index += 1

        frames = self.moving_frames if self.is_moving else self.idle_frames

        self.frame_index %= len(frames)
        self.image = frames[self.frame_index] 

        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)

    def draw(self, screen_surface, camera_x, camera_y):
        """Draws the player relative to the camera."""
        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y - camera_y
        screen_surface.blit(self.image, (screen_x, screen_y))
        
        # --- (DEBUG) Draw the collision box ---
        # col_box_screen_x = self.collision_box.x - camera_x
        # col_box_screen_y = self.collision_box.y - camera_y
        # debug_col_rect = pygame.Rect(col_box_screen_x, col_box_screen_y, 
        #                             self.collision_box.width, self.collision_box.height)
        # pygame.draw.rect(screen_surface, (0, 255, 0), debug_col_rect, 2)

