import pygame

class Environment:
    def __init__(self, world_width, world_height, background_path):
        """
        Initializes the environment's properties and loads its assets.
        world_width and world_height now refer to the size of the *full map*.
        """
        self.world_width = world_width
        self.world_height = world_height
        self.background_asset_path = background_path
        
        # Load and scale the background surface to WORLD size
        self.load_background()

    def load_background(self):
        try:
            # Load the original image
            original_background = pygame.image.load(self.background_asset_path).convert()
            # Scale it to the full world dimensions
            self.background = pygame.transform.scale(original_background, (self.world_width, self.world_height))
            print(f"Loaded background: {self.background_asset_path} and scaled to {self.world_width}x{self.world_height}")
        except pygame.error as e:
            print(f"--- FATAL ERROR (Environment) ---")
            print(f"Unable to load background image: {self.background_asset_path}")
            print(f"Pygame error: {e}")
            print("Using a solid black fallback for world map.")
            self.background = pygame.Surface((self.world_width, self.world_height))
            self.background.fill((0, 0, 0))

    def update(self):
        pass

    def draw(self, screen_surface, camera_offset_x, camera_offset_y):
        tile_width = self.background.get_width()
        tile_height = self.background.get_height()

        screen_width = screen_surface.get_width()
        screen_height = screen_surface.get_height()

        start_x = -(camera_offset_x % tile_width)
        start_y = -(camera_offset_y % tile_height)

        current_y = start_y
        while current_y < screen_height:
            current_x = start_x
            while current_x < screen_width:
                screen_surface.blit(self.background, (current_x, current_y))
                current_x += tile_width
            current_y += tile_height