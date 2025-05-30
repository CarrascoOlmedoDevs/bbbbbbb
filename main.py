import pygame
import sys
import math # Import math for distance calculation

# --- Placeholders for Game Components ---

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

        # Simple boundary check (optional for now, might be part of field)
        # Prevents ball from leaving screen
        if ball.x < ball.radius:
            ball.x = ball.radius
            ball.velocity[0] *= -0.8 # Bounce with some energy loss
        elif ball.x > self.field.width - ball.radius:
            ball.x = self.field.width - ball.radius
            ball.velocity[0] *= -0.8

        if ball.y < ball.radius:
            ball.y = ball.radius
            ball.velocity[1] *= -0.8
        elif ball.y > self.field.height - ball.radius:
            ball.y = self.field.height - ball.radius
            ball.velocity[1] *= -0.8


        # Check if ball has stopped
        current_speed_sq = ball.velocity[0]**2 + ball.velocity[1]**2
        if current_speed_sq < self.min_speed_to_stop**2:
             ball.velocity = [0.0, 0.0]
             ball.is_moving = False


    def check_hole(self, ball, hole):
        """Check if the ball is in the hole."""
        # Calculate distance between ball center and hole center
        distance = math.dist((ball.x, ball.y), (hole.x, hole.y))

        # Check if distance is less than the hole radius (ball center inside hole)
        # A more realistic check might involve ball radius and velocity
        if distance < hole.radius:
             # Check if ball is moving slow enough to fall in
             speed_sq = ball.velocity[0]**2 + ball.velocity[1]**2
             holed_speed_threshold = 50 # Speed threshold to fall in (pixels/sec)
             if speed_sq < holed_speed_threshold**2:
                 return True
        return False # Return True if ball is in hole

