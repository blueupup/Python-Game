import pygame
import random
import math

# --- Base Particle Class ---
# We use a base class so all particles share
# an update/draw structure.
class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)

    def update(self, dt):
        return True # Default: stay alive

    def draw(self, surface, camera_x, camera_y):
        pass

class HitSplat(Particle):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.size = random.randint(4, 6)
        self.color = (200, 200, 200) # Whitish
        self.vel.x = random.uniform(-0.5, 0.5) * 60
        self.vel.y = random.uniform(-1.5, -0.5) * 60
        self.life = random.uniform(0.2, 0.4) # In seconds
        self.size_decay = 8.0

    def update(self, dt):
        self.pos += self.vel * dt
        self.size -= self.size_decay * dt
        self.life -= dt
        
        # Return False when dead
        return self.size > 0 and self.life > 0

    def draw(self, surface, camera_x, camera_y):
        screen_x = int(self.pos.x - camera_x)
        screen_y = int(self.pos.y - camera_y)
        pygame.draw.circle(surface, self.color, (screen_x, screen_y), int(self.size))

class DeathBurst(Particle):
    def __init__(self, x, y, color=(200, 50, 50)):
        super().__init__(x, y)
        self.size = random.randint(3, 7)
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(2, 6) * 60
        self.color = color
        self.life = random.uniform(0.8, 1.5)
        self.size_decay = 10.0

    def update(self, dt):
        self.pos.x += math.cos(self.angle) * self.speed * dt
        self.pos.y += math.sin(self.angle) * self.speed * dt
        self.size -= self.size_decay * dt
        self.life -= dt
        
        self.speed *= 0.95 
        
        return self.size > 0 and self.life > 0

    def draw(self, surface, camera_x, camera_y):
        screen_x = int(self.pos.x - camera_x)
        screen_y = int(self.pos.y - camera_y)
        

        rect = pygame.Rect(
            screen_x - self.size // 2,
            screen_y - self.size // 2,
            self.size,
            self.size
        )
        pygame.draw.rect(surface, self.color, rect)


# This one object will control all world particles.
class ParticleManager:
    def __init__(self, hit_sound =None, levelup = None):
        # We use a set for faster removals
        self.particles = set()
        self.hit_sound = hit_sound
        self.levelup_sound = levelup

    def update(self, dt):

        dead_particles = set()
        for particle in self.particles:
            is_alive = particle.update(dt)
            if not is_alive:
                dead_particles.add(particle)
        
        # Now we remove the dead ones
        self.particles.difference_update(dead_particles)

    def draw(self, surface, camera_x, camera_y):
        for particle in self.particles:
            particle.draw(surface, camera_x, camera_y)


    def create_hit_effect(self, x, y):
        # Create a few small splats
        for _ in range(random.randint(2, 4)):
            self.particles.add(HitSplat(x, y))
        
        if hasattr(self, "hit_sound") and self.hit_sound:
            self.hit_sound.play()
    
    def create_death_explosion(self, x, y):
        # Create a big burst
        for _ in range(random.randint(15, 25)):
            self.particles.add(DeathBurst(x, y))

    def create_player_damage_effect(self, x, y):
        # Create a red burst
        red_color = (220, 0, 0)
        for _ in range(random.randint(10, 15)):
            self.particles.add(DeathBurst(x, y, color=red_color))
            
    def create_level_up_burst(self, x, y):
        print("--- [DEBUG] Creating level up burst! ---")
        colors = [
            (255, 255, 100), # Bright Yellow
            (255, 255, 255), # White
            (255, 180, 50)   # Orange
        ]
        
        # Spawn more particles
        for _ in range(random.randint(60, 90)): # Was 30-50
            color = random.choice(colors)
            self.particles.add(DeathBurst(x, y, color=color))
        if self.levelup_sound:
            self.levelup_sound.play()