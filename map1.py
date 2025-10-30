import pygame
import sys
from environment import Environment
from character import Character

# Camera update function and boundary restrictions
# This belongs in your main file, not the player file.
def update_camera(player_rect, camera_x, camera_y, SCREEN_W, SCREEN_H, MAP_W, MAP_H, camera_smoothness):
    camera_target_x = player_rect.centerx - SCREEN_W // 2
    camera_target_y = player_rect.centery - SCREEN_H // 2
    camera_target_x = max(0, min(camera_target_x, MAP_W - SCREEN_W))
    camera_target_y = max(0, min(camera_target_y, MAP_H - SCREEN_H))
    camera_x += (camera_target_x - camera_x) * camera_smoothness
    camera_y += (camera_target_y - camera_y) * camera_smoothness
    return camera_x, camera_y

def main():
    pygame.init()

    # --- Game Constants ---
    SCREEN_WIDTH, SCREEN_HEIGHT = 1080, 720
    WORLD_WIDTH, WORLD_HEIGHT = 2000, 2000
    FPS = 60
    BACKGROUND_IMAGE_PATH = "C:\\Users\\User\\Desktop\\Python-Game\\Images\\rm_GrassPlains_Night.png"

    Place_Holder_hp_image_path = "Images\pngtree-mushroom-pixel-art-vector-png-image_13852256.png"

    timer_font = pygame.font.SysFont("Arial", 24)
    total_time = 0.0
    
    # --- Setup ---
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("My Scrolling Game")
    clock = pygame.time.Clock()

    zoom_level = 2.0

    GAME_CANVAS_WIDTH = int(SCREEN_WIDTH/zoom_level)
    GAME_CANVAS_HEIGHT = int(SCREEN_HEIGHT/zoom_level) 

    game_canvas = pygame.Surface((GAME_CANVAS_WIDTH, GAME_CANVAS_HEIGHT))
    # --- Game Objects ---
    game_environment = Environment(WORLD_WIDTH, WORLD_HEIGHT, BACKGROUND_IMAGE_PATH)
    
    # Create the player instance!
    player = Character(WORLD_WIDTH // 2, WORLD_HEIGHT // 2)

    # This list will hold all your collision rects (from tiles, trees, etc.)
    collision_objects = [] 
    
    # --- Camera Variables ---
    camera_x = 0 
    camera_y = 0
    CAMERA_SMOOTHNESS = 0.05


    running = True
    while running:
        

        dt = clock.tick(FPS) / 1000.0 
        
        total_time += dt

        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Get all pressed keys
        keys = pygame.key.get_pressed()
      
        # 2. Update Logic
        # Pass dt, keys, and obstacles to the player's update method
        player.update(dt, keys, collision_objects)
        game_environment.update()

        # 3. Update Camera
        # Use your friend's smooth camera function
        camera_x, camera_y = update_camera(
            player.rect, camera_x, camera_y, 
            GAME_CANVAS_WIDTH, GAME_CANVAS_HEIGHT,
            WORLD_WIDTH, WORLD_HEIGHT, 
            CAMERA_SMOOTHNESS
        )

        game_canvas.fill((0,0,0))
        # Draw the background
        game_environment.draw(game_canvas, camera_x, camera_y) 

        player.draw(game_canvas, camera_x, camera_y)

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

        hp_image = pygame.image.load(Place_Holder_hp_image_path).convert_alpha()
        hp_image = pygame.transform.scale(hp_image, (40, 40))
        hp_image_rect = hp_image.get_rect()
        hp_image_rect.topleft = (SCREEN_WIDTH - 10, 10)

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