import pygame
import math

class Ball:
    def __init__(self, x: int, y: int, radius: int, color: tuple):
        # self is equivalent to this in java, so self.x = this.x
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed = [0, 0]
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
        if self.dragging and (self.speed[0] ** 2 + self.speed[1] ** 2 < 1):
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
                # Make the speed proportional to the drag distance and in the direction of the drag
                self.speed = [i * drag_distance * 0.2 for i in drag_direction]
            else:
                self.speed = [0, 0]

            self.dragging = False

    def update_position(self, screen, width, height):
        if self.dragging:
            if not self.drag_line:
                self.drag_line.append(self.current_pos)

            if self.drag_line:
                pygame.draw.line(
                    screen, (0, 0, 0), self.drag_line[0], pygame.mouse.get_pos(), 5
                )

        self.current_pos[0] += self.speed[0] * 0.08  # Apply x speed every frame
        self.current_pos[1] += self.speed[1] * 0.08  # Apply y speed every frame
        self.speed[0] *= 0.99  # Slow down x speed over time
        self.speed[1] *= 0.99  # Slow down y speed over time

        if self.speed[0] ** 2 + self.speed[1] ** 2 < 0.01:
            self.speed = [0, 0]

        # Check collision with window edges
        if self.current_pos[0] - self.radius <= 0:
            self.current_pos[0] = self.radius  # Keep the ball within the left edge
            self.speed[0] *= -1  # Reverse x speed
        elif self.current_pos[0] + self.radius >= width:
            self.current_pos[0] = (
                width - self.radius
            )  # Keep the ball within the right edge
            self.speed[0] *= -1  # Reverse x speed

        if self.current_pos[1] - self.radius <= 0:
            self.current_pos[1] = self.radius  # Keep the ball within the top edge
            self.speed[1] *= -1  # Reverse y speed
        elif self.current_pos[1] + self.radius >= height:
            self.current_pos[1] = (
                height - self.radius
            )  # Keep the ball within the bottom edge
            self.speed[1] *= -1  # Reverse y speed

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
        elif obstacle.orientation == "horizontal":
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

    def reverse_speed(self, obstacle):
        # Reverse speed components based on the collision
        if self.current_pos[0] == obstacle.x - self.radius or self.current_pos[0] == obstacle.x + obstacle.width + self.radius:
            self.speed[0] *= -1  # Reverse x speed
        if self.current_pos[1] == obstacle.y - self.radius or self.current_pos[1] == obstacle.y + obstacle.height + self.radius:
            self.speed[1] *= -1  # Reverse y speed

    def is_aabb_collision(self, obstacle):
        # Axis Aligned Bounding Box
        x_collision = (math.fabs(self.current_pos[0] - obstacle.x) * 2) < (self.radius + obstacle.width)
        y_collision = (math.fabs(self.current_pos[1] - obstacle.y) * 2) < (self.radius + obstacle.height)
        return (x_collision and y_collision)

    def handle_collision(self, screen_width, screen_height, obstacles):
        # Check for collisions with obstacles
        for obstacle in obstacles:
            if self.is_aabb_collision(obstacle):
                # Handle collision based on the obstacle's orientation
                self.adjust_position(obstacle)
                self.reverse_speed(obstacle)

        # Check for collisions with window edges
        self.update_position(screen_width, screen_height)

    def handle_collision_with_corner(self, corner_pos):
        x0, y0 = self.current_pos[0], self.current_pos[1]
        dx, dy = self.speed[0], self.speed[1]
        r = self.radius

        a = dx**2 + dy**2
        b = 2 * (x0 * dx + y0 * dy)
        c = x0**2 + y0**2 - r**2

        D = b**2 - 4 * a * c

        if D >= 0:
            t = (-b - math.sqrt(D)) / (2 * a)

            if 0 < t <= 1:
                self.current_pos[0] += t * self.speed[0]
                self.current_pos[1] += t * self.speed[1]

                ts = 1 - t

                x, y = self.current_pos[0] - corner_pos[0], self.current_pos[1] - corner_pos[1]
                c = -2 * (self.speed[0] * x + self.speed[1] * y) / (x**2 + y**2)
                self.speed[0] += c * x
                self.speed[1] += c * y

    def check_collision_with_obstacle(self, obstacle):
        # Check for AABB collision
        if self.is_aabb_collision(obstacle):
            # Check for corner collision
            corner_positions = obstacle.calculate_corner_positions()
            for corner_pos in corner_positions:
                if self.is_point_inside_circle(corner_pos[0], corner_pos[1]):
                    # Handle collision with corner
                    self.handle_collision_with_corner(corner_pos)

            # Handle collision with sides (AABB collision already handled)
            self.adjust_position(obstacle)
            self.reverse_speed(obstacle)
            return True

        return False

    def is_point_inside_circle(self, x, y):
        # Check if the point is inside the circle
        distance_squared = (self.current_pos[0] - x)**2 + (self.current_pos[1] - y)**2
        return distance_squared <= self.radius**2