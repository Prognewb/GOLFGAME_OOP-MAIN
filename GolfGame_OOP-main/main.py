import pygame

# import random
import os

from ball import Ball
from button import Button
from hole import Hole
from obstacles import Obstacle

from stickyball import StickyBall  # Import the SpecialBall class

# from slipperyball import SlipperyBall


pygame.init()

# Set window dimensions
width = 800
height = 600

# Get current directory
current_directory = os.getcwd()

# Set image path
image_path = os.path.join(current_directory, "images", "bg.png")


# Reset ball function
def resetball():
    ball.x = width // 2
    ball.y = height // 2
    ball.current_pos = [ball.x, ball.y]
    ball.velocity = [0, 0]
    ball.drag_line = []

    global total_strokes
    total_strokes = 0  # Reset total strokes


# Create screen
screen = pygame.display.set_mode((width, height))

# Load and resize background image
image = pygame.image.load(image_path)
image = pygame.transform.scale(image, (width, height))

# Set window caption
pygame.display.set_caption("2dGolf")

# Create ball object
# ball = Ball(width // 2, height // 2, 20, (255, 255, 255))
ball = StickyBall(
    width  //  2,
    height //  2,
    20,
    (255, 255, 255),
    "Sticky",
    speed_multiplier=10,
)
# ball.set_speed_multiplier(10)


# Create font object
font = pygame.font.Font(None, 30)

# Set running flag
running = True
ball_hit = False
ball_stopped = True
ball_was_hit = False
# Create reset button object
reset_button = Button(10, 10, 100, 50, (0, 255, 0), "Reset", (255, 255, 255))

# Create hole object
hole = Hole(396, 80, 25, (0, 0, 0))

obstacles = [
    Obstacle(130, 290, 50, 100, (0, 0, 0)),  # Example red obstacle
    Obstacle(400, 400, 20, 100, (0, 0, 0), orientation="horizontal")
    # Add more obstacles here as needed
]
# Initialize hole message and success message
hole_message = ""
success_message = ""
total_strokes = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
        # this happens when you click the ball and drag it
            if (
                ball.velocity[0] ** 2 + ball.velocity[1] ** 2 < 1
                and ball.dragging is False
                and (ball.current_pos[0] - event.pos[0]) ** 2
                + (ball.current_pos[1] - event.pos[1]) ** 2
                <= ball.radius**2
            ):
                ball.dragging = True

                ball.drag_line = [ball.current_pos]
                ball_was_hit = True

            reset_button.handle_click(pygame.mouse.get_pos(), reset_ball=resetball)

        elif event.type == pygame.MOUSEBUTTONUP:
            if (
                ball.dragging
                and ball.velocity[0] ** 2 + ball.velocity[1] ** 2 < 0.01**2
                and (ball.current_pos[0] - event.pos[0]) ** 2
                + (ball.current_pos[1] - event.pos[1]) ** 2
                > ball.radius**2
            ):
                ball.handle_release(pygame.mouse.get_pos())
            ball.dragging = False

            if (
                ball_was_hit and ball.drag_line
            ):  # Only increment if ball was hit and dragging line is present
                total_strokes += 1
                ball_was_hit = False  # Reset flag

    if ball.dragging:
        ball.drag_line.append(pygame.mouse.get_pos())

    if ball.velocity != [0, 0]:
        ball.dragging = False
        ball.drag_line = []

    if ball.drag_line:
        for start, end in zip(ball.drag_line, ball.drag_line[1:]):
            pygame.draw.line(screen, (0, 0, 0), start, end, 5)

    screen.blit(image, (0, 0))

    # Update ball's position and check for collisions

    ball.update_position(screen=screen, width=width, height=height)
    for obstacle in obstacles:
        if (
            ball.current_pos[0] + ball.radius >= obstacle.x
            and ball.current_pos[0] - ball.radius <= obstacle.x + obstacle.width
            and ball.current_pos[1] + ball.radius >= obstacle.y
            and ball.current_pos[1] - ball.radius <= obstacle.y + obstacle.height
        ):
            # Adjust x position based on collision with obstacle's x edges
            # Adjust y position based on collision with obstacle's y edges
            ball.adjust_position(obstacle)

            # Reverse velocity components based on the collision
            ball.reverse_velocity(obstacle)

            # Additional checks for corners
            ball.handle_corner_collisions(obstacle)

            if hasattr(ball, 'special_attribute') and ball.special_attribute == "Sticky":
                ball.handle_collision(screen_width=width, screen_height=height, obstacles=obstacles)

    distance_to_hole = (
        (ball.current_pos[0] - hole.x) ** 2 + (ball.current_pos[1] - hole.y) ** 2
    ) ** 0.5

    if distance_to_hole <= hole.radius:
        if distance_to_hole + ball.radius <= hole.radius:
            hole_message = "Ball in hole!"
            # ball.special_method()
            success_message = "Congrats!"
            ball.velocity = [0, 0]
        else:
            hole_message = "Ball partly in hole!"
    else:
        hole_message = ""
        success_message = ""

    hole.draw(screen)
    ball.draw(screen)
    reset_button.draw(screen)

    for obstacle in obstacles:
        obstacle.draw(screen,  20, 100, pygame=pygame)

    hole_text = font.render(hole_message, True, (255, 255, 255))
    hole_text_rect = hole_text.get_rect(bottomleft=(10, height - 10))
    screen.blit(hole_text, hole_text_rect)

    success_text = font.render(success_message, True, (255, 0, 0))
    success_text_rect = success_text.get_rect(centerx=width // 2, bottom=height - 10)
    screen.blit(success_text, success_text_rect)

    # Display stroke counter
    total_strokes_text = font.render(
        f"Total Strokes: {total_strokes}", True, (255, 255, 255)
    )
    total_strokes_text_rect = total_strokes_text.get_rect(topright=(width - 10, 10))
    screen.blit(total_strokes_text, total_strokes_text_rect)

    mouse_pos_text = font.render(
        f"Mouse Position: {pygame.mouse.get_pos()}", True, (255, 255, 255)
    )
    mouse_pos_rect = mouse_pos_text.get_rect(bottomleft=(10, height - 40))
    screen.blit(mouse_pos_text, mouse_pos_rect)

    velocity_text = font.render(f"Velocity: {ball.velocity}", True, (255, 255, 255))
    velocity_text_rect = velocity_text.get_rect(bottomright=(width - 10, height - 10))
    screen.blit(velocity_text, velocity_text_rect)

    pygame.display.flip()

pygame.quit()
