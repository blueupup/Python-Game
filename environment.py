import pygame



class Environment:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("2D Environment")

    def draw(self):
        self.screen.fill((0, 0, 0)) 
        pygame.display.flip()

    def update(self):
        pass

    def run(self):
        running = True
        clock = pygame.time.Clock()
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            self.update()
            self.draw()
            clock.tick(60)  # Limit to 60 frames per second
        
        pygame.quit()

if __name__ == "__main__":
    pygame.init()
    env = Environment(800, 600)
    env.run()