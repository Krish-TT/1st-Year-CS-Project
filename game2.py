import pygame
import random
import math
import heapq
import time
import sys
pygame.init()

#Colors
WHITE = (255, 255, 255)
ORANGE = (255, 165, 0)
BLACK = (0, 0, 0)
RED = (213, 50, 80)
GREEN = (0, 255, 0)
BLUE = (50, 153, 213)
DARK_ORANGE = (220, 110, 0)
PURPLE = (128, 0, 128)
YELLOW = (255, 255, 0)
PLUS_COLOR = GREEN
MINUS_COLOR = RED
STATION_COLOR = (200, 200, 200)
TRACK_COLOR = (100, 100, 100)

#Screen Setup
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE | pygame.FULLSCREEN)
pygame.display.set_caption('Orb Collector! - Graph Version')

#Game Settings
TRAIN_SIZE = 27
SPHERE_SIZE = 24
INITIAL_SPEED = 11
STATION_RADIUS = 15
TRACK_WIDTH = 5
PROBABILITY_OF_OPERATOR = 0.2 #20% chance for an operator at a station
NUM_STATIONS = 8
GAME_DURATION = 120 #2 minutes in seconds
NUM_STARS = 200
stars = []

#Water Setup
WATER_HEIGHT = 100 
water_level = SCREEN_HEIGHT - WATER_HEIGHT
water_animation_offset = 0
SCORE_DISPLAY_OFFSET = 30

#Fonts
font_style = pygame.font.SysFont("bahnschrift", 30)
score_font = pygame.font.SysFont("comicsansms", 50)
small_font = pygame.font.SysFont("comicsansms", 20)
timer_font = pygame.font.SysFont("comicsansms", 60)
score_color = YELLOW

clock = pygame.time.Clock()

sphere_colors = [(0, 162, 232), (255, 127, 39), (0, 255, 0),
                 (255, 242, 0), (163, 73, 164), (0, 112, 192)]
sphere_values = {sphere_colors[0]: 1, sphere_colors[1]: 2, sphere_colors[2]: 3,
                 sphere_colors[3]: 4, sphere_colors[4]: 5, sphere_colors[5]: 6}

ADDITION = '+'
SUBTRACTION = '-'
ADD_SUB_SIZE = 30

#Graph/Map Setup
class Station:
    def __init__(self, x, y, name):
        self.x = x
        self.y = y
        self.name = name
        self.connections = [] 
        self.spheres = []
        self.operator = None  #Either '+', '-', or None
       
    def __hash__(self):
        return hash((self.x, self.y, self.name))
   
    def __eq__(self, other):
        if not isinstance(other, Station):
            return False
        return (self.x, self.y, self.name) == (other.x, other.y, other.name)
   
    def __lt__(self, other):
        return (self.x, self.y, self.name) < (other.x, other.y, other.name)
      
    def draw(self, screen):
        #Draw connections first (so stations appear on top)
        for connected_station in self.connections:
            pygame.draw.line(screen, TRACK_COLOR, (self.x, self.y),
                           (connected_station.x, connected_station.y), TRACK_WIDTH)
      
        #Draw the station
        pygame.draw.circle(screen, STATION_COLOR, (self.x, self.y), STATION_RADIUS)
        #Draw station name
        name_surface = small_font.render(self.name, True, WHITE)
        name_rect = name_surface.get_rect(center=(self.x, self.y + STATION_RADIUS + 10))
        screen.blit(name_surface, name_rect)
       
        #Draw operator, if any
        if self.operator:
            operator_color = PLUS_COLOR if self.operator == ADDITION else MINUS_COLOR
            operator_font = pygame.font.SysFont("comicsansms", int(STATION_RADIUS * 1.2))
            operator_surface = operator_font.render(self.operator, True, operator_color)
            operator_rect = operator_surface.get_rect(center=(self.x - 25, self.y))
            screen.blit(operator_surface, operator_rect)
      
        #Draw spheres at this station
        for i, sphere in enumerate(self.spheres):
            sphere.x = self.x + (i * 30) - (len(self.spheres) * 15 + 15)
            sphere.y = self.y - 40
            sphere.draw(screen)

