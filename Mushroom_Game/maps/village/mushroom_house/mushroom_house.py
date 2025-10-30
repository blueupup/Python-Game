import pygame
import sys
import pytmx
import os

from utils.ts_movement import handle_player_movement, update_animation, update_camera
from utils import ts_debug  # !!! debug tool

# resouces path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
def get_path(*paths):
    return os.path.join(BASE_DIR, *paths)

# Loading Tiled collision / trigger
def load_tiled_collision_local(tmx_file, collision_layer_name='collision', trigger_layer_name='triggers'):
    try:
        tmx_data = pytmx.load_pygame(tmx_file)
    except Exception as e:
        print("Failed to load tmx:", e)
        return [], []

    collision_objects, trigger_objects = [], []

    for layer in tmx_data.visible_layers:
        if not isinstance(layer, pytmx.TiledObjectGroup):
            continue
        layer_name = layer.name.lower()
        if layer_name not in (collision_layer_name.lower(), trigger_layer_name.lower()):
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
            else:
                trigger_objects.append(obj_data)

    return collision_objects, trigger_objects

# Drawing Shadow
def draw_shadow_round(surface, player_rect, camera_x, camera_y):
    shadow_width = player_rect.width * 0.5
    shadow_height = player_rect.height * 0.15
    shadow_surf = pygame.Surface((shadow_width, shadow_height), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_surf, (0, 0, 0, 120), (0, 0, shadow_width, shadow_height))
    shadow_x = player_rect.centerx - shadow_width / 2 - camera_x
    shadow_y = player_rect.bottom - shadow_height / 0.47 - camera_y
    surface.blit(shadow_surf, (shadow_x, shadow_y))

# Player frames extraction
def get_frames(sheet, frame_w, frame_h, SCALE):
    frames = []
    frame_count = sheet.get_width() // frame_w
    for i in range(frame_count):
        rect = pygame.Rect(i * frame_w, 0, frame_w, frame_h)
        frame = sheet.subsurface(rect).copy()
        frame = pygame.transform.scale(frame, (frame_w * SCALE, frame_h * SCALE))
        frames.append(frame)
    return frames

# Player hitbox (foot area)
def get_player_collision_box(player_rect):
    box_width = player_rect.width * 0.3
    box_height = 35
    box_x = player_rect.centerx - box_width / 2
    box_y = player_rect.bottom - box_height - 30
    return pygame.Rect(box_x, box_y, box_width, box_height)

# Polygon and rectangle collision
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
    for p in polygon:
        if rect.collidepoint(p):
            return True
    return False

# Inside room main cycle
def run_mushroom_house(screen, entry_position, last_exit_position=None):
    "Mushroom house"
    clock = pygame.time.Clock()
    WIDTH, HEIGHT = screen.get_size()
    MAP_W, MAP_H = 1024, 768

    # defaul debug tool
    debug = ts_debug.DebugTool()

    # background and items in room
    bg = pygame.image.load(get_path("maps", "village", "mushroom_house", "assets", "mushroom_house.png")).convert()
    bg = pygame.transform.scale(bg, (MAP_W, MAP_H))
    item_layer = pygame.image.load(get_path("maps", "village", "mushroom_house", "assets", "mushroom_house_item.png")).convert_alpha()
    item_layer = pygame.transform.scale(item_layer, (MAP_W, MAP_H))

    # Tiled collision & trigger
    tmx_path = get_path("maps", "village", "mushroom_house", "assets", "mushroom_house.tmx")
    collision_objects, trigger_objects = load_tiled_collision_local(tmx_path)

    # Player resources
    FRAME_W, FRAME_H, SCALE = 32, 32, 4
    standing = pygame.image.load(get_path("assets", "standing.png")).convert_alpha()
    moving = pygame.image.load(get_path("assets", "moving.png")).convert_alpha()
    idle_frames = get_frames(standing, FRAME_W, FRAME_H, SCALE)
    move_frames = get_frames(moving, FRAME_W, FRAME_H, SCALE)

    # Player initial position
    player_rect = pygame.Rect(entry_position[0], entry_position[1], FRAME_W*SCALE, FRAME_H*SCALE)
    facing_right = False
    frame_index, frame_timer = 0, 0
    frame_speed, speed = 0.12, 4
    camera_x, camera_y = 0.0, 0.0
    camera_smoothness = 0.1

    running = True
    while running:
        dt = clock.tick(60)/1000.0
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

        # Player movement
        player_rect, is_moving, facing_right = handle_player_movement(
            player_rect, keys, speed,
            lambda rect, objs: any(
                rect.colliderect(o["rect"]) if o["type"]=="rect" else check_rect_polygon_collision(rect, o["points"])
                for o in objs
            ),
            get_player_collision_box,
            collision_objects,
            facing_right
        )

        # Animation
        current_frame, frame_index, frame_timer = update_animation(
            idle_frames, move_frames,
            is_moving, frame_index, frame_timer, dt,
            frame_speed, FRAME_W, FRAME_H, SCALE, facing_right
        )

        # Camera
        camera_x, camera_y = update_camera(
            player_rect, camera_x, camera_y, WIDTH, HEIGHT, MAP_W, MAP_H, camera_smoothness
        )

        # Drawing
        screen.blit(bg, (-camera_x, -camera_y))
        draw_shadow_round(screen, player_rect, camera_x, camera_y)
        screen.blit(current_frame, (player_rect.x - camera_x, player_rect.y - camera_y))
        screen.blit(item_layer, (-camera_x, -camera_y))

        # Door trigger (detect player box & door area)
        player_box = get_player_collision_box(player_rect)
        for obj in trigger_objects:
            if obj.get("name", "").lower() == "door":
                if obj["type"] == "rect":
                    collision = player_box.colliderect(obj["rect"])
                else:
                    collision = check_rect_polygon_collision(player_box, obj["points"])

                if collision:
                    from maps.village.main_village import run_village
                    run_village(screen, entry_position=last_exit_position)
                    return

        # Debug drawing
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

        pygame.display.flip()
