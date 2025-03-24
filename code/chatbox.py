import pygame
import google.generativeai as genai
import json
import os
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

# Get API key
API_KEY = config.get("API", "GEMINI_API_KEY", fallback=None)

class ChatBox:
    def __init__(self, x, y, width, height, font_size=18):
        self.player_stats = {
            'kills': 0,
            'level': 1,
            'xp': 0,
            'quests_completed': 0,
            'total_damage_dealt': 0,
            'total_damage_taken': 0,
            'time_played': 0  # in seconds
        }

        self.habits = {
            'frequent_places': [],
            'killcount_trends': [],
            'quests_completed': [],
            'preferred_weapons': [],
            'play_times': []  # Track when the player is active
        }

        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.Font(None, font_size)
        self.current_question = None  # Store only the latest question
        self.current_answer = None  # Store only the latest answer
        self.text_input = ""
        self.is_typing = False  # Track whether the user is typing
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

        #API_KEY = "AIzaSyDY6ylgqJc0YZUVe7YEamBK29IKA7_wl_Q"
        if not API_KEY:
            raise ValueError("API Key not found! Set GEMINI_API_KEY as an environment variable.")
        
        genai.configure(api_key=API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

        # Welcome message on start
        self.welcome_message = "Ask me anything about quests or the game.  Press 'Shift + O' to Enbale Chat and 'Shift + P' to disable it (Good Practice)."
        self.instructions_message = "Welcome, adventurer! I'm your assistant. Ask me anything about quests or the game.  Press 'Shift + O' to Enbale Chat and 'Shift + P' to disable it (Good Practice)."

        # Display the initial welcome message
        self.set_message("Welcome", self.welcome_message)
        self.set_message("Commands: 'q' changes weapons, 'Space' to attack, then Up  Down Left Right are movements.", self.instructions_message)

        # Load player data if it exists
        self.load_player_data()

    def set_message(self, question, answer):
        """Store only the latest question and answer."""
        self.current_question = question
        self.current_answer = answer

    def handle_input(self, event):
        """Handle user input."""
        global checking_event 
        
        checking_event = False
        if event.type == pygame.KEYDOWN:
            # Check if Shift is pressed
            shift_pressed = pygame.key.get_pressed()[pygame.K_LSHIFT] or pygame.key.get_pressed()[pygame.K_RSHIFT]

            # Start typing when Shift + O is pressed
            if shift_pressed and event.key == pygame.K_o:
                self.is_typing = True
                self.text_input = ""  # Clear the input box when starting to type

            # Stop typing when Shift + P is pressed
            elif shift_pressed and event.key == pygame.K_p:
                self.is_typing = False

            if self.is_typing:
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

        self.save_player_data()

        game_context = f"""
        You are the Questmaster in an RPG.
        - The player has killed {self.player_stats.get('kills', 0)} enemies.
        - The player is at level {self.player_stats.get('level', 1)} with {self.player_stats.get('xp', 0)} XP.
        - The player has completed {self.player_stats.get('quests_completed', 0)} quests.
        - Provide quest guidance and game hints based on the player's habits.
        - Keep responses short and clear.
        - The map is available here: {MAP_IMAGE_PATH}
        - The killcount is {self.player_stats.get('kills', 0)}. You may ask quests related to the killcount.
        - Usually, when the killcount is more than 3, that means you probably already asked a quest related to increasing killings.
        - Note: The North is always to the right, and east is up.
        - Note: Never digress away from the game.
        - Example of place quests: find Rico Village and kill 4 enemies there.
        - The player has frequently visited these places: {', '.join(self.habits.get('frequent_places', []))}.
        - The player has completed these quests: {', '.join(self.habits.get('quests_completed', []))}.
        - Kill count trends: {self.habits.get('killcount_trends', [])}.
        - Do not tell the player locations, tell them to look for it, not mention map
        - First quest should always be to increase the killcount, 'q' changes weapons, 'Space' uses the weapon, then up down left right are directions.
        """

        full_prompt = game_context + f"\nPlayer: {prompt}"
        response = self.model.generate_content([full_prompt])

        return response.text.strip() if response.text else "No response"

    def save_player_data(self):
        """Save player stats and habits to a JSON file."""
        player_data = {
            'player_stats': self.player_stats,
            'habits': self.habits
        }

        with open('player_data.json', 'w') as json_file:
            json.dump(player_data, json_file, indent=4)

    def load_player_data(self):
        """Load player stats and habits from a JSON file."""
        if os.path.exists('player_data.json'):
            with open('player_data.json', 'r') as json_file:
                player_data = json.load(json_file)
                self.player_stats = player_data.get('player_stats', self.player_stats)
                self.habits = player_data.get('habits', self.habits)

    def draw(self, surface):
        """Draw the chat box and messages."""
        pygame.draw.rect(surface, self.bg_color, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, 2)

        y_offset = 42  # Increased initial y-offset to position text lower
        if self.current_question and self.current_answer:
            # Render the question
            question_surface = self.font.render(f"Prompt: {self.current_question}", True, self.question_color)
            surface.blit(question_surface, (self.rect.x + 10, self.rect.y + y_offset))
            y_offset += 30  # Increased spacing between question and answer

            # Render the answer
            answer_surface = self.font.render(f"Reply: {self.current_answer}", True, self.answer_color)
            surface.blit(answer_surface, (self.rect.x + 10, self.rect.y + y_offset))
            y_offset += 30  # Increased spacing after the answer

        # Draw the input box
        pygame.draw.rect(surface, (255, 255, 255), self.input_rect, 0)  # White input box
        pygame.draw.rect(surface, self.border_color, self.input_rect, 2)  # Border

        # Render placeholder or user input text
        if not self.text_input:
            placeholder_surface = self.font.render(self.placeholder_text, True, self.placeholder_color)
            surface.blit(placeholder_surface, (self.input_rect.x + 5, self.input_rect.y + 5))
        else:
            input_surface = self.font.render(self.text_input, True, self.text_color)
            surface.blit(input_surface, (self.input_rect.x + 5, self.input_rect.y + 5))

        # Draw the small box with the label
        pygame.draw.rect(surface, self.small_box_color, self.small_box_rect)
        pygame.draw.rect(surface, self.small_box_border_color, self.small_box_rect, 2)
        label_text = self.font.render("GemChat", True, (255, 255, 255))
        surface.blit(label_text, (self.small_box_rect.x + 5, self.small_box_rect.y + 5))