class Renderer:
    """Handles drawing all game elements."""
    def __init__(self, surface):
        self.surface = surface
        self.font = pygame.font.Font(None, 36) # Default font for messages

    def render(self, field, ball, hole, game_state, input_handler):
        """Draw all game objects."""
        # Draw background
        self.surface.fill(field.color)

        # Draw field elements (obstacles etc.)
        field.draw(self.surface)

        # Draw the hole
        hole.draw(self.surface)

        # Draw the ball
        ball.draw(self.surface)

        # Draw aiming line if in aiming state and dragging
        if game_state == "aiming" and input_handler.is_dragging and input_handler.mouse_down_pos:
            mouse_pos = pygame.mouse.get_pos()
            # Draw line from ball position to current mouse position while dragging
            # This visualizes the *drag* vector, the shot will be opposite
            # pygame.draw.line(self.surface, (255, 0, 0), (int(ball.x), int(ball.y)), mouse_pos, 3) # From ball to mouse
            # Draw line from mouse_down_pos to current mouse_pos
            pygame.draw.line(self.surface, (255, 0, 0), input_handler.mouse_down_pos, mouse_pos, 3) # From drag start to current mouse

            # Optional: Draw arrow indicating shot direction/power
            drag_vec = (mouse_pos[0] - input_handler.mouse_down_pos[0], mouse_pos[1] - input_handler.mouse_down_pos[1])
            shot_vec = (-drag_vec[0], -drag_vec[1])
            shot_power = (shot_vec[0]**2 + shot_vec[1]**2)**0.5 * 0.5 # Match power calculation scale
            max_draw_power = 150 # Max length of the drawn shot line
            draw_length = min(shot_power, max_draw_power)

            if draw_length > 0:
                 norm = (shot_vec[0]**2 + shot_vec[1]**2)**0.5
                 if norm > 0:
                     draw_vec_normalized = (shot_vec[0] / norm, shot_vec[1] / norm)
                     end_point = (ball.x + draw_vec_normalized[0] * draw_length,
                                  ball.y + draw_vec_normalized[1] * draw_length)
                     pygame.draw.line(self.surface, (0, 0, 0), (int(ball.x), int(ball.y)), (int(end_point[0]), int(end_point[1])), 5) # Shot direction line

        # Display game state or messages
        if game_state == "aiming":
            message = "Aiming"
        elif game_state == "ball_moving":
            message = "Ball Moving"
        elif game_state == "holed":
            message = "HOLED!"
        else:
            message = game_state # Display other states

        text_surface = self.font.render(message, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(self.surface.get_width() // 2, 30))
        self.surface.blit(text_surface, text_rect)


        # Update the full screen
        pygame.display.flip()

class InputHandler:
    """Handles user input (mouse, keyboard)."""
    def __init__(self):
        self.mouse_down_pos = None
        self.is_dragging = False

    def handle_event(self, event):
        """Process a single Pygame event."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left click
                self.mouse_down_pos = event.pos
                self.is_dragging = True
                # print(f"Mouse down at {self.mouse_down_pos}") # Debug

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1: # Left click
                if self.is_dragging:
                    mouse_up_pos = event.pos
                    # print(f"Mouse up at {mouse_up_pos}") # Debug
                    self.is_dragging = False
                    # Signal a shot attempt with the drag start and end positions
                    return "shot_attempt", self.mouse_down_pos, mouse_up_pos

        return None # No specific action signal


    def update(self):
        """Update input state (e.g., check mouse button held down)."""
        # This method might be used for continuous actions, but for golf shot, events are better.
        # Could check if mouse is currently held down and update drag state if needed.
        pass

# --- Pygame Initialization ---
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pygame Golf Outline")

# Clock for controlling frame rate and delta time
clock = pygame.time.Clock()
FPS = 60 # Frames per second

# --- Game Objects Initialization ---
# Using placeholder positions and colors
field_color = (100, 200, 100) # Green
ball_color = (255, 255, 255) # White
hole_color = (50, 50, 50)   # Dark Grey

field = Field(SCREEN_WIDTH, SCREEN_HEIGHT, field_color)
ball = Ball(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2, 10, ball_color) # Start ball left of center
hole = Hole(SCREEN_WIDTH * 3 // 4, SCREEN_HEIGHT // 2, 15, hole_color) # Hole right of center

physics_engine = PhysicsEngine(field)
renderer = Renderer(screen)
input_handler = InputHandler()

# --- Game State ---
game_state = "aiming" # Possible states: "aiming", "ball_moving", "holed", "out_of_bounds"
shots_taken = 0 # Track number of shots

# --- Main Game Loop ---
running = True
while running:
    # Calculate delta time in seconds
    dt = clock.tick(FPS) / 1000.0

    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Pass events to input handler
        action = input_handler.handle_event(event)

        # Process actions based on game state
        if action and action[0] == "shot_attempt":
            if game_state == "aiming":
                # Calculate shot vector and power
                mouse_down_pos = action[1]
                mouse_up_pos = action[2]

                # Calculate vector from mouse_down_pos to mouse_up_pos
                drag_vector = (mouse_up_pos[0] - mouse_down_pos[0], mouse_up_pos[1] - mouse_down_pos[1])
                # The shot velocity is in the opposite direction of the drag vector
                shot_vector = (-drag_vector[0], -drag_vector[1])

                # Calculate power (e.g., proportional to drag distance)
                # Scale factor determines how sensitive the power is to drag distance
                power_scale = 0.5 # Adjust this to make shots stronger or weaker
                power = (shot_vector[0]**2 + shot_vector[1]**2)**0.5 * power_scale
                max_power = 500 # Limit maximum initial velocity

                if power > 10: # Only shoot if enough power to avoid accidental clicks
                    power = min(power, max_power)

                    # Normalize shot vector and scale by power
                    norm = (shot_vector[0]**2 + shot_vector[1]**2)**0.5
                    if norm > 0:
                        ball.velocity[0] = (shot_vector[0] / norm) * power
                        ball.velocity[1] = (shot_vector[1] / norm) * power
                        game_state = "ball_moving"
                        shots_taken += 1
                        print(f"Shot {shots_taken} with velocity: {ball.velocity}, power: {power}") # Debug
                    else:
                         # If norm is 0, it means mouse_down_pos == mouse_up_pos, no drag
                         pass # Do nothing if no drag

    # --- Game State Update ---
    if game_state == "ball_moving":
        physics_engine.update(ball, dt)
        # ball.update(dt) # Ball update might not be needed if physics engine modifies ball directly

        # Check if ball has stopped after physics update
        if not ball.is_moving:
            # Ball stopped, check if it's in the hole
            if physics_engine.check_hole(ball, hole):
                game_state = "holed"
                print(f"Ball holed in {shots_taken} shots!")
                # TODO: Add logic for next level or game over
            else:
                game_state = "aiming" # Ball stopped, ready for next shot
                print("Ball stopped. Ready for next shot.")

    elif game_state == "holed":
        # Game is won or level complete. Could add a delay or wait for input.
        pass # For now, just stays in this state

    elif game_state == "aiming":
        # The input handler is capturing mouse drag in this state
        pass


    # --- Drawing ---
    # Pass input_handler to renderer to draw the aiming line
    renderer.render(field, ball, hole, game_state, input_handler)

    # --- Update Display ---
    # Handled by renderer.render() -> pygame.display.flip()

# --- Quit Pygame ---
pygame.quit()
sys.exit() # Good practice to exit sys as well