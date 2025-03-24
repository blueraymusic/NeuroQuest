import pygame
import sys
from settings import *  
from level import Level
from chatbox import ChatBox
from gameover import GameOver  

class Menu:
    def __init__(self, screen):
        self.screen = screen
        # Load and scale the background image
        self.background = pygame.image.load('bg.png')
        
        bg_width, bg_height = self.background.get_size()
        aspect_ratio = bg_width / bg_height
        
        if WIDTH / HEIGTH > aspect_ratio:
            new_height = HEIGTH
            new_width = int(aspect_ratio * new_height)
        else:
            new_width = WIDTH
            new_height = int(new_width / aspect_ratio)
     
        self.background = pygame.transform.scale(self.background, (new_width, new_height))
        
        self.font = pygame.font.Font(None, 80)
        
        self.title_text = self.font.render("", True, (255, 215, 0))
        
        button_width = 250
        button_height = 80
        space_between = 20  # Space between the buttons
        
        self.play_button = pygame.Rect(WIDTH // 2 - button_width - space_between // 2, HEIGTH // 2, button_width, button_height)
        self.quit_button = pygame.Rect(WIDTH // 2 + space_between // 2, HEIGTH // 2, button_width, button_height)
    
    def draw(self):
        bg_x = (WIDTH - self.background.get_width()) // 2
        bg_y = (HEIGTH - self.background.get_height()) // 2
        self.screen.blit(self.background, (bg_x, bg_y))
        
        title_rect = self.title_text.get_rect(center=(WIDTH // 2, 150))
        self.screen.blit(self.title_text, title_rect.topleft)
        
        self._draw_button(self.play_button, "START", (30, 144, 255), (255, 255, 255), (0,19,222), scale_factor=1.1, glow_color=(0,19,222))  # Dodger Blue for START, Hover Color: Dark Turquoise, Glowing Color: Cyan
        self._draw_button(self.quit_button, "QUIT", (255, 99, 71), (255, 255, 255), (255, 69, 0), scale_factor=1.1, glow_color=(255, 99, 71))  # Tomato Red for QUIT, Hover Color: Orange Red
    
    def _draw_button(self, button_rect, text, button_color, text_color, hover_color, scale_factor=1.1, glow_color=None):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = button_rect.collidepoint(mouse_pos)
        
        if is_hovered:
            button_color = hover_color  
            current_width = int(button_rect.width * scale_factor)
            current_height = int(button_rect.height * scale_factor)
            scaled_rect = pygame.Rect(button_rect.centerx - current_width // 2, button_rect.centery - current_height // 2, current_width, current_height)
        else:
            scaled_rect = button_rect
        
        button_surface = pygame.Surface(scaled_rect.size, pygame.SRCALPHA)
        button_surface.fill((0, 0, 0, 0))  # Clear, no background fill
        
        pygame.draw.rect(button_surface, button_color, button_surface.get_rect(), border_radius=20)
        
        if glow_color:
            pygame.draw.rect(self.screen, glow_color, scaled_rect.inflate(20, 20), border_radius=25, width=5)  # Glowing effect around the button
        
        text_surface = self.font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=scaled_rect.center)
        
        self.screen.blit(button_surface, scaled_rect.topleft)
        

        self.screen.blit(text_surface, text_rect.topleft)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.play_button.collidepoint(event.pos):
                return 'play'
            if self.quit_button.collidepoint(event.pos):
                pygame.quit()
                sys.exit()
        return None

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGTH))  
        pygame.display.set_caption('NeuralQuest')
        self.clock = pygame.time.Clock()
        self.level = Level()
        self.chat_box = ChatBox(x=20, y=HEIGTH - 120, width=WIDTH - 40, height=120)
        
        main_sound = pygame.mixer.Sound('../audio/main.ogg')
        main_sound.set_volume(0.5)
        main_sound.play(loops=-1)
        
        self.menu = Menu(self.screen)
        self.in_menu = True
        self.game_over_screen = None  
    
    def run(self):
        while True:
            self.screen.fill(WATER_COLOR)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if self.in_menu:
                    action = self.menu.handle_event(event)
                    if action == 'play':
                        self.in_menu = False
                else:
                    self.chat_box.handle_input(event)
            
            if self.in_menu:
                self.menu.draw()
            elif self.level.player.health <= 0:  
                if self.game_over_screen is None:
                    self.game_over_screen = GameOver(self.level.player)  
                self.game_over_screen.run()
            else:
                self.level.run()
                self.chat_box.draw(self.screen)
            
            pygame.display.update()
            self.clock.tick(FPS)
    
if __name__ == '__main__':
    game = Game()
    game.run()
