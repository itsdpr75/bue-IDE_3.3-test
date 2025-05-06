import pygame
import sys
import random

pygame.init()
pygame.SRCALPHA

WIDTH, HEIGHT = 1500, 800
PANEL_WIDTH = 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BUE IDE v3.3")

# Color palette (unchanged)
BACKGROUND = (30, 30, 30)
GRID_COLOR = (50, 50, 50)
NODE_HEADER = (60, 60, 60)
NODE_BODY = (0, 0, 0, 128)
NODE_OUTLINE = (100, 100, 100)
NODE_TEXT = (200, 200, 200)
CONNECTOR_COLOR = (0, 174, 255)
PANEL_BACKGROUND = (50, 50, 50)
PANEL_TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (80, 80, 80)
BUTTON_HOVER_COLOR = (100, 100, 100)

class Node:
    def __init__(self, x, y, width, height, name="Node"):
        self.rect = pygame.Rect(x, y, width, height)
        self.name = name
        self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        self.inputs = ["In1"]
        self.outputs = ["Out1"]
        self.content = "Content"

    def draw(self, surface, camera):
        scaled_rect = pygame.Rect(
            (self.rect.x - camera.rect.x) * camera.zoom,
            (self.rect.y - camera.rect.y) * camera.zoom,
            self.rect.width * camera.zoom,
            self.rect.height * camera.zoom
        )
        pygame.draw.rect(surface, NODE_BODY, scaled_rect, border_radius=int(10 * camera.zoom))
        pygame.draw.rect(surface, NODE_OUTLINE, scaled_rect, int(2 * camera.zoom), border_radius=int(10 * camera.zoom))
        
        # Draw node header
        header_rect = pygame.Rect(scaled_rect.x, scaled_rect.y, scaled_rect.width, 30 * camera.zoom)
        pygame.draw.rect(surface, self.color, header_rect, border_top_left_radius=int(10 * camera.zoom), border_top_right_radius=int(10 * camera.zoom))
        
        font = pygame.font.Font(None, int(24 * camera.zoom))
        
        # Draw node name
        text = font.render(self.name, True, NODE_TEXT)
        text_rect = text.get_rect(center=(scaled_rect.centerx, scaled_rect.top + 15 * camera.zoom))
        surface.blit(text, text_rect)
        
        # Draw node content
        content_text = font.render(self.content, True, NODE_TEXT)
        content_rect = content_text.get_rect(center=(scaled_rect.centerx, scaled_rect.centery + 15 * camera.zoom))
        surface.blit(content_text, content_rect)

        # Draw input and output connectors
        for i, input_name in enumerate(self.inputs):
            y = scaled_rect.top + (40 + i * 30) * camera.zoom
            pygame.draw.circle(surface, CONNECTOR_COLOR, (scaled_rect.left, int(y)), int(8 * camera.zoom))
            text = font.render(input_name, True, NODE_TEXT)
            surface.blit(text, (scaled_rect.left + 15 * camera.zoom, int(y) - 10 * camera.zoom))

        for i, output_name in enumerate(self.outputs):
            y = scaled_rect.top + (40 + i * 30) * camera.zoom
            pygame.draw.circle(surface, CONNECTOR_COLOR, (scaled_rect.right, int(y)), int(8 * camera.zoom))
            text = font.render(output_name, True, NODE_TEXT)
            surface.blit(text, (scaled_rect.right - 65 * camera.zoom, int(y) - 10 * camera.zoom))

    def is_over(self, pos, camera):
        scaled_rect = pygame.Rect(
            (self.rect.x - camera.rect.x) * camera.zoom,
            (self.rect.y - camera.rect.y) * camera.zoom,
            self.rect.width * camera.zoom,
            self.rect.height * camera.zoom
        )
        return scaled_rect.collidepoint(pos)

    def get_input_port(self, pos, camera):
        scaled_rect = pygame.Rect(
            (self.rect.x - camera.rect.x) * camera.zoom,
            (self.rect.y - camera.rect.y) * camera.zoom,
            self.rect.width * camera.zoom,
            self.rect.height * camera.zoom
        )
        for i in range(len(self.inputs)):
            y = scaled_rect.top + (40 + i * 30) * camera.zoom
            if pygame.Rect(scaled_rect.left - 10 * camera.zoom, y - 10 * camera.zoom, 20 * camera.zoom, 20 * camera.zoom).collidepoint(pos):
                return i
        return None

    def get_output_port(self, pos, camera):
        scaled_rect = pygame.Rect(
            (self.rect.x - camera.rect.x) * camera.zoom,
            (self.rect.y - camera.rect.y) * camera.zoom,
            self.rect.width * camera.zoom,
            self.rect.height * camera.zoom
        )
        for i in range(len(self.outputs)):
            y = scaled_rect.top + (40 + i * 30) * camera.zoom
            if pygame.Rect(scaled_rect.right - 10 * camera.zoom, y - 10 * camera.zoom, 20 * camera.zoom, 20 * camera.zoom).collidepoint(pos):
                return i
        return None

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def add_input(self):
        self.inputs.append(f"In{len(self.inputs) + 1}")

    def add_output(self):
        self.outputs.append(f"Out{len(self.outputs) + 1}")

    def set_name(self, name):
        self.name = name

    def set_content(self, content):
        self.content = content

