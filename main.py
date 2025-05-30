import pygame
import sys
import math # Import math for distance calculation
import pygame.math # Import pygame.math for Vector2

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Define the playable area (screen bounds)
FIELD_RECT = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

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
# Damping factor for bounces off boundaries (e.g., 0.7 means 30% energy loss)
BOUNCE_DAMPING = 0.7

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
        """Check if the ball's center is within the hole's radius."""
        distance = (ball.position - self.position).length()
        # Check if distance is less than the hole radius
        return distance < self.radius

class PhysicsEngine:
    """Handles physics calculations for game objects."""
    def __init__(self, friction_factor_per_second, velocity_stop_threshold):
        self.friction_factor_per_second = friction_factor_per_second
        self.velocity_stop_threshold = velocity_stop_threshold

    def update_ball(self, ball, dt):
        """Applies physics (like friction) to the ball."""
        if ball.is_moving:
            # Apply friction: velocity decreases exponentially
            # friction_factor_per_frame = self.friction_factor_per_second ** dt
            # A simpler linear approximation for small dt: velocity *= (1 - friction_rate * dt)
            # Let's use the exponential decay which is more accurate
            friction_factor_per_frame = self.friction_factor_per_second ** dt
            ball.velocity *= friction_factor_per_frame

            # Update position based on velocity
            ball.position += ball.velocity * dt

            # Check if velocity is below threshold to stop movement
            if ball.velocity.length() < self.velocity_stop_threshold:
                ball.velocity = pygame.math.Vector2(0, 0)
                ball.is_moving = False
        else:
            # If not moving, ensure velocity is zero
            ball.velocity = pygame.math.Vector2(0, 0)

    # Add methods for applying forces, handling collisions, etc. here later

# --- Initialization ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Simple Golf Game")
clock = pygame.time.Clock()

# Create game objects
ball = Ball(BALL_START_POS, BALL_RADIUS, RED)
hole = Hole(HOLE_POS, HOLE_RADIUS, BLACK)

# Create physics engine instance
physics_engine = PhysicsEngine(FIELD_FRICTION_FACTOR_PER_SECOND, VELOCITY_STOP_THRESHOLD)

# --- Game State ---
# Could use a more complex state machine, but a simple flag works for now
ball_in_hole = False

# --- Game Loop ---
running = True
while running:
    dt = clock.tick(FPS) / 1000.0 # Delta time in seconds

    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Basic input: Click to apply a force (for testing movement)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and not ball.is_moving and not ball_in_hole: # Left click, ball not moving, not in hole
                 # Calculate direction vector from ball to mouse click
                 mouse_pos = pygame.math.Vector2(event.pos)
                 direction = mouse_pos - ball.position
                 # Apply a force (e.g., proportional to distance, capped)
                 force_magnitude = min(direction.length() * 50, 1000) # Example force calculation
                 if direction.length() > 0:
                     # Apply force as an instant velocity change for simplicity here
                     # In a real simulation, apply force over time (F=ma)
                     ball.velocity = direction.normalize() * force_magnitude
                     ball.is_moving = True
                     print(f"Applied velocity: {ball.velocity.length():.2f}")


    # --- Game Logic ---

    if not ball_in_hole: # Only update ball if not in hole
        # Update ball physics (friction, velocity, position)
        physics_engine.update_ball(ball, dt)

        # --- Collision Detection and Response ---

        # 1. Ball vs Field Boundaries
        # Check for collision and reflect velocity with damping
        if ball.position.x - ball.radius < FIELD_RECT.left:
            ball.position.x = FIELD_RECT.left + ball.radius # Correct position
            ball.velocity.x *= -BOUNCE_DAMPING              # Reflect and dampen
            # Ensure ball is marked as moving if it bounces
            if ball.velocity.length() > VELOCITY_STOP_THRESHOLD:
                 ball.is_moving = True

        elif ball.position.x + ball.radius > FIELD_RECT.right:
            ball.position.x = FIELD_RECT.right - ball.radius # Correct position
            ball.velocity.x *= -BOUNCE_DAMPING               # Reflect and dampen
            if ball.velocity.length() > VELOCITY_STOP_THRESHOLD:
                 ball.is_moving = True

        if ball.position.y - ball.radius < FIELD_RECT.top:
            ball.position.y = FIELD_RECT.top + ball.radius   # Correct position
            ball.velocity.y *= -BOUNCE_DAMPING               # Reflect and dampen
            if ball.velocity.length() > VELOCITY_STOP_THRESHOLD:
                 ball.is_moving = True

        elif ball.position.y + ball.radius > FIELD_RECT.bottom:
            ball.position.y = FIELD_RECT.bottom - ball.radius # Correct position
            ball.velocity.y *= -BOUNCE_DAMPING                # Reflect and dampen
            if ball.velocity.length() > VELOCITY_STOP_THRESHOLD:
                 ball.is_moving = True


        # 2. Ball vs Hole
        # Check if ball is within hole radius AND slow enough to fall in
        # Use a slightly higher threshold for falling in than the stop threshold
        HOLE_SINK_VELOCITY_THRESHOLD = VELOCITY_STOP_THRESHOLD * 4 # Example: 4 times the stop threshold
        if hole.is_ball_in_hole(ball) and ball.velocity.length() < HOLE_SINK_VELOCITY_THRESHOLD:
            ball.position = pygame.math.Vector2(hole.position) # Snap to hole center
            ball.velocity = pygame.math.Vector2(0, 0) # Stop the ball
            ball.is_moving = False
            ball_in_hole = True # Mark ball as in hole
            print("Ball in hole!") # Basic feedback

    # --- Drawing ---
    screen.fill(GREEN) # Fill background with field color

    hole.draw(screen) # Draw the hole
    ball.draw(screen) # Draw the ball

    # --- Update Display ---
    pygame.display.flip()

# --- Quit Pygame ---
pygame.quit()
sys.exit()