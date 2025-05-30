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
        # Draw outer ring (darker color) and inner hole (black)
        outer_color = (max(0, self.color[0]-50), max(0, self.color[1]-50), max(0, self.color[2]-50))
        # Draw using the Vector2 position (converted to int tuple)
        pygame.draw.circle(surface, outer_color, (int(self.position.x), int(self.position.y)), self.radius + 5) # Outer ring
        pygame.draw.circle(surface, (0, 0, 0), (int(self.position.x), int(self.position.y)), self.radius) # Inner hole


class Field:
    """Represents the playing field/level."""
    def __init__(self, width, height, color):
        self.width = width
        self.height = height
        self.color = color
        # Friction factor per second. 0.8 means 20% velocity loss per second.
        # A value closer to 1 means less friction.
        self.friction_factor_per_second = 0.8

    def draw(self, surface):
        """Draw the field background/elements."""
        # The background fill is done by the Renderer, but field could draw obstacles here
        pass


class PhysicsEngine:
    """Handles physics calculations (movement, collisions, friction, etc.)."""
    def __init__(self, field):
        self.field = field
        # Minimum speed squared to stop the ball (pixels/second)^2
        # Using squared value avoids sqrt calculation for comparison
        self.min_speed_sq_to_stop = 20 # Adjust this value as needed (e.g., 5 pixels/sec -> 25)

    def update(self, ball, dt):
        """Apply physics to the ball."""

        # Check if ball is considered moving based on velocity threshold
        if ball.velocity.length_squared() < self.min_speed_sq_to_stop:
            # If velocity is below threshold, stop the ball completely
            ball.velocity = pygame.math.Vector2(0, 0)
            ball.is_moving = False
            return # Ball stopped, no further physics needed this frame

        # If ball has significant velocity, mark it as moving
        ball.is_moving = True

        # Apply friction
        # Calculate the multiplier for this time step (dt seconds)
        # velocity_after_dt = velocity_before_dt * (friction_factor_per_second ** dt)
        friction_multiplier = self.field.friction_factor_per_second ** dt
        ball.velocity *= friction_multiplier

        # Update position based on velocity and time delta
        ball.position += ball.velocity * dt

        # Basic boundary checking (optional for now, but good practice)
        # if ball.position.x < ball.radius: ball.position.x = ball.radius; ball.velocity.x *= -0.5 # Bounce
        # if ball.position.x > SCREEN_WIDTH - ball.radius: ball.position.x = SCREEN_WIDTH - ball.radius; ball.velocity.x *= -0.5
        # if ball.position.y < ball.radius: ball.position.y = ball.radius; ball.velocity.y *= -0.5
        # if ball.position.y > SCREEN_HEIGHT - ball.radius: ball.position.y = SCREEN_HEIGHT - ball.radius; ball.velocity.y *= -0.5


class Renderer:
    """Handles drawing game objects."""
    def __init__(self, screen):
        self.screen = screen

    def render(self, field, ball, hole):
        """Draw all game objects."""
        # Draw field background
        self.screen.fill(field.color)

        # Draw hole
        hole.draw(self.screen)

        # Draw ball
        ball.draw(self.screen)

        # Update the full display Surface to the screen
        pygame.display.flip()


# --- Game Manager / Main Loop ---

