import pygame
from CharacterStats import CharacterStats

class Enemy(pygame.sprite.Sprite):
    
    def __init__(self, x, y, sprite_sheet_path, frame_w, frame_h, scale):
        super().__init__()
        

        self.stats = None 

        # self.idle_frames = load_spritesheet(...)
        # self.move_frames = load_spritesheet(...)

        self.image = pygame.Surface((32, 32))
        self.image.fill((200, 50, 50)) 

        self.rect = self.image.get_rect(center=(x, y))
        
        # --- AI & State ---
        self.is_moving = False
        self.target = None

    def update(self, dt, player_rect, collision_objects):

        if self.stats is None:
            return
        
        if self.stats.current_health <= 0:
            self.kill()

    def draw(self, screen_surface, camera_x, camera_y):

        screen_x = self.rect.x - camera_x
        screen_y = self.rect.y - camera_y
        screen_surface.blit(self.image, (screen_x, screen_y))
