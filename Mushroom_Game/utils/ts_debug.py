# utils/ts_debug.py
import pygame

class DebugTool:
    def __init__(self):
        self.enabled = False
        self.font = pygame.font.SysFont(None, 24)

    def toggle(self):
        self.enabled = not self.enabled

    def draw(self, screen, player_rect, player_hitbox=None, collision_objects=None, triggers=None, npcs=None, camera_x=0, camera_y=0):
        if not self.enabled:
            return

        # Player position
        text = self.font.render(f"Player: ({int(player_rect.x)}, {int(player_rect.y)})", True, (255, 255, 0))
        screen.blit(text, (10, 10))

        # Player hitbox
        if player_hitbox:
            pygame.draw.rect(screen, (255, 255, 0),
                             (player_hitbox.x - camera_x, player_hitbox.y - camera_y, player_hitbox.width, player_hitbox.height), 2)

        # map collision objects
        if collision_objects:
            for obj in collision_objects:
                if obj["type"] == "rect":
                    pygame.draw.rect(screen, (255, 0, 0),
                                     (obj["rect"].x - camera_x, obj["rect"].y - camera_y, obj["rect"].w, obj["rect"].h), 2)
                else:
                    pts = [(x - camera_x, y - camera_y) for x, y in obj["points"]]
                    pygame.draw.polygon(screen, (255, 0, 0), pts, 2)

        # Trigger areas
        if triggers:
            for obj in triggers:
                if obj["type"] == "rect":
                    pygame.draw.rect(screen, (0, 255, 255),
                                     (obj["rect"].x - camera_x, obj["rect"].y - camera_y, obj["rect"].w, obj["rect"].h), 2)
                else:
                    pts = [(x - camera_x, y - camera_y) for x, y in obj["points"]]
                    pygame.draw.polygon(screen, (0, 255, 255), pts, 2)

        # NPC collision boxes(if any)
        if npcs:
            for npc in npcs:
                pygame.draw.rect(screen, (255, 255, 0),
                                 (npc.rect.x - camera_x, npc.rect.y - camera_y, npc.rect.width, npc.rect.height), 2)
