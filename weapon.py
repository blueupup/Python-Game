import pygame

class Weapon:
    def __init__(self, name, image_path, scale, count, radius, rotation_speed, weapon_damage, hit_cooldown):
        self.name = name
        self.image_path = image_path
        self.scale = scale
        self.count = count
        self.radius = radius
        self.rotation_speed = rotation_speed
        self.weapon_damage = weapon_damage
        self.hit_cooldown = hit_cooldown
    
