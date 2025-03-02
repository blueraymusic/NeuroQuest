import pygame
import sys
import subprocess
import random


WIDTH, HEIGHT = 1280, 720

class GameOver:
    def __init__(self, player):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Game Over")
        self.font_large = pygame.font.Font(None, 120)
        self.font_small = pygame.font.Font(None, 50)
        self.player = player

        self.sky_color = (25, 25, 112)  # Dark midnight blue
        self.ground_color = (30, 30, 30)  # Dark gray ground
        self.text_color = (255, 255, 255)  # White text color

        # Particle effects
        self.particles = []

        # Animation Variables
        self.countdown = 3
        self.clock = pygame.time.Clock()
        self.bounce_offset = 0  # Bounce effect for text

        # Sound Effects
        pygame.mixer.init()
        self.game_over_sound = pygame.mixer.Sound("../audio/main.ogg")  
        self.game_over_sound.play()

    def draw_background(self):
        """Creates a night sky with stars and a floating atmosphere."""
        # Fill the background with a dark blue
        self.display_surface.fill(self.sky_color)

        # Draw stars (simple white dots scattered)
        for _ in range(100):
            star_x = random.randint(0, WIDTH)
            star_y = random.randint(0, HEIGHT)
            pygame.draw.circle(self.display_surface, (255, 255, 255), (star_x, star_y), random.randint(1, 3))


        for particle in self.particles:
            pygame.draw.circle(self.display_surface, (255, 255, 255), particle['pos'], random.randint(1, 4))
            particle['pos'][1] += particle['speed']  # Gravity-like effect

            if particle['pos'][1] > HEIGHT:
                self.particles.remove(particle)

        if random.random() < 0.1:  # Random chance to spawn a new particle
            self.particles.append({'pos': [random.randint(0, WIDTH), 0], 'speed': random.randint(1, 3)})

    def display_gameover(self):
        """Displays Game Over with animated effects and countdown."""
        while self.countdown >= 0:
            self.display_surface.fill((0, 0, 0))  # Reset screen
            self.draw_background()  # Draw animated background

            self.bounce_offset = abs(10 - (pygame.time.get_ticks() // 100) % 20)  # Bounce effect
            text_surf = self.font_large.render("GAME OVER", True, self.text_color)
            glow_surf = self.font_large.render("GAME OVER", True, (0, 255, 255))  
            text_rect = text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 3 - self.bounce_offset))
            
            # Apply glowing effect
            self.display_surface.blit(glow_surf, (text_rect.x - 5, text_rect.y - 5))  # Glow behind
            self.display_surface.blit(text_surf, text_rect)  # Main text


            if self.countdown > 0:
                countdown_surf = self.font_large.render(f"{self.countdown}", True, (255, 255, 0))
                countdown_rect = countdown_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                countdown_scale = 1 + 0.1 * (pygame.time.get_ticks() // 500 % 2)  # Pulse effect
                countdown_surf = pygame.transform.scale(countdown_surf, 
                    (int(countdown_surf.get_width() * countdown_scale), 
                    int(countdown_surf.get_height() * countdown_scale)))
                self.display_surface.blit(countdown_surf, countdown_rect)

            if pygame.time.get_ticks() % 800 < 400:
                retry_surf = self.font_small.render("Press SPACE to Restart or ENTER to Quit", True, (255, 255, 255))
                retry_rect = retry_surf.get_rect(center=(WIDTH // 2, HEIGHT - 150))
                self.display_surface.blit(retry_surf, retry_rect)

            pygame.display.flip()
            self.clock.tick(60)

            pygame.time.wait(1000)
            self.countdown -= 1

        self.wait_for_input()

    def wait_for_input(self):
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.restart_game()
                        waiting = False
                    elif event.key == pygame.K_RETURN:
                        pygame.quit()
                        sys.exit()

    def restart_game(self):
        subprocess.Popen([sys.executable, "main.py"])
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    class Player:
        pass  # Placeholder

    player = Player()
    game_over_screen = GameOver(player)
    game_over_screen.display_gameover()
