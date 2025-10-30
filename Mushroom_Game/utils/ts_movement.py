import pygame

# Player movement handling with collision detection
def handle_player_movement(player_rect, keys, speed,
                           check_collision_with_objects,
                           get_player_collision_box,
                           collision_objects,
                           facing_right):

# Determine movement direction
    move_x = (1 if keys[pygame.K_d] else 0) - (1 if keys[pygame.K_a] else 0)
    move_y = (1 if keys[pygame.K_s] else 0) - (1 if keys[pygame.K_w] else 0)

    move_vector = pygame.Vector2(move_x, move_y)
    is_moving = move_vector.length_squared() > 0

    if is_moving:
        move_vector = move_vector.normalize()

        # Detect X-axies (Foot)
        collision_box = get_player_collision_box(player_rect)
        new_box = collision_box.move(move_vector.x * speed, 0)
        if not check_collision_with_objects(new_box, collision_objects):
            player_rect.x += move_vector.x * speed

        # Detect Y-axies (chest)
        collision_box = get_player_collision_box(player_rect)
        new_box = collision_box.move(0, move_vector.y * speed)
        if not check_collision_with_objects(new_box, collision_objects):
            player_rect.y += move_vector.y * speed

        # Only update facing when actually moving
        if move_vector.x > 0:
            facing_right = True
        elif move_vector.x < 0:
            facing_right = False

    return player_rect, is_moving, facing_right

# Animation update function
def update_animation(idle_frames, move_frames, is_moving,
                     frame_index, frame_timer, dt, frame_speed, FRAME_W, FRAME_H, SCALE, facing_right):
    frame_timer += dt
    if frame_timer >= frame_speed:
        frame_timer = 0
        frame_index += 1

    frames = move_frames if is_moving else idle_frames

    if len(frames) > 0:
        frame_index %= len(frames)
        current_frame = frames[frame_index]
    else:
        current_frame = pygame.Surface((FRAME_W * SCALE, FRAME_H * SCALE), pygame.SRCALPHA)

    # Flip according to orientation
    if not facing_right:
        current_frame = pygame.transform.flip(current_frame, True, False)

    return current_frame, frame_index, frame_timer

# Camera update function and boundary restrictions
def update_camera(player_rect, camera_x, camera_y, WIDTH, HEIGHT, MAP_W, MAP_H, camera_smoothness):
    camera_target_x = player_rect.centerx - WIDTH // 2
    camera_target_y = player_rect.centery - HEIGHT // 2
    camera_target_x = max(0, min(camera_target_x, MAP_W - WIDTH))
    camera_target_y = max(0, min(camera_target_y, MAP_H - HEIGHT))
    camera_x += (camera_target_x - camera_x) * camera_smoothness
    camera_y += (camera_target_y - camera_y) * camera_smoothness
    return camera_x, camera_y
