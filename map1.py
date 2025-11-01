import pygame
import sys
from environment import Environment
from character import Character
from mob import Enemy
import math


class CameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        
    def draw(self, surface, camera_x, camera_y):
        for sprite in self.sprites():
            screen_x = sprite.rect.x - camera_x
            screen_y = sprite.rect.y - camera_y

            if hasattr(sprite, 'draw_shadow'):
                 sprite.draw_shadow(surface, screen_x, screen_y)
            
            surface.blit(sprite.image, (screen_x, screen_y))

def update_camera(player_rect, camera_x, camera_y, SCREEN_W, SCREEN_H, MAP_W, MAP_H, camera_smoothness):

    camera_target_x = player_rect.centerx - SCREEN_W // 2
    camera_target_y = player_rect.centery - SCREEN_H // 2


    camera_target_x = max(0, min(camera_target_x, MAP_W - SCREEN_W))
    camera_target_y = max(0, min(camera_target_y, MAP_H - SCREEN_H))
    

    new_camera_x = camera_x + (camera_target_x - camera_x) * camera_smoothness
    new_camera_y = camera_y + (camera_target_y - camera_y) * camera_smoothness
    
    return new_camera_x, new_camera_y

def main():
    pygame.init()

    # --- Game Constants ---
    SCREEN_WIDTH, SCREEN_HEIGHT = 1080, 720
    WORLD_WIDTH, WORLD_HEIGHT = 2000, 2000
    FPS = 60
    BACKGROUND_IMAGE_PATH = "Images\\rm_GrassPlains_Night.png"

    Place_Holder_hp_image_path = "Images\\pngtree-mushroom-pixel-art-vector-png-image_13852256.png"

    timer_font = pygame.font.SysFont("Arial", 24)
    total_time = 0.0
    
    # --- Setup ---
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("My Scrolling Game")
    clock = pygame.time.Clock()

    zoom_level = 2.0

    GAME_CANVAS_WIDTH = int(SCREEN_WIDTH/zoom_level)
    GAME_CANVAS_HEIGHT = int(SCREEN_HEIGHT/zoom_level) 

    #Spawn Radius

    game_canvas = pygame.Surface((GAME_CANVAS_WIDTH, GAME_CANVAS_HEIGHT))
    # --- Game Objects ---
    game_environment = Environment(WORLD_WIDTH, WORLD_HEIGHT, BACKGROUND_IMAGE_PATH)

    all_sprites = CameraGroup()
    enemy_group = pygame.sprite.Group()
    
    # Create the player instance!
    player = Character(WORLD_WIDTH // 2, WORLD_HEIGHT // 2)
    
    all_sprites.add(player)

    # --- Camera Variables ---
    camera_x = 0 
    camera_y = 0
    CAMERA_SMOOTHNESS = 0.05

    spawn_timer = 0.0

    spawn_interval = 2.5

    try:
        hp_image_raw = pygame.image.load(Place_Holder_hp_image_path).convert_alpha()
        hp_image = pygame.transform.scale(hp_image_raw, (40, 40))
    except Exception as e:
        print(f"Error loading HP image: {e}")
        # Create a fallback surface
        hp_image = pygame.Surface((40, 40))
        hp_image.fill((255, 0, 255))

    running = True
    while running:
        

        dt = clock.tick(FPS) / 1000.0 
        
        total_time += dt

        spawn_timer += dt

        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        if spawn_timer >= spawn_interval:
            spawn_timer = 0.0 # Reset the timer for the next spawn
            
            # --- This is the spawn logic from before ---
            try:
                # Calculate a random position around the player
                spawn_radius = (GAME_CANVAS_WIDTH + GAME_CANVAS_HEIGHT) / 2
                player_x = player.pos.x
                player_y = player.pos.y
                angle = 150
                spawn_x = player_x + math.cos(angle) * spawn_radius
                spawn_y = player_y + math.sin(angle) * spawn_radius

                # Create the new enemy
                bunny = Enemy(
                    x=spawn_x,
                    y=spawn_y,
                    frames_folder_path="Images\\Nousagi", # Adjust path
                    mob_type="bunny",                      # Must be in mobStats.py
                    scale=1,                               # Adjust scale
                    player_level=player.stats.level        # Assumes player has .stats.level
                )
                
                # Add it to the main groups
                all_sprites.add(bunny)
                enemy_group.add(bunny)
                
                print("--- A new enemy spawned! ---") # Debug message
                
            except Exception as e:
                print(f"FATAL: Error spawning enemy: {e}")

        # Get all pressed keys
        keys = pygame.key.get_pressed()
      
        player.update(dt, keys)

        enemy_group.update(dt, player)
        game_environment.update()

        camera_x, camera_y = update_camera(
            player.rect, camera_x, camera_y, 
            GAME_CANVAS_WIDTH, GAME_CANVAS_HEIGHT,
            WORLD_WIDTH, WORLD_HEIGHT, 
            CAMERA_SMOOTHNESS
        )

        game_canvas.fill((0,0,0))
        # Draw the background
        game_environment.draw(game_canvas, camera_x, camera_y) 

        all_sprites.draw(game_canvas, camera_x, camera_y)

        player_box_screen_x = player.collision_box.x - camera_x
        player_box_screen_y = player.collision_box.y - camera_y
        debug_player_rect = pygame.Rect(player_box_screen_x, player_box_screen_y, 
                                        player.collision_box.width, player.collision_box.height)
        pygame.draw.rect(game_canvas, (0, 255, 0), debug_player_rect, 2)

        screen.fill((0,0,0))

        scaled_canvas = pygame.transform.scale(game_canvas, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(scaled_canvas, (0, 0))

        total_seconds = int(total_time)
        minutes = total_seconds // 60
        seconds = total_seconds % 60

        time_string = f"{minutes:02}:{seconds:02}"

        total_time_text = timer_font.render(time_string, True, (255, 255, 255))
        time_rect = total_time_text.get_rect()
        time_rect.topright = (SCREEN_WIDTH -  10, 10)

        screen.blit(total_time_text, time_rect)

        screen.blit(hp_image, (10, 10))

        current_hp = player.stats.current_health
        max_hp = player.stats.max_health
        health_ratio = current_hp / max_hp

        bar_width = 200
        bar_height = 25
        bar_x = 60
        bar_y = 15

        current_health_width = bar_width * health_ratio

        background_bar_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        health_bar_rect = pygame.Rect(bar_x, bar_y, current_health_width, bar_height)

        pygame.draw.rect(screen, (50, 50, 50), background_bar_rect)
        pygame.draw.rect(screen, (255, 0, 0), health_bar_rect)

        pygame.display.flip()

    # --- Shutdown ---
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()