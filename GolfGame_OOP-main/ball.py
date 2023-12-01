import pygame


class Ball:
    def __init__(self, x: int, y: int, radius: int, color: tuple):
        # self is equivalent to this in java, so self.x = this.x
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.velocity = [0, 0]
        self.current_pos = [x, y]
        self.dragging = False
        self.drag_line = []

    def draw(self, screen):
        pygame.draw.circle(
            screen,
            self.color,
            (int(self.current_pos[0]), int(self.current_pos[1])),
            self.radius,
        )

    def handle_release(self, mouse_pos):
        if self.dragging and (self.velocity[0] ** 2 + self.velocity[1] ** 2 < 1):
            # Add current ball position to drag_line list
            self.drag_line.append(self.current_pos)

            # Calculate the distance and direction of the mouse drag
            drag_distance = (
                (self.current_pos[0] - mouse_pos[0]) ** 2
                + (self.current_pos[1] - mouse_pos[1]) ** 2
            ) ** 0.5

            drag_direction = [
                self.current_pos[0] - mouse_pos[0],
                self.current_pos[1] - mouse_pos[1],
            ]

            # Check if drag_distance is not zero
            if drag_distance != 0:
                # Normalize the direction vector
                drag_direction = [i / drag_distance for i in drag_direction]
                # Make the velocity proportional to the drag distance and in the direction of the drag
                self.velocity = [i * drag_distance * 0.2 for i in drag_direction]
            else:
                self.velocity = [0, 0]

            self.dragging = False

    def update_position(self, screen, width, height):
        if self.dragging:
            if not self.drag_line:
                self.drag_line.append(self.current_pos)

            if self.drag_line:
                pygame.draw.line(
                    screen, (0, 0, 0), self.drag_line[0], pygame.mouse.get_pos(), 5
                )

        self.current_pos[0] += self.velocity[0] * 0.08  # Apply x velocity every frame
        self.current_pos[1] += self.velocity[1] * 0.08  # Apply y velocity every frame
        self.velocity[0] *= 0.99  # Slow down x velocity over time
        self.velocity[1] *= 0.99  # Slow down y velocity over time

        if self.velocity[0] ** 2 + self.velocity[1] ** 2 < 0.01:
            self.velocity = [0, 0]

        # Check collision with window edges
        if self.current_pos[0] - self.radius <= 0:
            self.current_pos[0] = self.radius  # Keep the ball within the left edge
            self.velocity[0] *= -1  # Reverse x velocity
        elif self.current_pos[0] + self.radius >= width:
            self.current_pos[0] = (
                width - self.radius
            )  # Keep the ball within the right edge
            self.velocity[0] *= -1  # Reverse x velocity

        if self.current_pos[1] - self.radius <= 0:
            self.current_pos[1] = self.radius  # Keep the ball within the top edge
            self.velocity[1] *= -1  # Reverse y velocity
        elif self.current_pos[1] + self.radius >= height:
            self.current_pos[1] = (
                height - self.radius
            )  # Keep the ball within the bottom edge
            self.velocity[1] *= -1  # Reverse y velocity

    def adjust_position(self, obstacle):
        if obstacle.orientation == "vertical":
            # Adjust x position based on collision with obstacle's x edges
            if self.current_pos[0] < obstacle.x:
                self.current_pos[0] = obstacle.x - self.radius
            elif self.current_pos[0] > obstacle.x + obstacle.width:
                self.current_pos[0] = obstacle.x + obstacle.width + self.radius

            # Adjust y position based on collision with obstacle's y edges
            if self.current_pos[1] < obstacle.y:
                self.current_pos[1] = obstacle.y - self.radius
            elif self.current_pos[1] > obstacle.y + obstacle.height:
                self.current_pos[1] = obstacle.y + obstacle.height + self.radius

    def reverse_velocity(self, obstacle):
        if obstacle.orientation == "vertical":
            # Reverse velocity components based on the collision
            if self.current_pos[0] == obstacle.x - self.radius or self.current_pos[0] == obstacle.x + obstacle.width + self.radius:
                self.velocity[0] *= -1  # Reverse x velocity
            if self.current_pos[1] == obstacle.y - self.radius or self.current_pos[1] == obstacle.y + obstacle.height + self.radius:
                self.velocity[1] *= -1  # Reverse y velocity
        elif obstacle.orientation == "horizontal":
            # Reverse velocity components based on the collision
            if obstacle.y - self.radius <= self.current_pos[1] <= obstacle.y + obstacle.height + self.radius:
                self.velocity[1] *= -1  # Reverse y velocity

    def handle_corner_collisions(self, obstacle):
        # Additional checks for corners
        if (self.current_pos[0] - obstacle.x) ** 2 + (self.current_pos[1] - obstacle.y) ** 2 <= self.radius ** 2:
            # Ball collided with top-left corner, handle as needed
            self.velocity[0] *= -1  # Reverse only x velocity
            self.velocity[1] *= 1 # Maintain y velocity

        elif (self.current_pos[0] - (obstacle.x + obstacle.width)) ** 2 + (self.current_pos[1] - obstacle.y) ** 2 <= self.radius ** 2:
            # Ball collided with top-right corner, handle as needed
            self.velocity[0] *= -1  # Reverse only x velocity
            self.velocity[1] *= 1  # Maintain y velocity

        elif (self.current_pos[0] - obstacle.x) ** 2 + (self.current_pos[1] - (obstacle.y + obstacle.height)) ** 2 <= self.radius ** 2:
            # Ball collided with bottom-left corner, handle as needed
            self.velocity[0] *= -1  # Reverse only x velocity
            self.velocity[1] *= -1  # Maintain y velocity with opposite sign

        elif (self.current_pos[0] - (obstacle.x + obstacle.width)) ** 2 + (self.current_pos[1] - (obstacle.y + obstacle.height)) ** 2 <= self.radius ** 2:
            # Ball collided with bottom-right corner, handle as needed
            self.velocity[0] *= -1  # Reverse only x velocity
            self.velocity[1] *= -1  # Maintain y velocity with opposite sign