class GraphMap:
    def __init__(self):
        self.stations = []
        self.current_station = None
        self.path = []  #Current path the train is following
        self.path_index = 0
      
    def add_station(self, station):
        self.stations.append(station)
        if len(self.stations) == 1:  #First station is the starting point
            self.current_station = station
          
    def connect_stations(self, station1, station2):
        if station2 not in station1.connections:
            station1.connections.append(station2)
        if station1 not in station2.connections:
            station2.connections.append(station1)
          
    def find_path(self, start, end):
        #Priority queue: (distance, current_station, path)
        heap = [(0, start, [])]
        visited = set()
      
        while heap:
            dist, current, path = heapq.heappop(heap)
          
            if current == end:
                return path + [current]
              
            if current in visited:
                continue
              
            visited.add(current)
          
            for neighbor in current.connections:
                if neighbor not in visited:
                    dx = current.x - neighbor.x
                    dy = current.y - neighbor.y
                    distance = math.sqrt(dx*dx + dy*dy)
                  
                    heapq.heappush(heap, (dist + distance, neighbor, path + [current]))
      
        return None  #No path found
      
    def draw(self, screen):
        # Draw all stations and connections
        for station in self.stations:
            station.draw(screen)
          
        # Draw current path if one exists
        if len(self.path) > 1:
            for i in range(len(self.path)-1):
                pygame.draw.line(screen, GREEN, (self.path[i].x, self.path[i].y),
                               (self.path[i+1].x, self.path[i+1].y), 3)
   
    def has_valid_paths(self, station):
        """Check if there are any reachable stations with spheres or operators from the given station"""
        visited = set()
        queue = [station]
       
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
           
            # If this station has spheres or is an operator station (and not the current station)
            if (current != station) and (current.spheres or current.operator):
                return True
               
            for neighbor in current.connections:
                if neighbor not in visited:
                    queue.append(neighbor)
       
        return False

def init_stars():
    global stars
    stars = []
    for _ in range(NUM_STARS):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        size = random.randint(1, 3)
        brightness = random.randint(150, 255)
        stars.append([x, y, size, brightness])

def draw_stars(screen):
    for star in stars:
        brightness = max(150, min(255, star[3] + random.randint(-15, 15)))
        pygame.draw.circle(screen, (brightness, brightness, brightness), (star[0], star[1]), star[2])
       
