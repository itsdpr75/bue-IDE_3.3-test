import pygame
import sys
import random
import math

pygame.init()
pygame.SRCALPHA

WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Unreal-style Blueprint Interface")

# Color palette
BACKGROUND = (30, 30, 30)
GRID_COLOR = (50, 50, 50)
NODE_HEADER = (60, 60, 60)
NODE_BODY = (0, 0, 0, 128)
NODE_OUTLINE = (100, 100, 100)
NODE_TEXT = (200, 200, 200)
CONNECTOR_COLOR = (0, 174, 255)

class Node:
    def __init__(self, x, y, width, height, name="Node"):
        self.rect = pygame.Rect(x, y, width, height)
        self.name = name
        self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        self.inputs = ["In1"]
        self.outputs = ["Out1"]
        self.content = "Content"

    def draw(self, surface):
        # Draw node body
        pygame.draw.rect(surface, NODE_BODY, self.rect, border_radius=10)
        pygame.draw.rect(surface, NODE_OUTLINE, self.rect, 2, border_radius=10)
        
        # Draw node header
        header_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 30)
        pygame.draw.rect(surface, self.color, header_rect, border_top_left_radius=10, border_top_right_radius=10)
        
        font = pygame.font.Font(None, 24)
        
        # Draw node name
        text = font.render(self.name, True, NODE_TEXT)
        text_rect = text.get_rect(center=(self.rect.centerx, self.rect.top + 15))
        surface.blit(text, text_rect)
        
        # Draw node content
        content_text = font.render(self.content, True, NODE_TEXT)
        content_rect = content_text.get_rect(center=(self.rect.centerx, self.rect.centery + 15))
        surface.blit(content_text, content_rect)

        # Draw input and output connectors
        for i, input_name in enumerate(self.inputs):
            y = self.rect.top + 40 + i * 30
            pygame.draw.circle(surface, CONNECTOR_COLOR, (self.rect.left, int(y)), 8)
            text = font.render(input_name, True, NODE_TEXT)
            surface.blit(text, (self.rect.left + 15, int(y) - 10))

        for i, output_name in enumerate(self.outputs):
            y = self.rect.top + 40 + i * 30
            pygame.draw.circle(surface, CONNECTOR_COLOR, (self.rect.right, int(y)), 8)
            text = font.render(output_name, True, NODE_TEXT)
            surface.blit(text, (self.rect.right - 65, int(y) - 10))

    def is_over(self, pos):
        return self.rect.collidepoint(pos)

    def get_input_port(self, pos):
        for i in range(len(self.inputs)):
            y = self.rect.top + 40 + i * 30
            if pygame.Rect(self.rect.left - 10, y - 10, 20, 20).collidepoint(pos):
                return i
        return None

    def get_output_port(self, pos):
        for i in range(len(self.outputs)):
            y = self.rect.top + 40 + i * 30
            if pygame.Rect(self.rect.right - 10, y - 10, 20, 20).collidepoint(pos):
                return i
        return None

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def add_input(self):
        self.inputs.append(f"In{len(self.inputs) + 1}")

    def add_output(self):
        self.outputs.append(f"Out{len(self.outputs) + 1}")

class Connection:
    def __init__(self, start_node, end_node, start_port, end_port):
        self.start_node = start_node
        self.end_node = end_node
        self.start_port = start_port
        self.end_port = end_port

    def draw(self, surface):
        start_pos = (self.start_node.rect.right, 
                     self.start_node.rect.top + 40 + self.start_port * 30)
        end_pos = (self.end_node.rect.left, 
                   self.end_node.rect.top + 40 + self.end_port * 30)
        
        # Calculate control points for the curve
        control1 = (start_pos[0] + 100, start_pos[1])
        control2 = (end_pos[0] - 100, end_pos[1])
        
        # Draw a Bezier curve
        points = [(start_pos[0], start_pos[1])]
        for t in range(1, 100):
            t = t / 100
            x = (1-t)**3 * start_pos[0] + 3*(1-t)**2 * t * control1[0] + 3*(1-t) * t**2 * control2[0] + t**3 * end_pos[0]
            y = (1-t)**3 * start_pos[1] + 3*(1-t)**2 * t * control1[1] + 3*(1-t) * t**2 * control2[1] + t**3 * end_pos[1]
            points.append((int(x), int(y)))
        
        pygame.draw.lines(surface, CONNECTOR_COLOR, False, points, 2)

