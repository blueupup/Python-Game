import pygame
import random

def draw_text(surface, text, font, color, rect, center=True):
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect()
    if center:
        text_rect.center = rect.center
    else:
        text_rect.topleft = rect.topleft
    surface.blit(text_surf, text_rect)


class LevelUpUI:
    def __init__(self, player, all_sprites_group, canvas_width, canvas_height):
        self.player = player
        self.all_sprites = all_sprites_group # For the orbital upgrade
        
        self.current_upgrades = []
        
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        
        btn_w, btn_h = 400, 70
        btn_x = (self.canvas_width - btn_w) // 2
        btn_y_start = self.canvas_height // 2 - 100
        btn_padding = 20
        
        self.upgrade_btn_rects = []
        for i in range(3):
            rect = pygame.Rect(
                btn_x, 
                btn_y_start + i * (btn_h + btn_padding), 
                btn_w, 
                btn_h
            )
            self.upgrade_btn_rects.append(rect)
            
        # --- 4. Fonts ---
        self.title_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.desc_font = pygame.font.SysFont("Arial", 22)

    def _get_upgrade_options(self):
        all_options = [
            {"text": "+20 Max Health", "stat": "base_health", "value": 20},
            {"text": "+5 Base Attack", "stat": "base_attack", "value": 5},
            {"text": "+10 Move Speed", "stat": "speed", "value": 10},
            {"text": "Heal 30% HP", "stat": "heal_percent", "value": 0.3},
            {"text": "+1 Orbital", "stat": "add_orbital", "value": 1},
            # {"text": "+2 Defense", "stat": "defense", "value": 2}, 
        ]
        random.shuffle(all_options)
        self.current_upgrades = all_options[:3]
        print(f"[UI] Generated Upgrades: {self.current_upgrades}")

    def _apply_upgrade(self, upgrade):
        """
        Internal method to apply a chosen upgrade.
        """
        stat = upgrade['stat']
        value = upgrade['value']
        
        print(f"[UPGRADE] Applying: {stat} + {value}")
        
        if stat == "base_health":
            self.player.stats.base_health += value
            self.player.stats.heal(value)
        elif stat == "base_attack":
            self.player.stats.base_attack += value
        elif stat == "speed":
            self.player.speed += value
        elif stat == "heal_percent":
            self.player.stats.heal(self.player.stats.max_health * value)
        elif stat == "add_orbital":
            if self.player.active_weapon:
                self.player.active_weapon.count += value
                self.player.equip_weapon(self.player.active_weapon)
                self.all_sprites.add(self.player.orbitals)

    def activate(self):
        self._get_upgrade_options()

    def handle_event(self, event, zoom_level):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Convert SCREEN mouse pos to CANVAS mouse pos
            mouse_pos = pygame.mouse.get_pos()
            canvas_mouse_x = mouse_pos[0] / zoom_level
            canvas_mouse_y = mouse_pos[1] / zoom_level
            canvas_mouse_pos = (canvas_mouse_x, canvas_mouse_y)
            
            # Check collision with each button
            for i, rect in enumerate(self.upgrade_btn_rects):
                if rect.collidepoint(canvas_mouse_pos):
                    self._apply_upgrade(self.current_upgrades[i])
                    return 'running' # Signal to resume the game
                    
        return None # No state change

    def draw(self, game_canvas):
        overlay = pygame.Surface(game_canvas.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180)) # 180 = ~70% transparent
        game_canvas.blit(overlay, (0, 0))
        
        title_rect = pygame.Rect(0, 0, self.canvas_width, 100)
        title_rect.center = (self.canvas_width // 2, self.canvas_height // 4)
        draw_text(game_canvas, "LEVEL UP!", self.title_font, (255, 255, 0), title_rect)
        
        for i, rect in enumerate(self.upgrade_btn_rects):
            pygame.draw.rect(game_canvas, (80, 80, 80), rect, border_radius=10)
            pygame.draw.rect(game_canvas, (200, 200, 200), rect, 2, border_radius=10)
            
            if self.current_upgrades:
                draw_text(game_canvas, self.current_upgrades[i]['text'], self.desc_font, (255, 255, 255), rect)

class GameOverUI:
    def __init__(self, canvas_width, canvas_height):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        
        self.title_font = pygame.font.SysFont("Arial", 64, bold=True)
        self.stat_font = pygame.font.SysFont("Arial", 32)
        self.btn_font = pygame.font.SysFont("Arial", 28)
        self.score_font = pygame.font.SysFont("Arial", 40, bold=True)
        
        self.final_time_str = ""
        self.final_kills_str = ""
        self.final_score_str = ""
        
        self.final_score = 0
        self.final_time = 0
        self.kill_count = 0

        btn_w, btn_h = 250, 60
        btn_y = self.canvas_height * 0.65
        
        # Center the single button
        self.continue_btn_rect = pygame.Rect(0, 0, btn_w, btn_h)
        self.continue_btn_rect.center = (self.canvas_width // 2, btn_y)

    def activate(self, final_score, final_time, kill_count):
        minutes = int(final_time) // 60
        seconds = int(final_time) % 60
        self.final_time_str = f"Time Survived: {minutes:02}:{seconds:02}"

        self.final_kills_str = f"Enemies Slain: {kill_count}"
        self.final_score_str = f"Final Score: {final_score}"

        self.final_score = final_score
        self.final_time = final_time
        self.kill_count = kill_count

    def handle_event(self, event, zoom_level):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            canvas_mouse_x = mouse_pos[0] / zoom_level
            canvas_mouse_y = mouse_pos[1] / zoom_level
            canvas_mouse_pos = (canvas_mouse_x, canvas_mouse_y)
            
            if self.continue_btn_rect.collidepoint(canvas_mouse_pos):
                print("[Game] Returning to Hub (Restarting)...")
                return 'restart' # This triggers the 'hub' reset
                    
        return None # No state change

    def draw(self, game_canvas):
        #Darken the screen
        overlay = pygame.Surface(game_canvas.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        game_canvas.blit(overlay, (0, 0))
        
        #Draw "GAME OVER"
        title_rect = pygame.Rect(0, 0, self.canvas_width, 100)
        title_rect.center = (self.canvas_width // 2, self.canvas_height * 0.25)
        draw_text(game_canvas, "GAME OVER", self.title_font, (220, 0, 0), title_rect)
        
        time_rect = pygame.Rect(0, 0, self.canvas_width, 50)
        time_rect.center = (self.canvas_width // 2, self.canvas_height * 0.40)
        draw_text(game_canvas, self.final_time_str, self.stat_font, (255, 255, 255), time_rect)
        
        kills_rect = pygame.Rect(0, 0, self.canvas_width, 50)
        kills_rect.center = (self.canvas_width // 2, self.canvas_height * 0.45)
        draw_text(game_canvas, self.final_kills_str, self.stat_font, (255, 255, 255), kills_rect)
        
        score_rect = pygame.Rect(0, 0, self.canvas_width, 60)
        score_rect.center = (self.canvas_width // 2, self.canvas_height * 0.52)
        draw_text(game_canvas, self.final_score_str, self.score_font, (255, 255, 100), score_rect)
        
        #Draw "Continue" Button
        pygame.draw.rect(game_canvas, (80, 80, 80), self.continue_btn_rect, border_radius=10)
        pygame.draw.rect(game_canvas, (200, 200, 200), self.continue_btn_rect, 2, border_radius=10)
        draw_text(game_canvas, "Continue", self.btn_font, (255, 255, 255), self.continue_btn_rect)