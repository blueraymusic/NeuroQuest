import pygame
import google.generativeai as genai
import json


class ChatBox:
    def __init__(self, x, y, width, height, font_size=18):
        self.player_stats = {
            'kills': 0,
            'level': 1,
            'xp': 0
        }

        self.habits = {
            'frequent_places': [],
            'killcount_trends': [],
            'quests_completed': []
        }

        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.Font(None, font_size)
        self.current_question = None  # Store only the latest question
        self.current_answer = None  # Store only the latest answer
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

        self.small_box_rect = pygame.Rect(self.rect.left + 5, self.rect.top + 5, 150, 30) 
        self.small_box_color = (135, 206, 235) 
        self.small_box_border_color = (0, 0, 0) 

        self.player_stats = {"kills": 0, "level": 1, "xp": 0}


        API_KEY = "API-Gemini"
        if not API_KEY:
            raise ValueError("API Key not found! Set GEMINI_API_KEY as an environment variable.")
        
        genai.configure(api_key=API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

        # Welcome message on start
        self.welcome_message = "Welcome, adventurer! I'm your assistant. Ask me anything about quests or the game. Type 'exit' to leave."
        self.instructions_message = "Welcome, adventurer! I'm your assistant. Ask me anything about quests or the game. Type 'exit' to leave. To interact, type your message below and press Enter."

        # Display the initial welcome message
        self.set_message("Welcome", self.welcome_message)
        self.set_message("Instructions", self.instructions_message)

    def set_message(self, question, answer):
        """Store only the latest question and answer."""
        self.current_question = question
        self.current_answer = answer

    def handle_input(self, event):
        """Handle user input."""
        global checking_event 
        
        checking_event = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.text_input.strip():
                    question = self.text_input.strip()
                    if question.lower() == 'exit':
                        self.text_input = ""
                        self.set_message("Exit", "Goodbye! Have a great adventure!")
                        checking_event = True
                        return
                    
                    answer = self.get_response(question)
                    self.set_message(question, answer)  # Store only the latest question and answer
                    self.text_input = ""  # Clear the input box
            elif event.key == pygame.K_BACKSPACE:
                self.text_input = self.text_input[:-1]
            else:
                if len(self.text_input) < 100:  
                    self.text_input += event.unicode  

    def get_response(self, prompt):
        """Chat with Gemini and include game stats while tracking habits."""
        MAP_IMAGE_PATH = "map2.png"

        if "village" in prompt.lower():
            self.habits['frequent_places'].append('village')
        
        if "kill" in prompt.lower():
            self.habits['killcount_trends'].append(self.player_stats['kills'])
        
        if "quest" in prompt.lower():
            self.habits['quests_completed'].append(prompt)

        self.save_habits_to_json()

        game_context = f"""
        You are the Questmaster in an RPG.
        - The player has killed {self.player_stats['kills']} enemies.
        - The player is at level {self.player_stats['level']} with {self.player_stats['xp']} XP.
        - Provide quest guidance and game hints based on the player's habits.
        - Keep responses short and clear.
        - The map is available here: {MAP_IMAGE_PATH}
        - The killcount is {self.player_stats['kills']}. You may ask quests related to the killcount.
        - Usually, when the killcount is more than 3, that means you probably already asked a quest related to increasing killings.
        - Note: The North is always to the right, and east is up.
        - Note: Never digress away from the game.
        - Example of place quests: find Rico Village and kill 4 enemies there.
        - The player has frequently visited these places: {', '.join(self.habits['frequent_places'])}.
        - The player has completed these quests: {', '.join(self.habits['quests_completed'])}.
        - Kill count trends: {self.habits['killcount_trends']}.
        """

        full_prompt = game_context + f"\nPlayer: {prompt}"
        response = self.model.generate_content([full_prompt])

        return response.text.strip() if response.text else "No response"

    def save_habits_to_json(self):
        """Save player habits to a JSON file."""
        habits_data = {
            'frequent_places': self.habits['frequent_places'],
            'killcount_trends': self.habits['killcount_trends'],
            'quests_completed': self.habits['quests_completed']
        }

        with open('player_habits.json', 'w') as json_file:
            json.dump(habits_data, json_file, indent=4)

    def draw(self, surface):
        """Draw the chat box and messages."""
        pygame.draw.rect(surface, self.bg_color, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, 2)

        y_offset = 20
        if self.current_question and self.current_answer:
            # Check for the first welcome message
            question_surface = self.font.render(f"Q: {self.current_question}", True, self.question_color)
            surface.blit(question_surface, (self.rect.x + 10, self.rect.y + y_offset))
            y_offset += 20

            answer_surface = self.font.render(f"A: {self.current_answer}", True, self.answer_color)
            surface.blit(answer_surface, (self.rect.x + 10, self.rect.y + y_offset))
            y_offset += 25

        pygame.draw.rect(surface, (255, 255, 255), self.input_rect, 0)  # White input box
        pygame.draw.rect(surface, self.border_color, self.input_rect, 2)  # Border

        if not self.text_input:
            placeholder_surface = self.font.render(self.placeholder_text, True, self.placeholder_color)
            surface.blit(placeholder_surface, (self.input_rect.x + 5, self.input_rect.y + 5))
        else:
            input_surface = self.font.render(self.text_input, True, self.text_color)
            surface.blit(input_surface, (self.input_rect.x + 5, self.input_rect.y + 5))

        pygame.draw.rect(surface, self.small_box_color, self.small_box_rect)
        pygame.draw.rect(surface, self.small_box_border_color, self.small_box_rect, 2)
        label_text = self.font.render("GemChat", True, (255, 255, 255))
        surface.blit(label_text, (self.small_box_rect.x + 5, self.small_box_rect.y + 5))