class GameManager:
    """Manages the game state and main loop."""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Simple Golf Game")
        self.clock = pygame.time.Clock()

        # --- Game Objects ---
        self.field = Field(SCREEN_WIDTH, SCREEN_HEIGHT, GREEN)
        # Create ball and hole using Vector2 positions
        self.ball = Ball(BALL_START_POS, BALL_RADIUS, RED)
        self.hole = Hole(HOLE_POS, HOLE_RADIUS, BLACK) # Using BLACK for the hole color

        # --- Game Systems ---
        self.physics_engine = PhysicsEngine(self.field)
        self.renderer = Renderer(self.screen)

        # --- Game State ---
        self.game_state = "AIMING" # Possible states: "AIMING", "BALL_MOVING", "BALL_IN_HOLE"
        self.aim_start_pos = None # Position where mouse click started for aiming
        self.aim_end_pos = None   # Current mouse position while aiming

    def handle_input(self):
        """Handles user input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False # Signal to quit the game

            if self.game_state == "AIMING":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # Left click
                        # Store start position as a Vector2
                        self.aim_start_pos = pygame.math.Vector2(event.pos)
                        self.aim_end_pos = pygame.math.Vector2(event.pos) # Start drawing line immediately
                elif event.type == pygame.MOUSEMOTION:
                    if self.aim_start_pos is not None:
                        # Update end position as a Vector2
                        self.aim_end_pos = pygame.math.Vector2(event.pos)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and self.aim_start_pos is not None:
                        # Calculate velocity vector from start to end position
                        # The vector points from where the mouse is released back to where it was pressed
                        aim_vector = self.aim_start_pos - self.aim_end_pos
                        # Apply a scaling factor to control power
                        power_scale = 5 # Adjust this value to control how hard the ball is hit
                        self.ball.velocity = aim_vector * power_scale
                        # The physics engine will set is_moving based on velocity magnitude
                        # self.ball.is_moving = True # Physics engine handles this based on velocity
                        self.game_state = "BALL_MOVING"
                        self.aim_start_pos = None
                        self.aim_end_pos = None
            # Add input handling for other states if needed

        return True # Signal to continue the game

    def update(self, dt):
        """Updates game state."""
        if self.game_state == "BALL_MOVING":
            self.physics_engine.update(self.ball, dt)

            # Check if ball stopped moving (physics engine sets ball.is_moving)
            if not self.ball.is_moving:
                 print("Ball stopped. Transitioning to AIMING.") # Debug print
                 self.game_state = "AIMING" # Transition back to aiming state

            # Check if ball is in the hole (simple distance check)
            distance_to_hole = self.ball.position.distance_to(self.hole.position)
            # Ball is in hole if distance is less than hole radius minus ball radius (approx)
            # Add a small tolerance
            if distance_to_hole < self.hole.radius - self.ball.radius * 0.5: # Tolerance added
                 print("Ball in hole! Transitioning to BALL_IN_HOLE.") # Debug print
                 self.game_state = "BALL_IN_HOLE" # Or transition to game over/next level

        # Add update logic for other states if needed
        elif self.game_state == "BALL_IN_HOLE":
            # Maybe show a message, wait for input to restart, etc.
            pass # For now, just stay in this state


    def render(self):
        """Renders the game."""
        self.renderer.render(self.field, self.ball, self.hole)

        # Draw aiming line if in AIMING state and mouse is clicked
        if self.game_state == "AIMING" and self.aim_start_pos is not None and self.aim_end_pos is not None:
            # Draw line from ball position towards the opposite direction of the aim vector
            # The line represents the direction and magnitude of the shot
            aim_vector = self.aim_start_pos - self.aim_end_pos
            line_end_pos = self.ball.position + aim_vector # Draw line indicating shot direction/power
            # Limit the line length if it gets too long
            max_aim_length = 200 # Pixels
            if aim_vector.length() > max_aim_length:
                 aim_vector.scale_to_length(max_aim_length)
                 line_end_pos = self.ball.position + aim_vector

            # Draw the line from the ball's current position
            pygame.draw.line(self.screen, BLACK, (int(self.ball.position.x), int(self.ball.position.y)), (int(line_end_pos.x), int(line_end_pos.y)), 3)


    def run(self):
        """Main game loop."""
        running = True
        while running:
            # Calculate delta time in seconds
            dt = self.clock.tick(FPS) / 1000.0

            running = self.handle_input()
            if not running:
                break

            self.update(dt)
            self.render()

        pygame.quit()
        sys.exit()

# --- Entry Point ---
if __name__ == "__main__":