import pygame

class Weapon:
    def __init__(self, name, image_path, scale, weapon_damage, hit_cooldown, 
                 
                 # Orbital-specific stats
                 count=0, radius=0, rotation_speed=0, 
                 
                 # Melee-specific stats
                 attack_range=0, swing_arc=0):
        
        self.name = name
        self.image_path = image_path
        self.scale = scale
        self.weapon_damage = weapon_damage
        self.hit_cooldown = hit_cooldown

        # --- Determine Type ---
        if count > 0:
            self.weapon_type = "orbital"
        else:
            self.weapon_type = "melee"

        # --- Orbital Stats ---
        self.count = count
        self.radius = radius
        self.rotation_speed = rotation_speed
        
        self.attack_range = attack_range # How far the attack reaches
        self.swing_arc = swing_arc       # Arc of the attack in degrees

# --- Orbital Weapons ---
MUSHROOM_SONG = Weapon(
    name="Mushroom Song",
    image_path=r"Images\spr_LunaNote_0.png",
    scale=1,
    weapon_damage=5,
    hit_cooldown=0.5,
    count=4,            
    radius=60,          
    rotation_speed=2.0  
)

STORM_BLADE = Weapon(
    name="Storm Blade",
    image_path=r"Images\spr_AnyaBlade2.png", 
    scale=1.5,
    weapon_damage=25,
    hit_cooldown=1.0,
    attack_range=80,    
    swing_arc=90     
)

# ORNATE_KRIS = Weapon(
#     name="Ornate Kris",
#     image_path=r"Images\image_5eb8ce.png", # Your uploaded file
#     scale=1.5,
#     weapon_damage=12,
#     hit_cooldown=0.4,   # Fast stab
#     attack_range=45,    # Short reach
#     swing_arc=30        # Narrow stab
# )
