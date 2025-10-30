import pygame, sys
from maps.village import main_village

pygame.init()

WIDTH, HEIGHT = 1080, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mushroom Adventure")

font = pygame.font.Font(None, 60)
clock = pygame.time.Clock()

def draw_text(text, y, selected=False):
    color = (255, 255, 0) if selected else (255, 255, 255)
    text_surf = font.render(text, True, color)
    rect = text_surf.get_rect(center=(WIDTH//2, y))
    screen.blit(text_surf, rect)

def main_menu():
    menu_options = ["Start Game", "Exit"]
    index = 0
    running = True

    # event-driven key state (for menu we still use events)
    key_state = {}

    while running:
        # process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.KEYDOWN:
                key_state[event.key] = True
                if event.key == pygame.K_DOWN:
                    index = (index + 1) % len(menu_options)
                elif event.key == pygame.K_UP:
                    index = (index - 1) % len(menu_options)
                elif event.key == pygame.K_RETURN:
                    if index == 0:
                        # Clear event queue before switching
                        pygame.event.clear()
                        main_village.run_village(screen)   # pass same screen

                    elif index == 1:
                        pygame.quit(); sys.exit()
            elif event.type == pygame.KEYUP:
                key_state[event.key] = False

        # draw menu
        screen.fill((40, 40, 60))
        draw_text("Mushroom Adventure", 180)
        for i, text in enumerate(menu_options):
            draw_text(text, 320 + i * 80, selected=(i == index))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main_menu()
