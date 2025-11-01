class MobStats:
    def __init__(self, name, max_health, attack_power, xp_reward, defense, speed, aggro_range, attack_range, anim_speed=100):
        
        self.name = name
        
        self.max_health = max_health
        self.current_health = max_health
        self.attack_power = attack_power
        self.defense = defense
        self.speed = speed 

        self.xp_reward = xp_reward

        self.aggro_range = aggro_range     # Distance (pixels) to start chasing
        self.attack_range = attack_range   # Distance (pixels) to stop and attack
        
        # --- Animation Stats ---
        self.anim_speed = anim_speed

    def take_damage(self, amount):
        damage_taken = max(0, amount - self.defense)
        self.current_health -= damage_taken
        
        if self.current_health <= 0:
            self.current_health = 0
            return True
        return False

# --- 1. THE DATA ---
# This is where you define all your different mob types.
# We use a dictionary to store "blueprints" for the stats class.
MOB_DATA = {
    "bunny": {
        "name": "bunny",
        "max_health": 50,
        "attack_power": 5,
        "defense": 2,
        "speed": 75,         # Moves 75 pixels/sec
        "aggro_range": 300,  # Sees player from 300px away
        "attack_range": 40,  # Stops to attack at 40px
        "anim_speed": 150,    # Slower animation
        "xp_reward" : 50
    },

    "slime": {
        "name": "Slime",
        "max_health": 30,
        "attack_power": 3,
        "defense": 5,
        "speed": 50,         # Moves 50 pixels/sec
        "aggro_range": 250,
        "attack_range": 30,
        "anim_speed": 200    # Very slow animation
    },
    # --- Add more mob types here ---
    "dire_wolf": {
        "name": "Dire Wolf",
        "max_health": 70,
        "attack_power": 10,
        "defense": 3,
        "speed": 120,        # Very fast
        "aggro_range": 400,
        "attack_range": 50,
        "anim_speed": 80     # Fast animation
    }
}

# --- 2. THE FACTORY FUNCTION ---
# This is the *only* function your Enemy class should ever call.
def get_stats(mob_type):
    """
    Factory function to create a new instance of MobStats.
    - mob_type (str): The key (e.g., "goblin") to look up in MOB_DATA.
    """
    if mob_type not in MOB_DATA:
        print(f"--- FATAL (mobStats) ---")
        print(f"Unknown mob_type: {mob_type}")
        print(f"Valid types are: {list(MOB_DATA.keys())}")
        return None # This will cause the Enemy to fail safely

    # Get the dictionary of stats for this mob_type
    stats_dict = MOB_DATA[mob_type]
    
    # Create a new MobStats *instance* using the data
    # The ** unpacks the dictionary into keyword arguments
    return MobStats(**stats_dict)