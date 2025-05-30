import pygame
import sys
import math # Import math for distance calculation
import pygame.math # Import pygame.math for Vector2

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# --- Colors ---
WHITE = (255, 255, 255)
GREEN = (0, 128, 0) # Field color
RED = (255, 0, 0)   # Ball color
BLACK = (0, 0, 0)   # Hole color

# --- Game Object Initial Positions and Sizes ---
BALL_RADIUS = 15
# Use Vector2 for initial positions
BALL_START_POS = pygame.math.Vector2(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2)

HOLE_RADIUS = 20
HOLE_POS = pygame.math.Vector2(SCREEN_WIDTH * 3 // 4, SCREEN_HEIGHT // 2)

# --- Physics Constants ---
# Friction factor per second. 0.8 means 20% velocity loss per second.
# A value closer to 1 means less friction.
FIELD_FRICTION_FACTOR_PER_SECOND = 0.8
# Threshold below which velocity is considered zero
VELOCITY_STOP_THRESHOLD = 0.1

# --- Game Components ---

class Ball:
    """Represents the game ball."""
    def __init__(self, position, radius, color):
        # Use Vector2 for position and velocity
        self.position = pygame.math.Vector2(position)
        self.radius = radius
        self.color = color
        self.velocity = pygame.math.Vector2(0, 0) # Use Vector2 for velocity
        self.is_moving = False # Flag to indicate if the ball is currently moving significantly

    def update(self, dt):
        """Update ball state. Physics handled by PhysicsEngine."""
        # This method can be used for ball-specific logic later if needed,
        # but physics updates are handled externally for now.
        pass

    def draw(self, surface):
        """Draw the ball on the surface."""
        # Draw using the Vector2 position (converted to int tuple)
        pygame.draw.circle(surface, self.color, (int(self.position.x), int(self.position.y)), self.radius)

class Hole:
    """Represents the target hole."""
    def __init__(self, position, radius, color):
        self.position = pygame.math.Vector2(position)
        self.radius = radius
        self.color = color

    def draw(self, surface):
        """Draw the hole on the surface."""
        # Draw outer ring (dark grey) and inner hole (black)
        outer_color = (50, 50, 50) # Dark grey
        # Draw using the Vector2 position (converted to int tuple)
        pygame.draw.circle(surface, outer_color, (int(self.position.x), int(self.position.y)), self.radius + 5) # Outer ring
        pygame.draw.circle(surface, BLACK, (int(self.position.x), int(self.position.y)), self.radius) # Inner hole

    def is_ball_in_hole(self, ball):
        """Check if the ball is within the hole's radius."""
        distance_sq = (ball.position - self.position).length_squared()
        # Ball is in hole if its center is within the hole's radius
        # A slightly more forgiving check might be needed depending on desired gameplay
        # Let's use a threshold slightly less than hole radius to prevent flickering
        threshold_sq = (self.radius * 0.8)**2 # Adjust threshold as needed
        return distance_sq < threshold_sq


class Field:
    """Represents the playing field/level."""
    def __init__(self, width, height, color):
        self.width = width
        self.height = height
        self.color = color
        # Friction factor per second. 0.8 means 20% velocity loss per second.
        # A value closer to 1 means less friction.
        self.friction_factor_per_second = FIELD_FRICTION_FACTOR_PER_SECOND

    def draw(self, surface):
        """Draw the field background/elements."""
        # The background fill is done by the Renderer, but field could draw obstacles here
        pass


class PhysicsEngine:
    """Handles physics calculations (movement, collisions, friction, etc.)."""
    def __init__(self, field):
        self.field = field
        self.velocity_stop_threshold = VELOCITY_STOP_THRESHOLD

    def update(self, ball, dt):
        """Update physics for the ball."""
        if not ball.is_moving and ball.velocity.magnitude() < self.velocity_stop_threshold:
             # Ball is stopped, no physics update needed
             ball.velocity = pygame.math.Vector2(0, 0) # Ensure velocity is exactly zero
             return

        # Apply friction
        # The friction factor is per second, so we raise it to the power of dt
        friction_per_frame = self.field.friction_factor_per_second ** dt
        ball.velocity *= friction_per_frame

        # Update position based on velocity
        ball.position += ball.velocity * dt

        # Handle boundary collisions
        # Check left boundary
        if ball.position.x - ball.radius < 0:
            ball.position.x = ball.radius # Reposition to boundary
            ball.velocity.x *= -1 # Reverse x velocity

        # Check right boundary
        if ball.position.x + ball.radius > self.field.width:
            ball.position.x = self.field.width - ball.radius # Reposition to boundary
            ball.velocity.x *= -1 # Reverse x velocity

        # Check top boundary
        if ball.position.y - ball.radius < 0:
            ball.position.y = ball.radius # Reposition to boundary
            ball.velocity.y *= -1 # Reverse y velocity

        # Check bottom boundary
        if ball.position.y + ball.radius > self.field.height:
            ball.position.y = self.field.height - ball.radius # Reposition to boundary
            ball.velocity.y *= -1 # Reverse y velocity

        # Check if ball has stopped moving
        if ball.velocity.magnitude() < self.velocity_stop_threshold:
            ball.velocity = pygame.math.Vector2(0, 0)
            ball.is_moving = False
        else:
             ball.is_moving = True # Ensure is_moving is True if velocity is significant


class Renderer:
    """Handles drawing game objects."""
    def __init__(self, screen):
        self.screen = screen

    def render(self, field, ball, hole):
        """Draw all game elements."""
        # Draw field background
        self.screen.fill(field.color)

        # Draw hole
        hole.draw(self.screen)

        # Draw ball
        ball.draw(self.screen)

        # Update the full display Surface to the screen
        pygame.display.flip()

# --- Game State ---
class GameState:
    """Manages the overall game state (playing, menu, game over, etc.)."""
    def __init__(self):
        self.state = "playing" # Possible states: "playing", "won", "lost", "menu"

    def set_state(self, new_state):
        self.state = new_state

    def is_playing(self):
        return self.state == "playing"

    def is_won(self):
        return self.state == "won"

    # Add other state checks as needed

# --- Main Game Function ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Mini Golf")
    clock = pygame.time.Clock()

    # --- Game Objects ---
    field = Field(SCREEN_WIDTH, SCREEN_HEIGHT, GREEN)
    ball = Ball(BALL_START_POS, BALL_RADIUS, RED)
    hole = Hole(HOLE_POS, HOLE_RADIUS, BLACK) # Use BLACK for hole color

    # --- Systems ---
    physics_engine = PhysicsEngine(field)
    renderer = Renderer(screen)
    game_state = GameState() # Initialize game state

    # --- Game Loop ---
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0 # Delta time in seconds

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_state.is_playing() and not ball.is_moving:
                    mouse_pos = pygame.math.Vector2(event.pos)
                    direction_vector = mouse_pos - ball.position

                    # Calculate power based on distance from ball to click
                    # Adjust power_scale and max_initial_speed as needed
                    power_scale = 2.0 # Multiplier for distance to speed
                    max_initial_speed = 500.0 # Max speed in pixels per second

                    distance = direction_vector.magnitude()

                    if distance > 0: # Avoid division by zero if clicked exactly on the ball
                        initial_speed = min(distance * power_scale, max_initial_speed)
                        ball.velocity = direction_vector.normalize() * initial_speed
                        ball.is_moving = True # Set ball to moving state

        # --- Update Game State ---
        if game_state.is_playing():
            physics_engine.update(ball, dt)

            # Check for win condition
            if not ball.is_moving and hole.is_ball_in_hole(ball):
                 game_state.set_state("won")
                 print("You Won!") # Simple win message for now

        # --- Rendering ---
        renderer.render(field, ball, hole)

    pygame.quit()
    sys.exit()

# --- Run the game ---
if __name__ == "__main__":
    main()