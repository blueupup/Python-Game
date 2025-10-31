import pygame
import sys
import pytmx
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))  # add current dir to path

from utils.ts_movement import handle_player_movement, update_animation, update_camera
from utils import ts_debug  # !!! debug tool

# Global Virable:Player Exit Point
last_exit_position = None

# Unified absolute path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
def get_path(*paths):
    return os.path.join(BASE_DIR, *paths)

# Load tiled collision / trigger
def load_tiled_collision(tmx_file, collision_layer_name='collision', trigger_layer_name='triggers'):
    if pytmx is None:
        return [], []

    try:
        tmx_data = pytmx.load_pygame(tmx_file)
        collision_objects = []
        trigger_objects = []

        for layer in tmx_data.visible_layers:
            if not isinstance(layer, pytmx.TiledObjectGroup):
                continue

            layer_name = layer.name.lower()
            if layer_name not in [collision_layer_name.lower(), trigger_layer_name.lower()]:
                continue

            for obj in layer:
                name = getattr(obj, "name", "") or "Unnamed"
                if hasattr(obj, "points") and obj.points:
                    points = [(px, py) for px, py in obj.points]
                    obj_data = {"type": "polygon", "points": points, "name": name}
                else:
                    rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                    obj_data = {"type": "rect", "rect": rect, "name": name}

                if layer_name == collision_layer_name.lower():
                    collision_objects.append(obj_data)
                elif layer_name == trigger_layer_name.lower():
                    trigger_objects.append(obj_data)

        return collision_objects, trigger_objects

    except Exception as e:
        print(f"Load Tiled file fail !!!: {e}")
        return [], []

# Polygon collision detection
def point_in_polygon(point, polygon):
    x, y = point
    n = len(polygon)
    inside = False
    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def check_rect_polygon_collision(rect, polygon):
    corners = [
        (rect.left, rect.top),
        (rect.right, rect.top),
        (rect.left, rect.bottom),
        (rect.right, rect.bottom)
    ]
    for corner in corners:
        if point_in_polygon(corner, polygon):
            return True
    for point in polygon:
        if rect.collidepoint(point):
            return True
    return False

def check_collision_with_objects(player_rect, collision_objects):
    for obj in collision_objects:
        if obj["type"] == "rect":
            if player_rect.colliderect(obj["rect"]):
                return True
        elif obj["type"] == "polygon":
            if check_rect_polygon_collision(player_rect, obj["points"]):
                return True
    return False

# Shadow and player collision box
def draw_shadow(surface, player_rect, camera_x, camera_y):
    shadow_width = player_rect.width * 0.6
    shadow_height = player_rect.height * 0.2
    shadow_surf = pygame.Surface((shadow_width, shadow_height), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_surf, (0, 0, 0, 100), (0, 0, shadow_width, shadow_height))
    rotated_shadow = pygame.transform.rotate(shadow_surf, 20)
    shadow_x = player_rect.centerx - rotated_shadow.get_width() // 4.8 - camera_x
    shadow_y = player_rect.bottom - rotated_shadow.get_height() // 0.75 - camera_y
    surface.blit(rotated_shadow, (shadow_x, shadow_y))

def get_player_collision_box(player_rect):
    box_width = player_rect.width * 0.3
    box_height = 35
    box_x = player_rect.centerx - box_width / 2
    box_y = player_rect.bottom - box_height - 30
    return pygame.Rect(box_x, box_y, box_width, box_height)

