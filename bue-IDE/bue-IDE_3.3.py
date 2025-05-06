import pygame
import sys
import random

pygame.init()
pygame.SRCALPHA

WIDTH, HEIGHT = 1500, 800
PANEL_WIDTH = 300  # Panel width for editing nodes
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BUE IDE v3.2")

# Color palette
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

    def draw(self, surface):
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
    node = Node(x, y, 200, 150, f"Node {len(nodes)}")
    nodes.append(node)

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

def draw_panel(surface, node, mouse_pos):
    if node:
        pygame.draw.rect(surface, PANEL_BACKGROUND, pygame.Rect(WIDTH - PANEL_WIDTH, 0, PANEL_WIDTH, HEIGHT))
        font = pygame.font.Font(None, 24)
        
        # Title
        title = font.render("Node Editor", True, PANEL_TEXT_COLOR)
        surface.blit(title, (WIDTH - PANEL_WIDTH + 20, 20))
        
        # Node name
        name_text = font.render(f"Name: {node.name}", True, PANEL_TEXT_COLOR)
        surface.blit(name_text, (WIDTH - PANEL_WIDTH + 20, 60))
        
        # Input names
        input_title = font.render("Inputs:", True, PANEL_TEXT_COLOR)
        surface.blit(input_title, (WIDTH - PANEL_WIDTH + 20, 100))
        for i, input_name in enumerate(node.inputs):
            input_text = font.render(f"{i+1}. {input_name}", True, PANEL_TEXT_COLOR)
            surface.blit(input_text, (WIDTH - PANEL_WIDTH + 40, 130 + i * 30))
        add_input_button = pygame.Rect(WIDTH - PANEL_WIDTH + 20, 130 + len(node.inputs) * 30 + 10, 30, 30)
        pygame.draw.rect(surface, BUTTON_COLOR, add_input_button)
        add_input_text = font.render("+", True, PANEL_TEXT_COLOR)
        surface.blit(add_input_text, add_input_button.topleft)
        
        # Output names
        output_title = font.render("Outputs:", True, PANEL_TEXT_COLOR)
        surface.blit(output_title, (WIDTH - PANEL_WIDTH + 20, 200))
        for i, output_name in enumerate(node.outputs):
            output_text = font.render(f"{i+1}. {output_name}", True, PANEL_TEXT_COLOR)
            surface.blit(output_text, (WIDTH - PANEL_WIDTH + 40, 230 + i * 30))
        add_output_button = pygame.Rect(WIDTH - PANEL_WIDTH + 20, 230 + len(node.outputs) * 30 + 10, 30, 30)
        pygame.draw.rect(surface, BUTTON_COLOR, add_output_button)
        add_output_text = font.render("+", True, PANEL_TEXT_COLOR)
        surface.blit(add_output_text, add_output_button.topleft)
        
        # Content
        content_text = font.render(f"Content: {node.content}", True, PANEL_TEXT_COLOR)
        surface.blit(content_text, (WIDTH - PANEL_WIDTH + 20, 300))

        return add_input_button, add_output_button

nodes = []
connections = []
camera = Camera(WIDTH, HEIGHT)
selected_node = None
dragging_node = None
dragging_offset = (0, 0)
context_menu = ContextMenu()

while True:
    screen.fill(BACKGROUND)
    
    # Grid
    draw_grid(screen, camera)
    
    # Nodes
    for node in nodes:
        node.draw(screen)
    
    # Connections
    for connection in connections:
        connection.draw(screen)

    # Draw the panel if a node is selected
    add_input_button, add_output_button = None, None
    if selected_node:
        add_input_button, add_output_button = draw_panel(screen, selected_node, pygame.mouse.get_pos())

    # Draw the context menu
    context_menu.draw(screen)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if add_input_button and add_input_button.collidepoint(event.pos):
                    selected_node.add_input()
                elif add_output_button and add_output_button.collidepoint(event.pos):
                    selected_node.add_output()
                else:
                    for node in nodes:
                        if node.is_over(event.pos):
                            selected_node = node
                            dragging_node = node
                            dragging_offset = (node.rect.x - event.pos[0], node.rect.y - event.pos[1])
                            break
                    option = context_menu.get_option(event.pos)
                    if option == "Create Node":
                        create_node(event.pos, camera)
                        context_menu.hide()  # Hide the menu after selection
                    elif option == "Change Color" and selected_node:
                        change_node_color(selected_node)
                        context_menu.hide()  # Hide the menu after selection
            elif event.button == 3:  # Right click
                context_menu.show(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            dragging_node = None
        elif event.type == pygame.MOUSEMOTION:
            if dragging_node:
                dragging_node.move(event.pos[0] + dragging_offset[0] - dragging_node.rect.x, 
                                   event.pos[1] + dragging_offset[1] - dragging_node.rect.y)

    pygame.display.flip()
