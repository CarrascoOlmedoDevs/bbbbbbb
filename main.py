import pygame
import sys
import math
import pygame.math

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
        # Add a small tolerance or check against radius difference for more realistic "falling in"
        # For now, simple radius check:
        return distance < self.radius

class PhysicsEngine:
    """Handles physics updates for game objects."""
    def __init__(self, field_rect, friction_factor_per_second, velocity_stop_threshold, bounce_damping):
        self.field_rect = field_rect
        self.friction_factor = friction_factor_per_second
        self.stop_threshold = velocity_stop_threshold
        self.bounce_damping = bounce_damping

    def update(self, ball, dt):
        """Updates the ball's position and velocity based on physics."""
        # Stop ball if velocity is below threshold
        if ball.velocity.length() < self.stop_threshold and ball.is_moving:
             ball.velocity = pygame.math.Vector2(0, 0)
             ball.is_moving = False

        if ball.is_moving:
            # Apply friction
            # Calculate friction factor adjusted for delta time
            friction_factor_dt = self.friction_factor ** dt
            ball.velocity *= friction_factor_dt

            # Update position
            ball.position += ball.velocity * dt

            # Handle boundary collisions
            collided = False
            # Check right boundary
            if ball.position.x + ball.radius > self.field_rect.right:
                ball.position.x = self.field_rect.right - ball.radius
                ball.velocity.x *= -self.bounce_damping # Reverse and dampen velocity
                collided = True
            # Check left boundary
            elif ball.position.x - ball.radius < self.field_rect.left:
                ball.position.x = self.field_rect.left + ball.radius
                ball.velocity.x *= -self.bounce_damping
                collided = True
            # Check bottom boundary
            if ball.position.y + ball.radius > self.field_rect.bottom:
                ball.position.y = self.field_rect.bottom - ball.radius
                ball.velocity.y *= -self.bounce_damping
                collided = True
            # Check top boundary
            elif ball.position.y - ball.radius < self.field_rect.top:
                ball.position.y = self.field_rect.top + ball.radius
                ball.velocity.y *= -self.bounce_damping
                collided = True

            # If a collision occurred, re-check if velocity is now below threshold
            # This prevents the ball from bouncing forever with tiny velocities
            if collided and ball.velocity.length() < self.stop_threshold:
                 ball.velocity = pygame.math.Vector2(0, 0)
                 ball.is_moving = False


# --- Game Setup ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mini Golf")
clock = pygame.time.Clock()

# --- Game State Variables ---
game_state = 'playing' # Possible states: 'playing', 'hole_completed'
shot_count = 0

# --- Game Objects ---
ball = Ball(BALL_START_POS, BALL_RADIUS, RED)
hole = Hole(HOLE_POS, HOLE_RADIUS, BLACK)

# --- Physics Engine Instance ---
physics_engine = PhysicsEngine(FIELD_RECT, FIELD_FRICTION_FACTOR_PER_SECOND, VELOCITY_STOP_THRESHOLD, BOUNCE_DAMPING)

# --- Font for UI ---
font = pygame.font.Font(None, 36) # Default font, size 36

# --- Game Loop ---
running = True
is_pulling = False # Flag to indicate if the player is currently pulling the ball
pull_start_pos = pygame.math.Vector2(0, 0) # Position where pull started

while running:
    dt = clock.tick(FPS) / 1000.0 # Delta time in seconds

    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left mouse button
                # Allow pulling only if in 'playing' state and ball is not moving
                if game_state == 'playing' and not ball.is_moving:
                    mouse_pos = pygame.math.Vector2(event.pos)
                    # Check if click is on the ball (within a certain radius)
                    if (mouse_pos - ball.position).length() < ball.radius + 10: # Add tolerance for easier clicking
                        is_pulling = True
                        pull_start_pos = mouse_pos

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1: # Left mouse button
                if is_pulling:
                    is_pulling = False
                    # Calculate launch vector (opposite of pull vector)
                    current_mouse_pos = pygame.math.Vector2(event.pos)
                    pull_vector = current_mouse_pos - pull_start_pos
                    # Apply a force/velocity based on the pull vector
                    # Need to tune a force_factor or velocity_multiplier
                    FORCE_FACTOR = 5 # Example value, adjust as needed
                    ball.velocity = -pull_vector * FORCE_FACTOR
                    ball.is_moving = True # Ball is now moving
                    shot_count += 1 # Increment shot count

        # Basic key press handling (e.g., restart)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r: # Press 'R' to restart
                game_state = 'playing'
                shot_count = 0
                ball.position = pygame.math.Vector2(BALL_START_POS)
                ball.velocity = pygame.math.Vector2(0, 0)
                ball.is_moving = False
                is_pulling = False # Ensure not pulling after restart


    # --- Game Logic ---

    # Update physics only if the ball is moving
    if ball.is_moving:
        physics_engine.update(ball, dt)

    # Check for ball in hole ONLY if ball is not moving (or moving very slowly)
    # and game state is 'playing'
    if game_state == 'playing' and not ball.is_moving:
         if hole.is_ball_in_hole(ball):
             game_state = 'hole_completed'
             # Snap ball to hole center and stop movement completely
             ball.position = pygame.math.Vector2(hole.position)
             ball.velocity = pygame.math.Vector2(0, 0)
             ball.is_moving = False


    # --- Drawing ---
    screen.fill(GREEN) # Fill background with field color

    hole.draw(screen)
    ball.draw(screen)

    # Draw pull line if pulling
    if is_pulling:
        current_mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos())
        # Draw line from ball to current mouse position
        pygame.draw.line(screen, BLACK, ball.position, current_mouse_pos, 3)
        # Could add arrow head here for direction

    # Draw UI elements
    # Draw shot count
    shot_text_surface = font.render(f"Shots: {shot_count}", True, BLACK)
    screen.blit(shot_text_surface, (10, 10))

    # Draw game state message if applicable
    if game_state == 'hole_completed':
        win_text_surface = font.render("Hole Completed!", True, BLACK)
        text_rect = win_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(win_text_surface, text_rect)
        # Optional: Display final score/shots here too

    # --- Update Display ---
    pygame.display.flip()

# --- Quit Pygame ---
pygame.quit()
sys.exit()