class TrainEngine:
    def __init__(self, x, y, direction='right'):
        self.x = x
        self.y = y
        self.width = TRAIN_SIZE * 1.5
        self.height = TRAIN_SIZE
        self.direction = direction
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.target_station = None
        self.moving = False
        self.path_progress = 0  # 0 to 1 representing progress along current path segment
        self.arrival_threshold = 5  # Distance threshold for arriving at a station
      
    def update_direction(self, next_x, next_y):
        dx = next_x - self.x
        dy = next_y - self.y
      
        if abs(dx) > abs(dy):
            self.direction = 'right' if dx > 0 else 'left'
        else:
            self.direction = 'down' if dy > 0 else 'up'
      
    def has_reached_target(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        return distance <= self.arrival_threshold

    def draw(self, screen):
        pygame.draw.rect(screen, ORANGE, [self.x, self.y, self.width, self.height])
      
        # Draw direction-specific details
        if self.direction == 'right':
            # Front triangle
            pygame.draw.polygon(screen, ORANGE, [
                [self.x + self.width, self.y + self.height // 2],
                [self.x + self.width + self.height // 2, self.y + self.height // 2],
                [self.x + self.width, self.y]
            ])
            # Windows
            pygame.draw.circle(screen, BLACK, [self.x + self.width // 3, self.y + self.height // 2], self.height // 5)
            pygame.draw.circle(screen, BLACK, [self.x + 2 * self.width // 3, self.y + self.height // 2], self.height // 8)
        elif self.direction == 'left':
            # Front triangle
            pygame.draw.polygon(screen, ORANGE, [
                [self.x, self.y + self.height // 2],
                [self.x - self.height // 2, self.y + self.height // 2],
                [self.x, self.y]
            ])
            # Windows
            pygame.draw.circle(screen, BLACK, [self.x + self.width // 3, self.y + self.height // 2], self.height // 5)
            pygame.draw.circle(screen, BLACK, [self.x + 2 * self.width // 3, self.y + self.height // 2], self.height // 8)
        elif self.direction == 'down':
            # Front triangle
            pygame.draw.polygon(screen, ORANGE, [
                [self.x + self.width // 2, self.y + self.height],
                [self.x + self.width // 2, self.y + self.height + self.height // 2],
                [self.x, self.y + self.height]
            ])
            # Windows
            pygame.draw.circle(screen, BLACK, [self.x + self.width // 2, self.y + self.height // 3], self.height // 5)
            pygame.draw.circle(screen, BLACK, [self.x + self.width // 2, self.y + 2 * self.height // 3], self.height // 8)
        elif self.direction == 'up':
            # Front triangle
            pygame.draw.polygon(screen, ORANGE, [
                [self.x + self.width // 2, self.y],
                [self.x + self.width // 2, self.y - self.height // 2],
                [self.x, self.y]
            ])
            # Windows
            pygame.draw.circle(screen, BLACK, [self.x + self.width // 2, self.y + self.height // 3], self.height // 5)
            pygame.draw.circle(screen, BLACK, [self.x + self.width // 2, self.y + 2 * self.height // 3], self.height // 8)
      
        # Top details
        pygame.draw.rect(screen, BLACK, [self.x, self.y - 5, self.width, 5])
      
        self.rect.x = self.x
        self.rect.y = self.y

class TrainCoach:
    def __init__(self, x, y, direction='right', sphere_value=0):
        self.x = x
        self.y = y
        self.width = TRAIN_SIZE * 1.5
        self.height = TRAIN_SIZE
        self.direction = direction
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.sphere_value = sphere_value
        self.falling = False
        self.fall_speed = 0
      
    def draw(self, screen):
        pygame.draw.rect(screen, ORANGE, [self.x, self.y, self.width, self.height])
        pygame.draw.rect(screen, DARK_ORANGE, [self.x - 10, self.y + self.height // 3, 20, self.height // 3])
        pygame.draw.rect(screen, BLACK, [self.x, self.y - 5, self.width, 5])
      
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
    def __init__(self, x, y, type='color'):
        self.x = x
        self.y = y
        self.size = SPHERE_SIZE
        self.type = type
      
        if type == 'color':
            self.color_index = random.randint(0, 5)
            self.color = sphere_colors[self.color_index]
            self.value = sphere_values[self.color]
        elif type in (ADDITION, SUBTRACTION):
            self.color = PLUS_COLOR if type == ADDITION else MINUS_COLOR
            self.size = ADD_SUB_SIZE
            self.value = 0
          
        self.glow_size = self.size + 10
        self.glow_alpha = 150
      
    def draw(self, screen):
        glow_surface = pygame.Surface((self.glow_size*2, self.glow_size*2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*self.color, self.glow_alpha), (self.glow_size, self.glow_size), self.glow_size)
        screen.blit(glow_surface, (self.x - self.glow_size, self.y - self.glow_size))
      
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.size)
        highlight_pos = (self.x - self.size//3, self.y - self.size//3)
        highlight_size = self.size // 4
        pygame.draw.circle(screen, (255, 255, 255, 200), highlight_pos, highlight_size)
      
        if self.type in (ADDITION, SUBTRACTION):
            sign_font = pygame.font.SysFont("comicsansms", int(self.size * 1.2))
            sign_surface = sign_font.render(self.type, True, BLACK)
            sign_rect = sign_surface.get_rect(center=(self.x, self.y))
            screen.blit(sign_surface, sign_rect)

def display_score(score, screen, screen_pos=(SCREEN_WIDTH // 2, water_level - SCORE_DISPLAY_OFFSET)):
    value = score_font.render("Score: " + str(score), True, score_color)
    value_rect = value.get_rect(center=(SCREEN_WIDTH // 2, water_level - SCORE_DISPLAY_OFFSET))
    screen.blit(value, value_rect)

def display_timer(time_left, screen):
    minutes = time_left // 60
    seconds = time_left % 60
    timer_text = f"Time: {minutes:02d}:{seconds:02d}"
    
    # Create a smaller font for the timer
    large_timer_font = pygame.font.SysFont("comicsansms", 40)  # Decreased from 60
    timer_surface = large_timer_font.render(timer_text, True, WHITE)
    
    # Create a solid background rectangle with more padding
    padding = 15  # Decreased padding
    timer_bg = pygame.Rect(
        SCREEN_WIDTH // 2 - timer_surface.get_width() // 2 - padding,
        15,  # Moved up slightly
        timer_surface.get_width() + padding * 2,
        timer_surface.get_height() + padding * 2
    )
    
    # Draw solid black background
    pygame.draw.rect(screen, BLACK, timer_bg)
    
    # Draw thick red border
    pygame.draw.rect(screen, RED, timer_bg, 5)
    
    # Draw the text
    timer_rect = timer_surface.get_rect(center=timer_bg.center)
    screen.blit(timer_surface, timer_rect)

def message(msg, color):
    mesg = font_style.render(msg, True, color)
    msg_rect = mesg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))  # Moved up to 1/3 of screen height
    screen.blit(mesg, msg_rect)

def draw_water(screen, offset):
    for x in range(0, SCREEN_WIDTH, 10):
        y = water_level + int(math.sin((x + offset) * 0.02) * 10)
        pygame.draw.line(screen, PURPLE, (x, y), (x, SCREEN_HEIGHT), 10)

def create_initial_stations():
    """Create a set of stations at specific positions for the initial map."""
    # Calculate safe area with 50px padding
    safe_width = SCREEN_WIDTH - 100
    safe_height = SCREEN_HEIGHT - WATER_HEIGHT - 100
   
    # Define positions in a grid pattern within safe area
    positions = [
        (100 + safe_width * 0.2, 100 + safe_height * 0.2),  # A
        (100 + safe_width * 0.5, 100 + safe_height * 0.2),  # B
        (100 + safe_width * 0.8, 100 + safe_height * 0.3),  # C
        (100 + safe_width * 0.7, 100 + safe_height * 0.6),  # D
        (100 + safe_width * 0.3, 100 + safe_height * 0.7),  # E
        (100 + safe_width * 0.5, 100 + safe_height * 0.5),  # F
        (100 + safe_width * 0.2, 100 + safe_height * 0.5),  # G
        (100 + safe_width * 0.8, 100 + safe_height * 0.8)   # H
    ]
   
    stations = [
        Station(int(positions[0][0]), int(positions[0][1]), "A"),
        Station(int(positions[1][0]), int(positions[1][1]), "B"),
        Station(int(positions[2][0]), int(positions[2][1]), "C"),
        Station(int(positions[3][0]), int(positions[3][1]), "D"),
        Station(int(positions[4][0]), int(positions[4][1]), "E"),
        Station(int(positions[5][0]), int(positions[5][1]), "F"),
        Station(int(positions[6][0]), int(positions[6][1]), "G"),
        Station(int(positions[7][0]), int(positions[7][1]), "H")
    ]
    return stations

def create_map(stations):
    """Create a map with a given set of stations and some organized connections."""
    game_map = GraphMap()

    # Add stations to the map
    for station in stations:
        game_map.add_station(station)
        # Randomly assign an operator to the station
        if random.random() < PROBABILITY_OF_OPERATOR:
            station.operator = random.choice([ADDITION, SUBTRACTION])

    # Define organized connections (e.g., a grid-like or circular pattern)
    connections = [
        (0, 1), (1, 2), (2, 3),  # Top row
        (4, 5), (5, 6), (6, 7),  # Bottom row
        (0, 4), (1, 5), (2, 6), (3, 7),  # Vertical connections
        (0, 5), (3, 6)  # Diagonal connections
    ]

    # Connect the stations
    for i, j in connections:
        if i < len(stations) and j < len(stations):  # Ensure the stations exist
            game_map.connect_stations(stations[i], stations[j])

    return game_map

def reposition_stations(game_map):
    """Repositions the stations in a more organized manner within safe boundaries."""
    # Calculate safe area with 50px padding
    safe_width = SCREEN_WIDTH - 100
    safe_height = SCREEN_HEIGHT - WATER_HEIGHT - 100
   
    # Define positions in a grid pattern within safe area
    positions = []
    for i in range(NUM_STATIONS):
        row = i // (NUM_STATIONS // 2)
        col = i % (NUM_STATIONS // 2)
        x = 100 + (safe_width / (NUM_STATIONS // 2 + 1)) * (col + 1)
        y = 100 + (safe_height / 3) * (row + 1)
        positions.append((x, y))

    # Assign new positions to stations
    for i, station in enumerate(game_map.stations):
        x, y = positions[i]
        station.x = int(x)
        station.y = int(y)

    # After repositioning, clear existing spheres and regenerate them
    for station in game_map.stations:
        station.spheres = []
        if random.random() < 0.5:  # 50% chance to have a sphere
            station.spheres.append(MagicSphere(station.x, station.y))
        # Randomly assign an operator to the station
        if random.random() < PROBABILITY_OF_OPERATOR:
            station.operator = random.choice([ADDITION, SUBTRACTION])
        else:
            station.operator = None  # Ensure no operator remains from previous round
   
    # Rebuild connections with some randomness
    for station in game_map.stations:
        station.connections = []  # Clear existing connections
   
    for i in range(len(game_map.stations)):
        # Connect each station to a random subset of other stations
        num_connections = random.randint(1, 3)  # Connect to 1-3 other stations
        possible_connections = list(range(len(game_map.stations)))
        possible_connections.remove(i)  # Don't connect to itself
       
        connections = random.sample(possible_connections, min(num_connections, len(possible_connections)))
       
        for j in connections:
            game_map.connect_stations(game_map.stations[i], game_map.stations[j])
           
    return game_map

def detach_last_two_coaches(train_parts, falling_coaches):
    """Detach the last two coaches from the train and make them fall."""
    if len(train_parts) > 1:  # At least one coach besides the engine
        # Get the last two coaches (or just one if only one coach exists)
        num_to_detach = min(2, len(train_parts) - 1)
        for _ in range(num_to_detach):
            if len(train_parts) > 1:  # Check again in case we're down to just engine
                coach = train_parts.pop()
                coach.falling = True
                falling_coaches.append(coach)
        return num_to_detach
    return 0

def game_loop():
    global SCREEN_WIDTH, SCREEN_HEIGHT, screen, water_animation_offset, WATER_HEIGHT, water_level
   
    SCREEN_WIDTH = screen.get_width()
    SCREEN_HEIGHT = screen.get_height()
    WATER_HEIGHT = 100  # Decreased from 150
    water_level = SCREEN_HEIGHT - WATER_HEIGHT
   
    init_stars()
    initial_stations = create_initial_stations()
    game_map = create_map(initial_stations)
   
    # Start at the first station
    current_station = game_map.stations[0]
    train = TrainEngine(current_station.x, current_station.y)
    train_parts = [train]
    train_length = 1
   
    speed_multiplier = 1.0
    paused = False
    score = 0
    falling_coaches = []
    plus_count = 0
    minus_count = 0
    time_up = False  # Flag for time-up condition
   
    # Add initial spheres to stations
    for station in game_map.stations:
        if random.random() < 0.5:  # 50% chance to have a sphere
            station.spheres.append(MagicSphere(station.x, station.y))
   
    clock = pygame.time.Clock()
    game_over = False
    game_close = False
    
    # Timer setup
    start_time = time.time()
    time_left = GAME_DURATION
   
    while not game_over:
        # Calculate remaining time
        current_time = time.time()
        elapsed = current_time - start_time
        time_left = max(0, GAME_DURATION - int(elapsed))
        
        # Check if time is up
        if time_left <= 0 and not game_close:
            game_close = True
            time_up = True
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
              
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:  # Immediate quit on Q key
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_p:
                    paused = not paused
                elif event.key == pygame.K_1:
                    speed_multiplier = 0.75
                elif event.key == pygame.K_2:
                    speed_multiplier = 1.0
                elif event.key == pygame.K_3:
                    speed_multiplier = 1.25
                elif event.key == pygame.K_SPACE and not train.moving:
                    # Find the station with the mouse cursor
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    for station in game_map.stations:
                        if math.sqrt((station.x - mouse_x)**2 + (station.y - mouse_y)**2) < STATION_RADIUS:
                            # Calculate path to this station
                            path = game_map.find_path(current_station, station)
                            if path and len(path) > 1:
                                game_map.path = path
                                game_map.path_index = 1
                                train.moving = True
                                train.target_station = station
                                current_station = station
                                break
                elif event.key == pygame.K_r:
                    game_map = reposition_stations(game_map)
                    # After repositioning, the train should start at the first station again
                    current_station = game_map.stations[0]
                    train.x = current_station.x
                    train.y = current_station.y
                    train.target_station = None
                    train.moving = False
                    game_map.current_station = current_station
                    # Clear existing path
                    game_map.path = []
                    game_map.path_index = 0
                  
            elif event.type == pygame.VIDEORESIZE:
                SCREEN_WIDTH, SCREEN_HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                init_stars()
              
        if paused:
            screen.fill((20, 20, 50))
            draw_stars(screen)
            msg = font_style.render('Paused. Press P to resume.', True, WHITE)
            screen.blit(msg, [SCREEN_WIDTH // 3, SCREEN_HEIGHT // 3])
            pygame.display.update()
            pygame.time.wait(100)
            continue
          
        # Check if all stations are empty (all orbs collected)
        all_stations_empty = all(not station.spheres for station in game_map.stations)
        if all_stations_empty and not train.moving and not time_up:
            # Instead of ending game, refresh the map with new orbs
            game_map = reposition_stations(game_map)
            current_station = game_map.stations[0]
            train.x = current_station.x
            train.y = current_station.y
            train.target_station = None
            train.moving = False
            game_map.current_station = current_station
            game_map.path = []
            game_map.path_index = 0
          
        # Move train along path if one exists
        if train.moving and game_map.path and game_map.path_index < len(game_map.path):
            current_target = game_map.path[game_map.path_index]
          
            # Calculate direction vector
            dx = current_target.x - train.x
            dy = current_target.y - train.y
            distance = math.sqrt(dx*dx + dy*dy)
          
            # Normalize and scale by speed
            if distance > train.arrival_threshold:
                dx = dx / distance * (INITIAL_SPEED * speed_multiplier)
                dy = dy / distance * (INITIAL_SPEED * speed_multiplier)
              
                train.x += dx
                train.y += dy
                train.update_direction(current_target.x, current_target.y)
            else:
                # Reached the current target in path
                train.x = current_target.x
                train.y = current_target.y
                game_map.path_index += 1
              
                # If we reached the final destination
                if game_map.path_index >= len(game_map.path):
                    train.moving = False
                    game_map.path = []
                    game_map.path_index = 0
                  
                    # Check for spheres at this station
                    if train.target_station.spheres:
                        sphere = train.target_station.spheres.pop(0)
                        train_length += 1
                      
                        # Add a new coach at the end of the train
                        last_part = train_parts[-1] if train_parts else train
                        new_coach = TrainCoach(last_part.x, last_part.y, train.direction, sphere.value)
                        train_parts.append(new_coach)
                        score += sphere.value
                      
                    # Apply operator effect if any
                    if train.target_station.operator:
                        if train.target_station.operator == ADDITION:
                            plus_count += 1
                            # Detach last two coaches and add their values to score
                            num_detached = detach_last_two_coaches(train_parts, falling_coaches)
                            if num_detached > 0:
                                # Calculate sum of detached coaches' values
                                detached_values = sum(c.sphere_value for c in falling_coaches[-num_detached:])
                                score += detached_values
                        elif train.target_station.operator == SUBTRACTION:
                            minus_count += 1
                            # Detach last two coaches and subtract their values from score
                            num_detached = detach_last_two_coaches(train_parts, falling_coaches)
                            if num_detached > 0:
                                # Calculate sum of detached coaches' values
                                detached_values = sum(c.sphere_value for c in falling_coaches[-num_detached:])
                                score -= detached_values
        
        # Fill with dark blue and draw stars
        screen.fill((20, 20, 50))
        draw_stars(screen)
      
        # Display timer first (so it's always visible)
        display_timer(time_left, screen)
      
        # Draw the map (stations, connections, and path)
        game_map.draw(screen)
      
        # Draw train parts
        if train_parts:
            # Update coach positions to follow the engine
            for i, part in enumerate(train_parts):
                if i == 0:  # Engine
                    part.x = train.x
                    part.y = train.y
                else:  # Coaches follow the previous part
                    prev_part = train_parts[i-1]
                  
                    # Calculate angle towards the previous part
                    angle = math.atan2(prev_part.y - part.y, prev_part.x - part.x)
                  
                    # Move the coach closer to the previous part
                    part.x = prev_part.x - math.cos(angle) * (part.width + 5)
                    part.y = prev_part.y - math.sin(angle) * (part.width + 5)
                  
                part.draw(screen)
      
        # Update and draw falling coaches
        for coach in falling_coaches[:]:
            if coach.update_falling():
                falling_coaches.remove(coach)
            else:
                coach.draw(screen)
              
        # Draw water
        draw_water(screen, water_animation_offset)
        water_animation_offset += 2
      
        # Display score at the water level
        score_position = (SCREEN_WIDTH // 2, water_level - SCORE_DISPLAY_OFFSET)
        display_score(score, screen, score_position)
        
        # Display instructions in center
        instructions = small_font.render("Hover over a station and press SPACE to navigate there", True, WHITE)
        instructions_rect = instructions.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        screen.blit(instructions, instructions_rect)
       
        pygame.display.update()
        clock.tick(60)
       
        while game_close:
            screen.fill((20, 20, 50))
            draw_stars(screen)
            
            if time_up:
                message("Time's Up! Game Over. Press C-Play Again or Q-Quit", RED)
            else:
                message("Game Over! No valid paths left. Press C-Play Again or Q-Quit", RED)
           
            # Display the final score
            score_position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
            display_score(score, screen, score_position)
           
            # Display the counts of "+" and "-" bubbles
            plus_surface = score_font.render(f"+: {plus_count}", True, PLUS_COLOR)
            minus_surface = score_font.render(f"-: {minus_count}", True, MINUS_COLOR)
           
            plus_rect = plus_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            minus_rect = minus_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
           
            screen.blit(plus_surface, plus_rect)
            screen.blit(minus_surface, minus_rect)
           
            pygame.display.update()
           
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    game_close = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    elif event.key == pygame.K_c:
                        game_loop()
                        return

if __name__ == '__main__':
    try:
        game_loop()
    finally:
        pygame.quit()
        sys.exit()