class ContextMenu:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, 150, 160)
        self.visible = False
        self.options = ["Create Node", "Edit Node", "Change Color", "Add Input", "Add Output"]

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
    node = Node(x, y, 200, 150, f"Node {len(nodes)}")
    nodes.append(node)

def edit_node(node):
    new_name = input("Enter new node name: ")
    new_content = input("Enter new node content: ")
    if new_name:
        node.name = new_name
    if new_content:
        node.content = new_content

def change_node_color(node):
    new_color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
    node.color = new_color

def draw_grid(surface, camera):
    for x in range(0, WIDTH, 50):
        pygame.draw.line(surface, GRID_COLOR, 
                         (x - camera.rect.x * camera.zoom, 0), 
                         (x - camera.rect.x * camera.zoom, HEIGHT))
    for y in range(0, HEIGHT, 50):
        pygame.draw.line(surface, GRID_COLOR, 
                         (0, y - camera.rect.y * camera.zoom), 
                         (WIDTH, y - camera.rect.y * camera.zoom))

nodes = []
connections = []
context_menu = ContextMenu()
camera = Camera(WIDTH, HEIGHT)
dragging = False
connecting = False
panning = False
selected_node = None
start_node = None
start_port = None

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if context_menu.visible:
                    option = context_menu.get_option(event.pos)
                    if option == "Create Node":
                        create_node(event.pos, camera)
                    elif option == "Edit Node" and selected_node:
                        edit_node(selected_node)
                    elif option == "Change Color" and selected_node:
                        change_node_color(selected_node)
                    elif option == "Add Input" and selected_node:
                        selected_node.add_input()
                    elif option == "Add Output" and selected_node:
                        selected_node.add_output()
                    context_menu.hide()
                else:
                    for node in nodes:
                        screen_pos = ((node.rect.x - camera.rect.x) * camera.zoom,
                                      (node.rect.y - camera.rect.y) * camera.zoom)
                        if pygame.Rect(screen_pos, (node.rect.width * camera.zoom, node.rect.height * camera.zoom)).collidepoint(event.pos):
                            output_port = node.get_output_port(((event.pos[0] / camera.zoom + camera.rect.x),
                                                                (event.pos[1] / camera.zoom + camera.rect.y)))
                            if output_port is not None:
                                connecting = True
                                start_node = node
                                start_port = output_port
                            else:
                                dragging = True
                                selected_node = node
                                offset_x = node.rect.x - (event.pos[0] / camera.zoom + camera.rect.x)
                                offset_y = node.rect.y - (event.pos[1] / camera.zoom + camera.rect.y)
                            break
                    else:
                        panning = True
                        pan_start = event.pos
            elif event.button == 3:  # Right click
                context_menu.show(event.pos)
                for node in nodes:
                    screen_pos = ((node.rect.x - camera.rect.x) * camera.zoom,
                                  (node.rect.y - camera.rect.y) * camera.zoom)
                    if pygame.Rect(screen_pos, (node.rect.width * camera.zoom, node.rect.height * camera.zoom)).collidepoint(event.pos):
                        selected_node = node
                        break
                else:
                    selected_node = None
            elif event.button == 4:  # Scroll up
                camera.zoom_in(1.1)
            elif event.button == 5:  # Scroll down
                camera.zoom_out(1.1)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                dragging = False
                panning = False
                if connecting:
                    for node in nodes:
                        screen_pos = ((node.rect.x - camera.rect.x) * camera.zoom,
                                      (node.rect.y - camera.rect.y) * camera.zoom)
                        if pygame.Rect(screen_pos, (node.rect.width * camera.zoom, node.rect.height * camera.zoom)).collidepoint(event.pos):
                            input_port = node.get_input_port(((event.pos[0] / camera.zoom + camera.rect.x),
                                                              (event.pos[1] / camera.zoom + camera.rect.y)))
                            if input_port is not None and node != start_node:
                                connections.append(Connection(start_node, node, start_port, input_port))
                            break
                    connecting = False
                    start_node = None
                    start_port = None

        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                selected_node.move((event.pos[0] / camera.zoom - selected_node.rect.x + offset_x),
                                   (event.pos[1] / camera.zoom - selected_node.rect.y + offset_y))
            elif panning:
                dx, dy = event.pos[0] - pan_start[0], event.pos[1] - pan_start[1]
                camera.move(-dx / camera.zoom, -dy / camera.zoom)
                pan_start = event.pos

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                context_menu.hide()
                connecting = False
                start_node = None
                start_port = None

    screen.fill(BACKGROUND)
    draw_grid(screen, camera)

    for connection in connections:
        connection.draw(screen)

    for node in nodes:
        screen_pos = ((node.rect.x - camera.rect.x) * camera.zoom,
                      (node.rect.y - camera.rect.y) * camera.zoom)
        scaled_rect = pygame.Rect(screen_pos, (node.rect.width * camera.zoom, node.rect.height * camera.zoom))
        pygame.draw.rect(screen, NODE_BODY, scaled_rect, border_radius=int(10 * camera.zoom))
        pygame.draw.rect(screen, NODE_OUTLINE, scaled_rect, 2, border_radius=int(10 * camera.zoom))
        
        header_rect = pygame.Rect(screen_pos[0], screen_pos[1], node.rect.width * camera.zoom, 30 * camera.zoom)
        pygame.draw.rect(screen, node.color, header_rect, border_top_left_radius=int(10 * camera.zoom), border_top_right_radius=int(10 * camera.zoom))
        
        font = pygame.font.Font(None, int(24 * camera.zoom))
        
        text = font.render(node.name, True, NODE_TEXT)
        text_rect = text.get_rect(center=(scaled_rect.centerx, scaled_rect.top + 15 * camera.zoom))
        screen.blit(text, text_rect)
        
        content_text = font.render(node.content, True, NODE_TEXT)
        content_rect = content_text.get_rect(center=(scaled_rect.centerx, scaled_rect.centery + 15 * camera.zoom))
        screen.blit(content_text, content_rect)

        for i, input_name in enumerate(node.inputs):
            y = screen_pos[1] + (40 + i * 30) * camera.zoom
            pygame.draw.circle(screen, CONNECTOR_COLOR, (screen_pos[0], int(y)), int(8 * camera.zoom))
            text = font.render(input_name, True, NODE_TEXT)
            screen.blit(text, (screen_pos[0] + 15 * camera.zoom, int(y) - 10 * camera.zoom))

        for i, output_name in enumerate(node.outputs):
            y = screen_pos[1] + (40 + i * 30) * camera.zoom
            pygame.draw.circle(screen, CONNECTOR_COLOR, (screen_pos[0] + node.rect.width * camera.zoom, int(y)), int(8 * camera.zoom))
            text = font.render(output_name, True, NODE_TEXT)
            screen.blit(text, (screen_pos[0] + (node.rect.width - 65) * camera.zoom, int(y) - 10 * camera.zoom))

    if connecting:
        start_pos = (start_node.rect.right - camera.rect.x, 
                     start_node.rect.top + 40 + start_port * 30 - camera.rect.y)
        start_pos = (start_pos[0] * camera.zoom, start_pos[1] * camera.zoom)
        end_pos = pygame.mouse.get_pos()
        
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
        
        pygame.draw.lines(screen, CONNECTOR_COLOR, False, points, 2)

    context_menu.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()
        