# Main cycle
def run_village(screen, entry_position=None):
    global last_exit_position
    clock = pygame.time.Clock()
    WIDTH, HEIGHT = screen.get_size()
    MAP_W, MAP_H = 2048, 1536

    # !!! initialization debug tool
    debug = ts_debug.DebugTool()

    # Background & buildings
    bg = pygame.image.load(get_path("maps", "village", "assets", "bg_village.png")).convert()
    bg = pygame.transform.scale(bg, (MAP_W, MAP_H))
    building_layer = pygame.image.load(get_path("maps", "village", "assets", "village_buildings.png")).convert_alpha()
    building_layer = pygame.transform.scale(building_layer, (MAP_W, MAP_H))

    # Collision & trigger
    collision_objects, trigger_objects = load_tiled_collision(get_path("maps", "village", "assets", "village_map.tmx"))

    # Player resources
    standing = pygame.image.load("Images\standing.png").convert_alpha()
    moving = pygame.image.load("Images\moving.png").convert_alpha()
    FRAME_W, FRAME_H, SCALE = 32, 32, 4

    def get_frames(sheet, frame_w, frame_h):
        frames = []
        frame_count = sheet.get_width() // frame_w
        for i in range(frame_count):
            rect = pygame.Rect(i * frame_w, 0, frame_w, frame_h)
            frame = sheet.subsurface(rect)
            frame = pygame.transform.scale(frame, (frame_w * SCALE, frame_h * SCALE))
            frames.append(frame)
        return frames

    idle_frames = get_frames(standing, FRAME_W, FRAME_H)
    move_frames = get_frames(moving, FRAME_W, FRAME_H)

    # !!! Player initial position
    start_pos = entry_position or last_exit_position or (1200, 1000)
    last_exit_position = None
    player_rect = pygame.Rect(start_pos[0], start_pos[1], FRAME_W*SCALE, FRAME_H*SCALE)

    facing_right, frame_index, frame_timer = False, 0, 0
    frame_speed, speed = 0.12, 4
    camera_x, camera_y = 0, 0
    camera_smoothness = 0.1

    running = True
    while running:
        dt = clock.tick(60)/1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                elif event.key == pygame.K_F1:
                    debug.toggle()

        keys = pygame.key.get_pressed()

        # !!! Player movement
        player_rect, is_moving, facing_right = handle_player_movement(
            player_rect, keys, speed,
            check_collision_with_objects,
            get_player_collision_box,
            collision_objects,
            facing_right
        )

        # !!! Animation
        current_frame, frame_index, frame_timer = update_animation(
            idle_frames, move_frames,
            is_moving,
            frame_index, frame_timer, dt,
            frame_speed, FRAME_W, FRAME_H, SCALE, facing_right
        )

        # !!! Camera
        camera_x, camera_y = update_camera(
            player_rect, camera_x, camera_y,
            WIDTH, HEIGHT, MAP_W, MAP_H, camera_smoothness
        )

        # draw
        screen.blit(bg, (-camera_x, -camera_y))
        draw_shadow(screen, player_rect, camera_x, camera_y)
        screen.blit(current_frame, (player_rect.x - camera_x, player_rect.y - camera_y))
        screen.blit(building_layer, (-camera_x, -camera_y))

        # !!! Debug info
        debug.draw(
            screen,
            player_rect,
            player_hitbox=get_player_collision_box(player_rect),
            collision_objects=collision_objects,
            triggers=trigger_objects,
            npcs=None,
            camera_x=camera_x,
            camera_y=camera_y
        )

        # !!! player trigger detection
        player_box = get_player_collision_box(player_rect)


        # !!! mushroom house entrance
        for obj in trigger_objects:
            if obj.get("name","").lower() == "mushroomhouse door":
                collision = False
                if obj["type"] == "rect":
                    collision = player_box.colliderect(obj["rect"])
                elif obj["type"] == "polygon":
                    collision = check_rect_polygon_collision(player_box, obj["points"])
                
                if collision:
                    hint_text = pygame.font.SysFont(None,24).render("Press E to enter Mushroom House", True, (255,255,255))
                    screen.blit(hint_text, (WIDTH//2 - 160, HEIGHT - 60))
                    
                    if keys[pygame.K_e]:
                        from mushroom_house.mushroom_house import run_mushroom_house
                        current_pos = (player_rect.centerx, player_rect.centery)
                        print(f"Entering Mushroom House，last position is: {current_pos}")
                        run_mushroom_house(screen, entry_position=(450, 535), last_exit_position=current_pos)

        pygame.display.flip()
