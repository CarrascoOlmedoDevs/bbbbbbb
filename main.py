import pygame
import sys
import math # Import math for distance calculation

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
BALL_START_X = SCREEN_WIDTH // 4
BALL_START_Y = SCREEN_HEIGHT // 2

HOLE_RADIUS = 20
HOLE_POS_X = SCREEN_WIDTH * 3 // 4
HOLE_POS_Y = SCREEN_HEIGHT // 2


# --- Game Components ---

class Ball:
    """Represents the game ball."""
    def __init__(self, x, y, radius, color):
        self.x = float(x) # Use float for position for smoother movement
        self.y = float(y)
        self.radius = radius
        self.color = color
        self.velocity = [0.0, 0.0] # [vx, vy] - Use floats
        self.is_moving = False

    def update(self, dt):
        """Update ball state based on velocity and dt."""
        # Position update is handled by PhysicsEngine for now
        pass

    def draw(self, surface):
        """Draw the ball on the surface."""
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

class Hole:
    """Represents the target hole."""
    def __init__(self, x, y, radius, color):
        self.x = float(x)
        self.y = float(y)
        self.radius = radius
        self.color = color

    def draw(self, surface):
        """Draw the hole on the surface."""
        # Draw outer ring (darker color) and inner hole (black)
        outer_color = (max(0, self.color[0]-50), max(0, self.color[1]-50), max(0, self.color[2]-50))
        pygame.draw.circle(surface, outer_color, (int(self.x), int(self.y)), self.radius + 5) # Outer ring
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x), int(self.y)), self.radius) # Inner hole


class Field:
    """Represents the playing field/level."""
    def __init__(self, width, height, color):
        self.width = width
        self.height = height
        self.color = color
        # Placeholder for field properties like friction, obstacles, etc.
        self.friction_factor = 0.99 # How much velocity is kept per second (approx)

    def draw(self, surface):
        """Draw the field background/elements."""
        # The background fill is done by the Renderer, but field could draw obstacles here
        pass


class PhysicsEngine:
    """Handles physics calculations (movement, collisions, friction, etc.)."""
    def __init__(self, field):
        self.field = field
        # Placeholder for physics constants
        self.min_speed_to_stop = 5 # Pixels per second threshold to stop the ball

    def update(self, ball, dt):
        """Apply physics to the ball."""
        if not ball.is_moving:
            return

        # Apply friction (simplified: reduce velocity)
        # A more realistic friction might depend on speed and surface
        friction_multiplier = self.field.friction_factor ** dt # Apply friction based on delta time
        ball.velocity[0] *= friction_multiplier
        ball.velocity[1] *= friction_multiplier

        # Update position based on velocity
        ball.x += ball.velocity[0] * dt
        ball.y += ball.velocity[1] * dt

        # Check if ball has stopped
        speed = math.sqrt(ball.velocity[0]**2 + ball.velocity[1]**2)
        if speed < self.min_speed_to_stop:
            ball.velocity = [0.0, 0.0]
            ball.is_moving = False


class InputHandler:
    """Handles user input."""
    def __init__(self, ball):
        self.ball = ball
        self.is_dragging = False
        self.drag_start_pos = None

    def handle_event(self, event):
        """Process a single pygame event."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left click
                # Check if click is on the ball
                mouse_x, mouse_y = event.pos
                dist_to_ball = math.dist((mouse_x, mouse_y), (self.ball.x, self.ball.y))
                if dist_to_ball <= self.ball.radius and not self.ball.is_moving:
                    self.is_dragging = True
                    self.drag_start_pos = event.pos
                    print("Started dragging") # Debug print

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_dragging: # Left click release
                self.is_dragging = False
                drag_end_pos = event.pos
                print("Stopped dragging") # Debug print
                self.apply_shot(self.drag_start_pos, drag_end_pos)
                self.drag_start_pos = None

    def apply_shot(self, start_pos, end_pos):
        """Calculate and apply velocity based on drag."""
        if start_pos and end_pos:
            # Vector from end to start determines direction
            # Magnitude determines speed
            vec_x = start_pos[0] - end_pos[0]
            vec_y = start_pos[1] - end_pos[1]

            # Apply velocity (scale factor might be needed)
            # Example scaling: 0.5
            speed_factor = 0.5
            self.ball.velocity[0] = vec_x * speed_factor
            self.ball.velocity[1] = vec_y * speed_factor
            self.ball.is_moving = True
            print(f"Applied velocity: {self.ball.velocity}") # Debug print

    def draw_drag_line(self, surface):
        """Draw the line representing the shot direction and power."""
        if self.is_dragging and self.drag_start_pos:
            current_mouse_pos = pygame.mouse.get_pos()
            # Draw line from ball position to current mouse position
            # The direction of the line represents the *opposite* of the shot direction
            pygame.draw.line(surface, BLACK, (int(self.ball.x), int(self.ball.y)), current_mouse_pos, 3)


class Renderer:
    """Handles drawing game objects."""
    def __init__(self, screen, field, ball, hole):
        self.screen = screen
        self.field = field
        self.ball = ball
        self.hole = hole

    def render(self, input_handler):
        """Draw all game elements."""
        # Draw field background
        self.screen.fill(self.field.color)

        # Draw hole
        self.hole.draw(self.screen)

        # Draw ball
        self.ball.draw(self.screen)

        # Draw input elements (like drag line)
        input_handler.draw_drag_line(self.screen)

        # Update the display
        pygame.display.flip()


# --- Game Setup ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mini Golf")
clock = pygame.time.Clock()

# --- Create Game Objects ---
field = Field(SCREEN_WIDTH, SCREEN_HEIGHT, GREEN)
ball = Ball(BALL_START_X, BALL_START_Y, BALL_RADIUS, RED)
hole = Hole(HOLE_POS_X, HOLE_POS_Y, HOLE_RADIUS, BLACK) # Using BLACK for the hole color

physics_engine = PhysicsEngine(field)
input_handler = InputHandler(ball)
renderer = Renderer(screen, field, ball, hole)


# --- Game Loop ---
running = True
while running:
    dt = clock.tick(FPS) / 1000.0 # Delta time in seconds

    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        input_handler.handle_event(event)

    # --- Game State Updates ---
    physics_engine.update(ball, dt)

    # --- Drawing ---
    renderer.render(input_handler)


# --- Quit Pygame ---
pygame.quit()
sys.exit()