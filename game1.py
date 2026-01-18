import pygame
import random
import math

pygame.init()

# --- Colors ---
WHITE = (255, 255, 255)
ORANGE = (255, 165, 0)
BLACK = (0, 0, 0)
RED = (213, 50, 80)
GREEN = (0, 255, 0)
BLUE = (50, 153, 213)
DARK_ORANGE = (220, 110, 0)
PURPLE = (128, 0, 128)  # Purple color for water
YELLOW = (255, 255, 0)
PLUS_COLOR = GREEN  # Color for addition bubbles
MINUS_COLOR = RED  # Color for subtraction bubbles

# --- Screen Setup ---
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption('Orb Collectors!-')

# --- Game Settings ---
TRAIN_SIZE = 27
SPHERE_SIZE = 24
INITIAL_SPEED = 11

# --- Stars Background ---
NUM_STARS = 200  # Number of stars in the background
stars = []  # Will store star positions and sizes

# --- Fonts ---
font_style = pygame.font.SysFont("bahnschrift", 30)
score_font = pygame.font.SysFont("comicsansms", 50) # Increased font size
score_color = YELLOW #Added YELLOW to the score font, for visibilty purpose

clock = pygame.time.Clock()

# Sphere colors and their unique values
sphere_colors = [(0, 162, 232), (255, 127, 39), (0, 255, 0),
                 (255, 242, 0), (163, 73, 164), (0, 112, 192)]  # Blue, Orange, Green, Yellow, Purple, Blue
sphere_values = {sphere_colors[0]: 1, sphere_colors[1]: 2, sphere_colors[2]: 3,
                 sphere_colors[3]: 4, sphere_colors[4]: 5, sphere_colors[5]: 6}

# --- Addition and Subtraction Bubbles ---
ADDITION = '+'
SUBTRACTION = '-'
ADD_SUB_SIZE = 30 #bubble size of the additional bubble

# --- Water Setup ---
WATER_HEIGHT = 220
water_level = SCREEN_HEIGHT - WATER_HEIGHT
water_animation_offset = 0
SCORE_DISPLAY_OFFSET = 30  # Offset above water level

# --- Creation Rate Variables ---
NUM_BUBBLE_DECREASE_RATE = 15000 #Rate to reduce the Bubble creation rate
OP_BUBBLE_INCREASE_RATE = 10000 #Rate to increase the op creation

# Initialize stars with random positions
def init_stars():
    global stars
    stars = []
    for _ in range(NUM_STARS):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        size = random.randint(1, 3)  # Random star sizes
        brightness = random.randint(150, 255)  # Random brightness
        stars.append([x, y, size, brightness])

# Draw stars function
def draw_stars(screen):
    for star in stars:
        # Make some stars twinkle by slightly varying brightness
        brightness = max(150, min(255, star[3] + random.randint(-15, 15)))
        pygame.draw.circle(screen, (brightness, brightness, brightness), (star[0], star[1]), star[2])

