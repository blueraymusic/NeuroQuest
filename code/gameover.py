import pygame
import sys
import random
import subprocess
import math

# Constants
WIDTH, HEIGHT = 1280, 720
FPS = 60

# Colors
SKY_COLOR = (25, 25, 112)  # Dark midnight blue
GROUND_COLOR = (30, 30, 30)  # Dark gray
TEXT_COLOR = (255, 255, 255)  # White
GLOW_COLOR = (0, 255, 255)  # Cyan glow
BUTTON_COLOR = (50, 50, 200)  # Blue
BUTTON_HOVER_COLOR = (100, 100, 255)  # Light blue
PARTICLE_COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]  # Random particle colors


class GameOver:
    def __init__(self, player):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Game Over")
        self.clock = pygame.time.Clock()
        self.player = player

        # Fonts
        self.font_large = pygame.font.Font(None, 120)
        self.font_medium = pygame.font.Font(None, 60)
        self.font_small = pygame.font.Font(None, 40)

        # Particles
        self.particles = []
        for _ in range(300):  # Initial particles
            self.particles.append(self.create_particle())

        # Buttons
        self.buttons = [
            {"text": "Restart", "rect": pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50), "color": BUTTON_COLOR, "hover": False, "scale": 1.0},
            {"text": "Quit", "rect": pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 120, 200, 50), "color": BUTTON_COLOR, "hover": False, "scale": 1.0}
        ]

        # Sound Effects (placeholders)
        pygame.mixer.init()
        self.hover_sound = pygame.mixer.Sound("../audio/hit.wav")  
        self.click_sound = pygame.mixer.Sound("../audio/sword.wav")  
        self.particle_sound = pygame.mixer.Sound("../audio/main.ogg")  

        # Custom Cursor
        self.cursor_size = 20
        self.cursor_color = (255, 255, 255)

        # Countdown Timer
        self.countdown = 20  #
        self.countdown_active = True

        # High Score
        self.high_score = self.load_high_score()

    def create_particle(self):
        """Create a single particle with random properties."""
        return {
            "pos": [random.randint(0, WIDTH), random.randint(0, HEIGHT)],
            "speed": [random.uniform(-1, 1), random.uniform(-1, 1)],
            "size": random.randint(2, 4),
            "color": random.choice(PARTICLE_COLORS),
            "life": random.randint(50, 100)
        }

    def draw_particles(self):
        """Draw and update particles."""
        mouse_pos = pygame.mouse.get_pos()
        for particle in self.particles:
            # Attract particles to the mouse
            dx = mouse_pos[0] - particle["pos"][0]
            dy = mouse_pos[1] - particle["pos"][1]
            dist = math.hypot(dx, dy)
            if dist < 100:  # Attraction radius
                force = 0.1 / dist
                particle["speed"][0] += dx * force
                particle["speed"][1] += dy * force

            # Update particle position
            particle["pos"][0] += particle["speed"][0]
            particle["pos"][1] += particle["speed"][1]

            # Bounce off edges
            if particle["pos"][0] < 0 or particle["pos"][0] > WIDTH:
                particle["speed"][0] *= -1
            if particle["pos"][1] < 0 or particle["pos"][1] > HEIGHT:
                particle["speed"][1] *= -1

            # Draw particle
            pygame.draw.circle(self.display_surface, particle["color"], (int(particle["pos"][0]), int(particle["pos"][1])), particle["size"])

    def draw_glowing_text(self, text, font, color, glow_color, position):
        """Draw text with a glowing effect."""
        text_surface = font.render(text, True, color)
        glow_surface = font.render(text, True, glow_color)
        for offset in range(-5, 6, 2):  # Create a glow effect
            self.display_surface.blit(glow_surface, (position[0] + offset, position[1]))
            self.display_surface.blit(glow_surface, (position[0], position[1] + offset))
        self.display_surface.blit(text_surface, position)

    def draw_buttons(self):
        """Draw interactive buttons with hover and click effects."""
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            if button["rect"].collidepoint(mouse_pos):
                if not button["hover"]:  # Play hover sound once
                    self.hover_sound.play()
                button["hover"] = True
                button["color"] = BUTTON_HOVER_COLOR
                button["scale"] = min(button["scale"] + 0.1, 1.2)  # Scale up
            else:
                button["hover"] = False
                button["color"] = BUTTON_COLOR
                button["scale"] = max(button["scale"] - 0.1, 1.0)  # Scale down

            # Draw button
            scaled_rect = button["rect"].copy()
            scaled_rect.width = int(button["rect"].width * button["scale"])
            scaled_rect.height = int(button["rect"].height * button["scale"])
            scaled_rect.center = button["rect"].center
            pygame.draw.rect(self.display_surface, button["color"], scaled_rect, border_radius=10)
            text_surface = self.font_medium.render(button["text"], True, TEXT_COLOR)
            text_rect = text_surface.get_rect(center=scaled_rect.center)
            self.display_surface.blit(text_surface, text_rect)

    def handle_events(self):
        """Handle user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    for button in self.buttons:
                        if button["rect"].collidepoint(mouse_pos):
                            self.click_sound.play()
                            if button["text"] == "Restart":
                                self.restart_game()
                            elif button["text"] == "Quit":
                                pygame.quit()
                                sys.exit()

    def restart_game(self):
        """Restart the game."""
        """
        subprocess.Popen([sys.executable, "main.py"])
        pygame.quit()
        sys.exit()
        """
        from main import Game
        game = Game()
        game.run()


    def load_high_score(self):
        """Load the high score from a file."""
        try:
            with open("high_score.txt", "r") as file:
                return int(file.read())
        except FileNotFoundError:
            return 0

    def save_high_score(self):
        """Save the high score to a file."""
        with open("high_score.txt", "w") as file:
            file.write(str(self.player.score))

    def run(self):
        """Main game loop."""
        while True:
            self.display_surface.fill(SKY_COLOR)
            self.draw_particles()
            self.draw_glowing_text("GAME OVER", self.font_large, TEXT_COLOR, GLOW_COLOR, (WIDTH // 2 - 250, HEIGHT // 4))
            self.draw_buttons()
            self.handle_events()

            # Draw high score
            high_score_text = self.font_small.render(f"Kills Score: {self.high_score}", True, TEXT_COLOR)
            self.display_surface.blit(high_score_text, (WIDTH // 2 - 100, HEIGHT // 2 - 100))

            #resetting the kill count
            with open("high_score.txt", "w") as file:
               file.write('0')
               

            # Countdown timer
            if self.countdown_active:
                countdown_text = self.font_small.render(f"Restarting in {round(self.countdown)}...", True, TEXT_COLOR)
                self.display_surface.blit(countdown_text, (WIDTH // 2 - 100, HEIGHT - 100))
                self.countdown -= 1 / FPS
                if self.countdown <= 0:
                    self.restart_game()

            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    class Player:
        def __init__(self):
            self.score = 1000  # Placeholder score

    player = Player()
    game_over_screen = GameOver(player)
    game_over_screen.run()