import pygame
import google.generativeai as genai
import os

class ChatBox:
    def __init__(self, x, y, width, height, font_size=18):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.Font(None, font_size)
        self.message = None  # Store only the latest message
        self.text_input = ""
        self.is_typing = False  
        self.input_rect = pygame.Rect(self.rect.left + 5, self.rect.bottom - 30, self.rect.width - 10, 25)
        self.placeholder_text = "Enter Message"

        # Colors
        self.bg_color = (240, 230, 200)
        self.border_color = (180, 120, 50)
        self.text_color = (50, 50, 50)
        self.placeholder_color = (150, 150, 150)
        self.question_color = (34, 139, 34)
        self.answer_color = (102, 205, 170)

        # Small Box for Label
        self.small_box_rect = pygame.Rect(self.rect.left + 5, self.rect.top + 5, 150, 30) 
        self.small_box_color = (135, 206, 235) 
        self.small_box_border_color = (0, 0, 0) 

        # Game Stats
        self.player_stats = {"kills": 0, "level": 1, "xp": 0}

        # Configure Gemini API
        API_KEY = "API_gemini"  # Use environment variable for security
        if not API_KEY:
            raise ValueError("API Key not found! Set GEMINI_API_KEY as an environment variable.")
        
        genai.configure(api_key=API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def set_message(self, question, answer):
        """Store only the latest question and answer."""
        self.message = (question, answer)

    def handle_input(self, event):
        """Handle user input."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.text_input.strip():
                    question = self.text_input.strip()
                    answer = self.get_response(question)
                    self.set_message(question, answer)  # Store only the latest message
                    self.text_input = ""
            elif event.key == pygame.K_BACKSPACE:
                self.text_input = self.text_input[:-1]
            else:
                if len(self.text_input) < 100:  
                    self.text_input += event.unicode  

    def get_response(self, prompt):
        """Chat with Gemini and include game stats."""
        MAP_IMAGE_PATH = "assets/images/maps/map2.png"

        game_context = f"""
        You are the Questmaster in an RPG. 
        - The player has killed {self.player_stats['kills']} enemies.
        - The player is at level {self.player_stats['level']} with {self.player_stats['xp']} XP.
        - Provide quest guidance and game hints.
        - Keep responses short and clear.
        - The map is available here: {MAP_IMAGE_PATH}
        """

        full_prompt = game_context + f"\nPlayer: {prompt}"
        response = self.model.generate_content([full_prompt])

        return response.text.strip() if response.text else "No response"

    def draw(self, surface):
        """Draw the chat box and messages."""
        pygame.draw.rect(surface, self.bg_color, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, 2)

        y_offset = 20
        if self.message:
            question, answer = self.message
            question_surface = self.font.render(f"Q: {question}", True, self.question_color)
            surface.blit(question_surface, (self.rect.x + 10, self.rect.y + y_offset))
            y_offset += 20

            answer_surface = self.font.render(f"A: {answer}", True, self.answer_color)
            surface.blit(answer_surface, (self.rect.x + 10, self.rect.y + y_offset))
            y_offset += 25

        # Input Box
        pygame.draw.rect(surface, (255, 255, 255), self.input_rect, 0)  # White input box
        pygame.draw.rect(surface, self.border_color, self.input_rect, 2)  # Border

        # Show placeholder if input is empty
        if not self.text_input:
            placeholder_surface = self.font.render(self.placeholder_text, True, self.placeholder_color)
            surface.blit(placeholder_surface, (self.input_rect.x + 5, self.input_rect.y + 5))
        else:
            input_surface = self.font.render(self.text_input, True, self.text_color)
            surface.blit(input_surface, (self.input_rect.x + 5, self.input_rect.y + 5))

        # Small Box (GemChat)
        pygame.draw.rect(surface, self.small_box_color, self.small_box_rect)
        pygame.draw.rect(surface, self.small_box_border_color, self.small_box_rect, 2)
        label_text = self.font.render("GemChat", True, (255, 255, 255))
        surface.blit(label_text, (self.small_box_rect.x + 5, self.small_box_rect.y + 5))
