import pygame

class MeleeWeaponSprite(pygame.sprite.Sprite):
    def __init__(self, player, weapon_blueprint):
        super().__init__()
        self.player = player
        
        # --- Animation config ---
        self.life_duration = 0.25 # How long it stays (seconds)
        self.life_timer = self.life_duration
        self.lunge_speed = 100 # How fast it moves forward
        self.start_pos = pygame.math.Vector2(self.player.rect.center)

        try:
            image = pygame.image.load(weapon_blueprint.image_path).convert_alpha()
            w, h = image.get_size()
            scale = weapon_blueprint.scale
            self.base_image = pygame.transform.scale(image, (int(w * scale), int(h * scale)))
        except Exception as e:
            print(f"--- WEAPON SPRITE ERROR: {e} ---")
            self.base_image = pygame.Surface((30, 60))
            self.base_image.fill((255, 0, 255)) # Pink error
        
        if self.player.facing_right:
            # Nudge the starting position to be in front
            nudge_x = self.player.rect.width // 2
            self.start_pos.x += nudge_x
        else:
            # Flip the image and reverse the lunge
            self.base_image = pygame.transform.flip(self.base_image, True, False)
            self.lunge_speed *= -1 
            nudge_x = -self.player.rect.width // 2
            self.start_pos.x += nudge_x

        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=self.start_pos)
        self.pos = pygame.math.Vector2(self.rect.topleft) # Use float for smooth lunge

    def update(self, dt):
        self.life_timer -= dt
        if self.life_timer <= 0:
            self.kill() # Destroy self
            return
            
        self.pos.x += self.lunge_speed * dt
        self.rect.topleft = self.pos

        self.image = self.base_image.copy()
        alpha = max(0, 255 * (self.life_timer / self.life_duration))
        self.image.set_alpha(alpha)