class Connection:
    def __init__(self, start_node, end_node, start_port, end_port):
        self.start_node = start_node
        self.end_node = end_node
        self.start_port = start_port
        self.end_port = end_port

    def draw(self, surface, camera):
        start_pos = (
            (self.start_node.rect.right - camera.rect.x) * camera.zoom,
            (self.start_node.rect.top + 40 + self.start_port * 30 - camera.rect.y) * camera.zoom
        )
        end_pos = (
            (self.end_node.rect.left - camera.rect.x) * camera.zoom,
            (self.end_node.rect.top + 40 + self.end_port * 30 - camera.rect.y) * camera.zoom
        )
        
        # Calculate control points for the curve
        control1 = (start_pos[0] + 100 * camera.zoom, start_pos[1])
        control2 = (end_pos[0] - 100 * camera.zoom, end_pos[1])
        
        # Draw a Bezier curve
        points = [(start_pos[0], start_pos[1])]
        for t in range(1, 100):
            t = t / 100
            x = (1-t)**3 * start_pos[0] + 3*(1-t)**2 * t * control1[0] + 3*(1-t) * t**2 * control2[0] + t**3 * end_pos[0]
            y = (1-t)**3 * start_pos[1] + 3*(1-t)**2 * t * control1[1] + 3*(1-t) * t**2 * control2[1] + t**3 * end_pos[1]
            points.append((int(x), int(y)))
        
        pygame.draw.lines(surface, CONNECTOR_COLOR, False, points, int(2 * camera.zoom))

class ContextMenu:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, 150, 120)
        self.visible = False
        self.options = ["Create Node", "Change Color"]

    def show(self, pos):
        self.rect.topleft = pos
        self.visible = True

    def hide(self):
        self.visible = False

    def draw(self, surface):
        if self.visible:
            pygame.draw.rect(surface, NODE_BODY, self.rect)
            pygame.draw.rect(surface, NODE_OUTLINE, self.rect, 2)
            font = pygame.font.Font(None, 24)
            for i, option in enumerate(self.options):
                text = font.render(option, True, NODE_TEXT)
                surface.blit(text, (self.rect.x + 10, self.rect.y + 10 + i * 30))

    def get_option(self, pos):
        if self.visible and self.rect.collidepoint(pos):
            index = (pos[1] - self.rect.y - 10) // 30
            if 0 <= index < len(self.options):
                return self.options[index]
        return None

class Camera:
    def __init__(self, width, height):
        self.rect = pygame.Rect(0, 0, width, height)
        self.zoom = 1.0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def zoom_in(self, factor):
        self.zoom *= factor

    def zoom_out(self, factor):
        self.zoom /= factor

def create_node(pos, camera):
    x = (pos[0] + camera.rect.x) / camera.zoom
    y = (pos[1] + camera.rect.y) / camera.zoom
    return Node(int(x), int(y), 200, 100)

def draw_grid(surface, camera):
    grid_spacing = 50 * camera.zoom
    for x in range(0, WIDTH, int(grid_spacing)):
        pygame.draw.line(surface, GRID_COLOR, ((x - camera.rect.x) * camera.zoom, 0), ((x - camera.rect.x) * camera.zoom, HEIGHT))
    for y in range(0, HEIGHT, int(grid_spacing)):
        pygame.draw.line(surface, GRID_COLOR, (0, (y - camera.rect.y) * camera.zoom), (WIDTH, (y - camera.rect.y) * camera.zoom))

# Initialize
camera = Camera(WIDTH, HEIGHT)
context_menu = ContextMenu()
nodes = []
connections = []

dragging_node = None
moving_camera = False
connecting = False
start_node = None
start_port = None
is_output = False

# Main loop
while True:
    screen.fill(BACKGROUND)
    draw_grid(screen, camera)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        # Mouse button down events
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                for node in nodes:
                    if node.is_over(event.pos, camera):
                        dragging_node = node
                        start_port = node.get_input_port(event.pos, camera)
                        if start_port is not None:
                            connecting = True
                            start_node = node
                            is_output = False
                            break
                        start_port = node.get_output_port(event.pos, camera)
                        if start_port is not None:
                            connecting = True
                            start_node = node
                            is_output = True
                            break
                if not dragging_node and not connecting:
                    context_menu.show(event.pos)

            elif event.button == 3:  # Right click
                context_menu.show(event.pos)
        
        # Mouse button up events
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click release
                dragging_node = None
                if connecting:
                    for node in nodes:
                        if node != start_node and node.is_over(event.pos, camera):
                            if is_output:
                                end_port = node.get_input_port(event.pos, camera)
                                if end_port is not None:
                                    connections.append(Connection(start_node, node, start_port, end_port))
                                    break
                            else:
                                end_port = node.get_output_port(event.pos, camera)
                                if end_port is not None:
                                    connections.append(Connection(node, start_node, end_port, start_port))
                                    break
                    connecting = False
                    start_node = None
                    start_port = None
                    is_output = False

        # Mouse motion events
        if event.type == pygame.MOUSEMOTION:
            if dragging_node:
                dragging_node.move(event.rel[0], event.rel[1])
            if moving_camera:
                camera.move(-event.rel[0], -event.rel[1])

    for connection in connections:
        connection.draw(screen, camera)

    for node in nodes:
        node.draw(screen, camera)

    context_menu.draw(screen)

    pygame.display.update()