class TrainEngine:
    def __init__(self, x, y, direction='right'):
        self.x = x
        self.y = y
        self.width = TRAIN_SIZE * 1.5
        self.height = TRAIN_SIZE
        self.direction = direction
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)  # Add a rect attribute

    def draw(self, screen):
        # Adjust drawing based on direction
        if self.direction == 'right':
            # Main body
            pygame.draw.rect(screen, ORANGE, [self.x, self.y, self.width, self.height])
            # Front triangle
            pygame.draw.polygon(screen, ORANGE, [
                [self.x + self.width, self.y + self.height // 2],
                [self.x + self.width + self.height // 2, self.y + self.height // 2],
                [self.x + self.width, self.y]
            ])
            # Windows
            pygame.draw.circle(screen, BLACK, [self.x + self.width // 3, self.y + self.height // 2], self.height // 5)
            pygame.draw.circle(screen, BLACK, [self.x + 2 * self.width // 3, self.y + self.height // 2], self.height // 8)
            # Top details
            pygame.draw.rect(screen, BLACK, [self.x, self.y - 5, self.width, 5])

        elif self.direction == 'left':
            # Main body
            pygame.draw.rect(screen, ORANGE, [self.x - self.width + TRAIN_SIZE, self.y, self.width, self.height])
            # Front triangle
            pygame.draw.polygon(screen, ORANGE, [
                [self.x - self.width + TRAIN_SIZE, self.y + self.height // 2],
                [self.x - self.width + TRAIN_SIZE - self.height // 2, self.y + self.height // 2],
                [self.x - self.width + TRAIN_SIZE, self.y]
            ])
            # Windows
            pygame.draw.circle(screen, BLACK, [self.x - self.width // 3, self.y + self.height // 2], self.height // 5)
            pygame.draw.circle(screen, BLACK, [self.x - 2 * self.width // 3 + TRAIN_SIZE, self.y + self.height // 2], self.height // 8)
            # Top details
            pygame.draw.rect(screen, BLACK, [self.x - self.width + TRAIN_SIZE, self.y - 5, self.width, 5])

        elif self.direction == 'down':
            # Main body
            pygame.draw.rect(screen, ORANGE, [self.x, self.y, self.height, self.width])
            # Front triangle
            pygame.draw.polygon(screen, ORANGE, [
                [self.x + self.height // 2, self.y + self.width],
                [self.x + self.height // 2, self.y + self.width + self.height // 2],
                [self.x, self.y + self.width]
            ])
            # Windows
            pygame.draw.circle(screen, BLACK, [self.x + self.height // 2, self.y + self.width // 3], self.height // 5)
            pygame.draw.circle(screen, BLACK, [self.x + self.height // 2, self.y + 2 * self.width // 3], self.height // 8)
            # Top details
            pygame.draw.rect(screen, BLACK, [self.x - 5, self.y, 5, self.width])

        elif self.direction == 'up':
            # Main body
            pygame.draw.rect(screen, ORANGE, [self.x, self.y - self.width + TRAIN_SIZE, self.height, self.width])
            # Front triangle
            pygame.draw.polygon(screen, ORANGE, [
                [self.x + self.height // 2, self.y - self.width + TRAIN_SIZE],
                [self.x + self.height // 2, self.y - self.width + TRAIN_SIZE - self.height // 2],
                [self.x, self.y - self.width + TRAIN_SIZE]
            ])
            # Windows
            pygame.draw.circle(screen, BLACK, [self.x + self.height // 2, self.y - self.width // 3], self.height // 5)
            pygame.draw.circle(screen, BLACK, [self.x + self.height // 2, self.y - 2 * self.width // 3 + TRAIN_SIZE], self.height // 8)
            # Top details
            pygame.draw.rect(screen, BLACK, [self.x - 5, self.y - self.width + TRAIN_SIZE, 5, self.width])

        self.rect.x = self.x  # update the rect x position
        self.rect.y = self.y  # update the rect y position

class TrainCoach:
    def __init__(self, x, y, direction='right', sphere_value=0): #Add sphere value
        self.x = x
        self.y = y
        self.width = TRAIN_SIZE * 1.5
        self.height = TRAIN_SIZE
        self.direction = direction
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)  # Add a rect attribute
        self.sphere_value = sphere_value  # Store the value of the sphere eaten
        self.falling = False
        self.fall_speed = 0

    def draw(self, screen):
        # Adjust drawing based on direction
        if self.direction == 'right':
            # Main body
            pygame.draw.rect(screen, ORANGE, [self.x, self.y, self.width, self.height])
            # Connector
            pygame.draw.rect(screen, DARK_ORANGE, [self.x - 10, self.y + self.height // 3, 20, self.height // 3])
            # Top details
            pygame.draw.rect(screen, BLACK, [self.x, self.y - 5, self.width, 5])
        elif self.direction == 'left':
            # Main body
            pygame.draw.rect(screen, ORANGE, [self.x - self.width + TRAIN_SIZE, self.y, self.width, self.height])
            # Connector
            pygame.draw.rect(screen, DARK_ORANGE, [self.x - 10, self.y + self.height // 3, 20, self.height // 3])
            # Top details
            pygame.draw.rect(screen, BLACK, [self.x, self.y - 5, self.width, 5])

        elif self.direction == 'down':
            # Main body
            pygame.draw.rect(screen, ORANGE, [self.x, self.y, self.height, self.width])
            # Connector
            pygame.draw.rect(screen, DARK_ORANGE, [self.x - 10, self.y + self.height // 3, 20, self.height // 3])
            # Top details
            pygame.draw.rect(screen, BLACK, [self.x, self.y - 5, self.width, 5])

        elif self.direction == 'up':
            # Main body
            pygame.draw.rect(screen, ORANGE, [self.x, self.y - self.width + TRAIN_SIZE, self.height, self.width])
            # Connector
            pygame.draw.rect(screen, DARK_ORANGE, [self.x - 10, self.y + self.height // 3, 20, self.height // 3])
            # Top details
            pygame.draw.rect(screen, BLACK, [self.x, self.y - 5, self.width, 5])

        self.rect.x = self.x  # update the rect x position
        self.rect.y = self.y  # update the rect y position

        # Display the sphere value on the coach
        value_surface = score_font.render(str(self.sphere_value), True, BLACK)
        value_rect = value_surface.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(value_surface, value_rect)

    def update_falling(self):
        if self.falling:
            self.fall_speed += 0.5
            self.y += self.fall_speed
            return self.y + self.height > water_level
        return False

class MagicSphere:
    def __init__(self, x, y, type='color'): #type of sphere
        self.x = x
        self.y = y
        self.size = SPHERE_SIZE
        self.type = type

        if type == 'color':
            self.color_index = random.randint(0, 5)
            self.color = sphere_colors[self.color_index]
            self.value = sphere_values[self.color]
        elif type == ADDITION or type == SUBTRACTION:
            self.color = PLUS_COLOR if type == ADDITION else MINUS_COLOR # Different Colors
            self.size = ADD_SUB_SIZE
            self.value = 0  # No value for add/sub bubbles
        self.glow_size = self.size + 10
        self.glow_alpha = 150  # Transparency for glow effect

    def draw(self, screen):
        # Draw glow effect
        glow_surface = pygame.Surface((self.glow_size*2, self.glow_size*2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*self.color, self.glow_alpha), (self.glow_size, self.glow_size), self.glow_size)
        screen.blit(glow_surface, (self.x - self.glow_size, self.y - self.glow_size))

        # Draw main sphere
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.size)

        # Draw highlight
        highlight_pos = (self.x - self.size//3, self.y - self.size//3)
        highlight_size = self.size // 4
        pygame.draw.circle(screen, (255, 255, 255, 200), highlight_pos, highlight_size)

        # Draw + or - sign
        if self.type == ADDITION or self.type == SUBTRACTION:
            sign_font = pygame.font.SysFont("comicsansms", int(self.size * 1.2))
            sign_surface = sign_font.render(self.type, True, BLACK)
            sign_rect = sign_surface.get_rect(center=(self.x, self.y))
            screen.blit(sign_surface, sign_rect)

def display_score(score, screen, screen_pos = [10, 10]):
    value = score_font.render("Score: " + str(score), True, score_color)
    value_rect = value.get_rect(center=screen_pos) # Align the text in center
    screen.blit(value, value_rect)

def message(msg, color):
    mesg = font_style.render(msg, True, color)
    msg_rect = mesg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
    screen.blit(mesg, msg_rect)

def get_random_food_position():
    """Ensures food spawns within the 900x800 centered area."""
    center_x = SCREEN_WIDTH // 2
    center_y = SCREEN_HEIGHT // 2

    box_width = 900
    box_height = 800

    min_x = max(center_x - box_width // 2, 0)
    min_y = max(center_y - box_height // 2, 0)

    max_x = min_x + box_width - SPHERE_SIZE
    max_y = min_y + box_height - SPHERE_SIZE

    return (
        random.randint(min_x // 10, max_x // 10) * 10,
        random.randint(min_y // 10, max_y // 10) * 10
    )

def distance(x1, y1, x2, y2):
    """Calculate the Euclidean distance between two points."""
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def draw_water(screen, offset):
    """Draws animated water at the bottom of the screen."""
    for x in range(0, SCREEN_WIDTH, 10):
        y = water_level + int(math.sin((x + offset) * 0.02) * 10)  # Sine-wave
        pygame.draw.line(screen, PURPLE, (x, y), (x, SCREEN_HEIGHT), 10)

def game_loop():
    global SCREEN_WIDTH, SCREEN_HEIGHT, screen, water_animation_offset, WATER_HEIGHT, water_level

    SCREEN_WIDTH = screen.get_width()
    SCREEN_HEIGHT = screen.get_height()
    WATER_HEIGHT = 220
    water_level = SCREEN_HEIGHT - WATER_HEIGHT

    # Initialize stars when game starts
    init_stars()

    train_x, train_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    train_x_change, train_y_change = 0, 0
    train_length = 1  # Initially only the engine
    speed_multiplier = 1.0
    paused = False
    direction = 'right'
    score = 0  # initial score
    falling_coaches = []  # List to hold falling coaches
    plus_count = 0  # Count of addition bubbles picked
    minus_count = 0  # Count of subtraction bubbles picked

    train_parts = [TrainEngine(train_x, train_y, direction)]  # Start with just the engine

    # --- Multiple Spheres ---
    spheres = []  # List to hold multiple spheres
    add_sub_spheres =[] #List to hold additional sphere

    # --- Sphere Creation Rate ---
    sphere_creation_rate = 5000  # Initial rate: 1 sphere every 5 seconds (in milliseconds)
    add_sub_creation_rate = 7000 #Intial rate for add and sub bubbles
    sphere_creation_timer = pygame.time.get_ticks()  # Last time a sphere was created
    add_sub_creation_timer = pygame.time.get_ticks() #Last time add or sub bubble was created
    sphere_increase_difficulty_rate = 20000 # Reduce time every 20 seconds
    sphere_increase_difficulty_timer = pygame.time.get_ticks() #Reduce the bubble creation timer
    op_creation_increase_timer = pygame.time.get_ticks() #Timer that increases the rate of op creation

    clock = pygame.time.Clock()
    game_over = False
    game_close = False

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and direction != 'right':
                    train_x_change = -TRAIN_SIZE
                    train_y_change = 0
                    direction = 'left'
                elif event.key == pygame.K_RIGHT and direction != 'left':
                    train_x_change = TRAIN_SIZE
                    train_y_change = 0
                    direction = 'right'
                elif event.key == pygame.K_UP and direction != 'down':
                    train_y_change = -TRAIN_SIZE
                    train_x_change = 0
                    direction = 'up'
                elif event.key == pygame.K_DOWN and direction != 'up':
                    train_y_change = TRAIN_SIZE
                    train_x_change = 0
                    direction = 'down'
                elif event.key == pygame.K_p:
                    paused = not paused
                elif event.key == pygame.K_1:
                    speed_multiplier = 0.75
                elif event.key == pygame.K_2:
                    speed_multiplier = 1.0
                elif event.key == pygame.K_3:
                    speed_multiplier = 1.25

            elif event.type == pygame.VIDEORESIZE:
                SCREEN_WIDTH, SCREEN_HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                init_stars()  # Redistribute stars when screen is resized

        if paused:
            screen.fill((20, 20, 50))  # Dark blue background
            draw_stars(screen)  # Draw stars even in pause screen
            msg = font_style.render('Paused. Press P to resume.', True, WHITE)
            screen.blit(msg, [SCREEN_WIDTH // 3, SCREEN_HEIGHT // 3])
            pygame.display.update()
            pygame.time.wait(100)
            continue

        # Update train position
        train_x += train_x_change
        train_y += train_y_change

        # Check for collisions with boundaries
        if train_x >= SCREEN_WIDTH or train_x < 0 or train_y >= SCREEN_HEIGHT or train_y < 0:
            game_close = True

        # Fill with dark blue and draw stars
        screen.fill((20, 20, 50))  # Dark blue background
        draw_stars(screen)

        # --- Sphere Creation Logic ---
        current_time = pygame.time.get_ticks()
        if current_time - sphere_creation_timer > sphere_creation_rate:
            food_x, food_y = get_random_food_position()
            spheres.append(MagicSphere(food_x, food_y))
            sphere_creation_timer = current_time
        #---Add sub logic
        if current_time - add_sub_creation_timer > add_sub_creation_rate:
            food_x, food_y = get_random_food_position()
            #randomly chose add or sub
            type = random.choice([ADDITION, SUBTRACTION])
            add_sub_spheres.append(MagicSphere(food_x, food_y, type))
            add_sub_creation_timer = current_time

        # --- Increase difficulty ---
        if current_time - sphere_increase_difficulty_timer > sphere_increase_difficulty_rate and sphere_creation_rate > 1000:
            sphere_creation_rate -= 250 # Reduce creation rate
            sphere_increase_difficulty_timer = current_time

        # --- Draw and handle spheres ---
        for sphere in spheres[:]:  # Iterate over a slice copy to allow removal
            sphere.draw(screen)
            # Detect food collision and reposition it correctly
            if abs(train_x - sphere.x) < TRAIN_SIZE and abs(train_y - sphere.y) < TRAIN_SIZE:
                spheres.remove(sphere)  # Remove eaten sphere
                food_x, food_y = get_random_food_position()
                spheres.append(MagicSphere(food_x, food_y))  # Create a new random sphere
                train_length += 1  # Increase length of the train

                # Add a new coach at the end of the train
                last_part = train_parts[-1] if train_parts else train_parts[0]
                new_coach = TrainCoach(last_part.x, last_part.y, direction, sphere.value)  # Pass the sphere value
                train_parts.append(new_coach)

        #---Add and sub bubble handling---
        for sphere in add_sub_spheres[:]:
            sphere.draw(screen)
            if abs(train_x - sphere.x) < TRAIN_SIZE and abs(train_y - sphere.y) < TRAIN_SIZE:
                add_sub_spheres.remove(sphere)
                op_type = sphere.type

                # Only perform operation if we have at least 2 coaches (not counting engine)
                if len(train_parts) > 2:  # Engine + 2 coaches
                    if op_type == ADDITION:
                        plus_count += 1
                        # Get last two coaches (excluding engine)
                        coach1 = train_parts[-2]
                        coach2 = train_parts[-1]
                        # Calculate score based on operation
                        score += (coach1.sphere_value + coach2.sphere_value)
                        # Set both coaches to fall
                        coach1.falling = True
                        coach2.falling = True
                        falling_coaches.extend([coach1, coach2])
                        # Remove both coaches from train
                        train_parts = train_parts[:-2]
                        train_length -= 2
                    elif op_type == SUBTRACTION:
                        minus_count += 1
                        # Get last two coaches (excluding engine)
                        coach1 = train_parts[-2]
                        coach2 = train_parts[-1]
                        # Calculate score based on operation
                        score += (coach1.sphere_value - coach2.sphere_value)
                        # Set both coaches to fall
                        coach1.falling = True
                        coach2.falling = True
                        falling_coaches.extend([coach1, coach2])
                        # Remove both coaches from train
                        train_parts = train_parts[:-2]
                        train_length -= 2
                else:
                    # Not enough coaches - game over if we only have engine left
                    if len(train_parts) <= 1:
                        game_close = True

                # Create new operation sphere
                food_x, food_y = get_random_food_position()
                type = random.choice([ADDITION, SUBTRACTION])#recreate the bubble with random type
                add_sub_spheres.append(MagicSphere(food_x, food_y, type))

        #Check if the train engine was consumed and if it was close the game
        if len(train_parts) <= 0:
            game_close = True

        # --- Update train parts positions based on history---
        for i, part in enumerate(train_parts):
            part.direction = direction

            if i == 0:  # Engine
                part.x = train_x
                part.y = train_y
            else:  # Coaches follow the previous part
                prev_part = train_parts[i-1]

                # Calculate the distance between current coach and the previous one
                dist = distance(part.x, part.y, prev_part.x, prev_part.y)

                # If they are too far apart, adjust the coach position
                if dist > TRAIN_SIZE * 1.6:  # Slightly more than the width of the part
                    # Calculate angle towards the previous part
                    angle = math.atan2(prev_part.y - part.y, prev_part.x - part.x)

                    # Move the coach closer to the previous part
                    part.x = prev_part.x - math.cos(angle) * (part.width + 5)  # Adjust 5 for slight overlap
                    part.y = prev_part.y - math.sin(angle) * (part.width + 5)  # Adjust 5 for slight overlap

            part.draw(screen)

        # --- Update falling coaches ---
        for coach in falling_coaches[:]:
            if coach.update_falling():
                falling_coaches.remove(coach)
            else:
                coach.draw(screen)

        # --- Draw Water ---
        draw_water(screen, water_animation_offset)
        water_animation_offset += 2

        # Display score at the water level
        score_position = (SCREEN_WIDTH // 2, water_level - SCORE_DISPLAY_OFFSET)
        display_score(score, screen, score_position)

        # Display score at the top
        display_score(score, screen)

        pygame.display.update()

        clock.tick(int(INITIAL_SPEED * speed_multiplier))

        while game_close:
            screen.fill((20, 20, 50))
            draw_stars(screen)
            message("Game Over! Press C-Play Again or Q-Quit", RED)
            # Display the final score
            score_position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50) # adjust the Final score Location
            display_score(score, screen, score_position)

            # Display the counts of "+" and "-" bubbles
            plus_surface = score_font.render(f"+: {plus_count}", True, PLUS_COLOR)
            minus_surface = score_font.render(f"-: {minus_count}", True, MINUS_COLOR)

            plus_rect = plus_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20)) #location of Plus
            minus_rect = minus_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))#LOcation of Minus

            screen.blit(plus_surface, plus_rect)
            screen.blit(minus_surface, minus_rect)

            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    elif event.key == pygame.K_c:
                        game_loop()
                        return

# --- Start Game ---
if __name__ == '__main__':
    try:
        game_loop()
    finally:
        pygame.quit()