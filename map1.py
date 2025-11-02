import pygame
import sys
from environment import Environment
from character import Character
from mob import Enemy
import math
import random
from weapon import MUSHROOM_SONG, STORM_BLADE
from UIManager import LevelUpUI, GameOverUI 
from particle import ParticleManager
from meeleehitbox import MeleeHitbox

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
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()

    # --- Game Constants ---
    SCREEN_WIDTH, SCREEN_HEIGHT = 1080, 720
    WORLD_WIDTH, WORLD_HEIGHT = 3500,3500
    FPS = 60
    BACKGROUND_IMAGE_PATH = "Images\\rm_GrassPlains_Night.png"

    Place_Holder_hp_image_path = r"Images\pixil-frame-0_1_-removebg-preview.png"

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

    all_sprites = CameraGroup()
    enemy_group = pygame.sprite.Group()
    
    player = Character(WORLD_WIDTH // 2, WORLD_HEIGHT // 2)

    hit_sound = pygame.mixer.Sound(r"Images\atk.mp3")
    levelup_sound = pygame.mixer.Sound(r"Images\chest2.mp3")

    particle_manager = ParticleManager(hit_sound=hit_sound, levelup=levelup_sound)
    player.set_particle_manager(particle_manager)
    player.set_groups(all_sprites, enemy_group)


    player.equip_weapon(MUSHROOM_SONG)
    
    all_sprites.add(player)

    level_up_screen = LevelUpUI(
        player, 
        all_sprites, 
        GAME_CANVAS_WIDTH, 
        GAME_CANVAS_HEIGHT
    )

    game_over_screen = GameOverUI(GAME_CANVAS_WIDTH, GAME_CANVAS_HEIGHT)

    game_state = 'running'

    # --- Camera Variables ---
    camera_x = 0 
    camera_y = 0
    CAMERA_SMOOTHNESS = 0.05

    spawn_timer = 0.0
    
    base_spawn_interval = 2.5       
    min_spawn_interval = 0.5        
    time_to_max_difficulty = 300.0 

    POINTS_PER_KILL = 50
    POINTS_PER_SECOND = 1

    total_time = 0.0
    kill_count = 0

    try:
        hp_image_raw = pygame.image.load(Place_Holder_hp_image_path).convert_alpha()
        hp_image = pygame.transform.scale(hp_image_raw, (40, 40))
    except Exception as e:
        print(f"Error loading HP image: {e}")
        hp_image = pygame.Surface((40, 40))
        hp_image.fill((255, 0, 255))



    running = True
    while running:
        
        dt = clock.tick(FPS) / 1000.0
        
        particle_manager.update(dt) 

        events = pygame.event.get()
        
        for event in events:
            if event.type == pygame.QUIT:
                return 'quit' 

            if game_state == 'level_up':
                action = level_up_screen.handle_event(event, zoom_level)
                if action == 'running':
                    particle_manager.create_level_up_burst(player.pos.x, player.pos.y)
                    game_state = 'running'
            elif game_state == 'game_over':
                action = game_over_screen.handle_event(event, zoom_level)
                if action == 'restart':
                    return {
                        "status": "game_over",
                        "score": game_over_screen.final_score,
                        "time": game_over_screen.final_time,
                        "kills": game_over_screen.kill_count
                    }

        if game_state == 'running':
            if dt == 0: continue 

            total_time += dt
            spawn_timer += dt

            keys = pygame.key.get_pressed()

            if keys[pygame.K_l]: # Debug key
                 particle_manager.create_level_up_burst(player.pos.x, player.pos.y)


            difficulty_progress = min(1.0, total_time / time_to_max_difficulty)
            current_spawn_interval = base_spawn_interval - (base_spawn_interval - min_spawn_interval) * difficulty_progress
            
            if spawn_timer >= current_spawn_interval:
                spawn_timer = 0.0
                try:
                    margin = 100
                    spawn_radius = max(GAME_CANVAS_WIDTH, GAME_CANVAS_HEIGHT) / 2 + margin
                    player_x = player.pos.x
                    player_y = player.pos.y
                    angle = random.uniform(0, 2 * math.pi)
                    spawn_x = player_x + math.cos(angle) * spawn_radius
                    spawn_y = player_y + math.sin(angle) * spawn_radius
                    
                    if random.random() < 0.5: # 50% chance for slime
                        new_enemy = Enemy(
                            x=spawn_x, 
                            y=spawn_y, 
                            frames_folder_path=r"Images\Slime", 
                            mob_type="slime", 
                            scale=1, 
                            player_level=player.stats.level,
                            particle_manager=particle_manager,
                            use_mask_collision=True, 
                            mask_path=r"Images\spr_Soratomo_mask.png"
                        )
                    else: # 50% chance for bunny
                        new_enemy = Enemy(
                            x=spawn_x,
                            y=spawn_y,
                            frames_folder_path=r"Images\Nousagi",
                            mob_type="bunny",
                            scale=1,
                            player_level=player.stats.level,
                            particle_manager=particle_manager
                        )
                    
                    all_sprites.add(new_enemy)
                    enemy_group.add(new_enemy)
                    
                    
                except Exception as e:
                    print(f"FATAL: Error spawning enemy: {e}")

            player.update(dt, keys)
            game_environment.update()
            
            player_hitbox = player.get_player_collision_box()

            for enemy in enemy_group:
                xp_reward = enemy.update(dt, player) 

                if xp_reward is not None:
                    kill_count += 1
                    if player.stats.add_xp(xp_reward):
                        game_state = 'level_up'
                        level_up_screen.activate()
                        print("--- LEVEL UP! --- Pausing game.")

            for enemy in enemy_group:
                if player_hitbox.colliderect(enemy.collision_box):
                    if enemy.can_deal_touch_damage():
                        enemy.deal_damage(player)

            camera_x, camera_y = update_camera(
                player.rect, camera_x, camera_y, 
                GAME_CANVAS_WIDTH, GAME_CANVAS_HEIGHT,
                WORLD_WIDTH, WORLD_HEIGHT, 
                CAMERA_SMOOTHNESS
            )
            
            if player.stats.current_health <= 0:
                game_state = 'game_over'
                score_from_time = int(total_time * POINTS_PER_SECOND)
                score_from_kills = kill_count * POINTS_PER_KILL
                final_score = score_from_time + score_from_kills
                game_over_screen.activate(final_score, total_time, kill_count)
                print("--- GAME OVER ---")
                player.kill()

        
        # --- Drawing ---
        game_canvas.fill((0,0,0))
        game_environment.draw(game_canvas, camera_x, camera_y) 
        all_sprites.draw(game_canvas, camera_x, camera_y)
        particle_manager.draw(game_canvas, camera_x, camera_y)

        
        # --- UI Drawing ---
        if game_state == 'level_up':
            level_up_screen.draw(game_canvas)
        elif game_state == 'game_over':
            game_over_screen.draw(game_canvas)

        screen.fill((0,0,0))
        scaled_canvas = pygame.transform.scale(game_canvas, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(scaled_canvas, (0, 0))

        if game_state != 'game_over':
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
            health_ratio = max(0, current_hp / max_hp) 

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

    return 'quit'


if __name__ == "__main__":
    
    while True:
        action = main() # Run the game
        
        if action == 'quit':
            break # Exit the `while True` loop
        
        if action == 'restart':
            print("--- RESTARTING GAME ---")
            continue # Go to the top of the `while True` loop and call main() again
            

    print("--- SHUTTING DOWN ---")
    pygame.quit()
    sys.exit()