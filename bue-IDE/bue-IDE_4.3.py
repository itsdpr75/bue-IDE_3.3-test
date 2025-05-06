import pygame
import sys
import random
import json
import os

pygame.init()
pygame.SRCALPHA

WIDTH, HEIGHT = 1500, 800
PANEL_WIDTH = 300
TOP_PANEL_HEIGHT = 50
PREDEFINED_PANEL_WIDTH = 200
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BUE IDE v3.5")

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
SAVE_BUTTON_COLOR = (200, 200, 200)
SAVE_BUTTON_HOVER_COLOR = (150, 150, 150)

# Node class with customizable properties
class Node:
    def __init__(self, x, y, width, height, name="Node", color=(100, 100, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.name = name
        self.color = color
        self.inputs = ["In1"]
        self.outputs = ["Out1"]
        self.content = "Content"
        self.symbol = ""  # Symbol in the upper corner
        self.center_text = ""  # Text in the center
        self.description = ""
        self.input_colors = [(0, 174, 255) for _ in range(len(self.inputs))]  # Default input colors
        self.output_colors = [(0, 174, 255) for _ in range(len(self.outputs))]  # Default output colors
        self.input_types = ["Any" for _ in range(len(self.inputs))]  # Default input types
        self.output_types = ["Any" for _ in range(len(self.outputs))]  # Default output types
        self.code = ""  # Code associated with the node
        self.lock = False  # Configuration lock
        self.symbol_color = (255, 255, 255)  # Default symbol color

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
        
        # Draw node name (using the color of the node)
        text = font.render(self.name, True, self.color)  # Set the color to the node color
        text_rect = text.get_rect(center=(scaled_rect.centerx, scaled_rect.top + 15 * camera.zoom))
        surface.blit(text, text_rect)
        
        # Draw node content
        content_text = font.render(self.content, True, NODE_TEXT)
        content_rect = content_text.get_rect(center=(scaled_rect.centerx, scaled_rect.centery + 15 * camera.zoom))
        surface.blit(content_text, content_rect)

        # Draw input and output connectors
        for i, input_name in enumerate(self.inputs):
            y = scaled_rect.top + (40 + i * 30) * camera.zoom
            pygame.draw.circle(surface, self.input_colors[i], (scaled_rect.left, int(y)), int(8 * camera.zoom))
            text = font.render(input_name, True, NODE_TEXT)
            surface.blit(text, (scaled_rect.left + 15 * camera.zoom, int(y) - 10 * camera.zoom))

        for i, output_name in enumerate(self.outputs):
            y = scaled_rect.top + (40 + i * 30) * camera.zoom
            pygame.draw.circle(surface, self.output_colors[i], (scaled_rect.right, int(y)), int(8 * camera.zoom))
            text = font.render(output_name, True, NODE_TEXT)
            surface.blit(text, (scaled_rect.right - 65 * camera.zoom, int(y) - 10 * camera.zoom))

# Project class to handle saving and loading projects
class Project:
    def __init__(self):
        self.nodes = []
        self.connections = []

    def add_node(self, node):
        self.nodes.append(node)

    def add_connection(self, connection):
        self.connections.append(connection)

    def save(self, filename):
        data = {
            "nodes": [self._node_to_dict(node) for node in self.nodes],
            "connections": [self._connection_to_dict(connection) for connection in self.connections]
        }
        with open(filename, 'w') as file:
            json.dump(data, file)

    def load(self, filename):
        with open(filename, 'r') as file:
            data = json.load(file)
        self.nodes = [self._dict_to_node(node_data) for node_data in data["nodes"]]
        self.connections = [self._dict_to_connection(conn_data) for conn_data in data["connections"]]

    def _node_to_dict(self, node):
        return {
            "x": node.rect.x,
            "y": node.rect.y,
            "width": node.rect.width,
            "height": node.rect.height,
            "name": node.name,
            "inputs": node.inputs,
            "outputs": node.outputs,
            "content": node.content,
            "symbol": node.symbol,
            "center_text": node.center_text,
            "description": node.description,
            "input_colors": node.input_colors,
            "output_colors": node.output_colors,
            "input_types": node.input_types,
            "output_types": node.output_types,
            "code": node.code,
            "lock": node.lock,
            "symbol_color": node.symbol_color,
            "color": node.color
        }

    def _connection_to_dict(self, connection):
        return {
            "start_node": self.nodes.index(connection.start_node),
            "end_node": self.nodes.index(connection.end_node),
            "start_port": connection.start_port,
            "end_port": connection.end_port
        }

    def _dict_to_node(self, data):
        node = Node(data["x"], data["y"], data["width"], data["height"], data["name"], data["color"])
        node.inputs = data["inputs"]
        node.outputs = data["outputs"]
        node.content = data["content"]
        node.symbol = data["symbol"]
        node.center_text = data["center_text"]
        node.description = data["description"]
        node.input_colors = data["input_colors"]
        node.output_colors = data["output_colors"]
        node.input_types = data["input_types"]
        node.output_types = data["output_types"]
        node.code = data["code"]
        node.lock = data["lock"]
        node.symbol_color = data["symbol_color"]
        return node

    def _dict_to_connection(self, data):
        start_node = self.nodes[data["start_node"]]
        end_node = self.nodes[data["end_node"]]
        return Connection(start_node, end_node, data["start_port"], data["end_port"])

# Connection class
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

def create_node(pos, camera, name="Node", color=(100, 100, 255)):
    x = (pos[0] + camera.rect.x) / camera.zoom
    y = (pos[1] + camera.rect.y) / camera.zoom
    node = Node(x, y, 200, 150, name, color)
    nodes.append(node)

def draw_grid(surface, camera):
    for x in range(0, WIDTH, 50):
        pygame.draw.line(surface, GRID_COLOR, 
                         ((x - camera.rect.x) * camera.zoom, 0), 
                         ((x - camera.rect.x) * camera.zoom, HEIGHT))
    for y in range(0, HEIGHT, 50):
        pygame.draw.line(surface, GRID_COLOR, 
                         (0, (y - camera.rect.y) * camera.zoom), 
                         (WIDTH, (y - camera.rect.y) * camera.zoom))

# Function to draw the top panel
def draw_top_panel(surface):
    pygame.draw.rect(surface, PANEL_BACKGROUND, pygame.Rect(0, 0, WIDTH, TOP_PANEL_HEIGHT))
    font = pygame.font.Font(None, 24)

    # Save button
    save_button = pygame.Rect(WIDTH - 220, 10, 100, 30)
    pygame.draw.rect(surface, SAVE_BUTTON_COLOR, save_button)
    save_text = font.render("Save", True, (0, 0, 0))
    surface.blit(save_text, (save_button.x + 30, save_button.y + 5))

    # Open button
    open_button = pygame.Rect(WIDTH - 110, 10, 100, 30)
    pygame.draw.rect(surface, SAVE_BUTTON_COLOR, open_button)
    open_text = font.render("Open", True, (0, 0, 0))
    surface.blit(open_text, (open_button.x + 30, open_button.y + 5))

    return save_button, open_button

# Function to draw the side panel (always visible)
def draw_side_panel(surface, node):
    pygame.draw.rect(surface, PANEL_BACKGROUND, pygame.Rect(WIDTH - PANEL_WIDTH, 0, PANEL_WIDTH, HEIGHT))
    font = pygame.font.Font(None, 24)

    if node:
        # Title
        title = font.render("Node Editor", True, PANEL_TEXT_COLOR)
        surface.blit(title, (WIDTH - PANEL_WIDTH + 20, 20))
        
        # Node name
        name_text = font.render(f"Name: {node.name}", True, PANEL_TEXT_COLOR)
        surface.blit(name_text, (WIDTH - PANEL_WIDTH + 20, 60))
        
        # Inputs
        input_title = font.render("Inputs:", True, PANEL_TEXT_COLOR)
        surface.blit(input_title, (WIDTH - PANEL_WIDTH + 20, 100))
        for i, input_name in enumerate(node.inputs):
            input_text = font.render(f"{i+1}. {input_name}", True, PANEL_TEXT_COLOR)
            surface.blit(input_text, (WIDTH - PANEL_WIDTH + 40, 130 + i * 30))

        # Outputs
        output_title = font.render("Outputs:", True, PANEL_TEXT_COLOR)
        surface.blit(output_title, (WIDTH - PANEL_WIDTH + 20, 160 + len(node.inputs) * 30))
        for i, output_name in enumerate(node.outputs):
            output_text = font.render(f"{i+1}. {output_name}", True, PANEL_TEXT_COLOR)
            surface.blit(output_text, (WIDTH - PANEL_WIDTH + 40, 190 + len(node.inputs) * 30 + i * 30))
        
    else:
        # Display "Select a node" message
        no_node_text = font.render("Select a node to adjust its configuration.", True, PANEL_TEXT_COLOR)
        surface.blit(no_node_text, (WIDTH - PANEL_WIDTH + 20, 60))

# Function to draw predefined nodes panel
def draw_predefined_panel(surface, predefined_nodes):
    pygame.draw.rect(surface, PANEL_BACKGROUND, pygame.Rect(0, 0, PREDEFINED_PANEL_WIDTH, HEIGHT))
    font = pygame.font.Font(None, 24)

    title = font.render("Predefined Nodes", True, PANEL_TEXT_COLOR)
    surface.blit(title, (20, 20))

    if not predefined_nodes:
        no_node_text = font.render("No nodes", True, PANEL_TEXT_COLOR)
        surface.blit(no_node_text, (20, 60))
    else:
        for i, node_name in enumerate(predefined_nodes):
            node_text = font.render(node_name, True, PANEL_TEXT_COLOR)
            surface.blit(node_text, (20, 60 + i * 30))

# Function to load predefined nodes
def load_predefined_nodes(folder="nodes"):
    if not os.path.exists(folder):
        return []
    return [f.replace(".bnode", "") for f in os.listdir(folder) if f.endswith(".bnode")]

# Main loop and event handling
nodes = []
connections = []
camera = Camera(WIDTH, HEIGHT)
selected_node = None
dragging_node = None
dragging_offset = (0, 0)
dragging_predefined = None  # To track dragging predefined nodes
project = Project()

predefined_nodes = load_predefined_nodes()

while True:
    screen.fill(BACKGROUND)
    
    # Grid
    draw_grid(screen, camera)

    # Top panel
    save_button, open_button = draw_top_panel(screen)
    
    # Side panel
    draw_side_panel(screen, selected_node)

    # Predefined nodes panel
    draw_predefined_panel(screen, predefined_nodes)
    
    # Nodes
    for node in nodes:
        node.draw(screen, camera)
    
    # Connections
    for connection in connections:
        connection.draw(screen, camera)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if save_button.collidepoint(event.pos):
                    project.save("my_project.buepyt")
                elif open_button.collidepoint(event.pos):
                    project.load("my_project.buepyt")
                else:
                    for node in nodes:
                        if node.is_over(event.pos, camera):
                            selected_node = node
                            dragging_node = node
                            dragging_offset = (
                                node.rect.x - (event.pos[0] + camera.rect.x) / camera.zoom,
                                node.rect.y - (event.pos[1] + camera.rect.y) / camera.zoom
                            )
                            break
                    # Check if clicking on a predefined node
                    for i, node_name in enumerate(predefined_nodes):
                        if pygame.Rect(20, 60 + i * 30, 160, 30).collidepoint(event.pos):
                            dragging_predefined = node_name
                            break
            elif event.button == 3:  # Right click
                pass  # Implement context menu here
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click release
                if dragging_predefined:
                    # Create a new node at the mouse position
                    create_node(pygame.mouse.get_pos(), camera, dragging_predefined, (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)))
                    dragging_predefined = None
                dragging_node = None
        elif event.type == pygame.MOUSEMOTION:
            if dragging_node:
                dragging_node.move(
                    (event.pos[0] + camera.rect.x) / camera.zoom - dragging_node.rect.x - dragging_offset[0],
                    (event.pos[1] + camera.rect.y) / camera.zoom - dragging_node.rect.y - dragging_offset[1]
                )
            elif pygame.mouse.get_pressed()[0]:  # Left mouse button held down
                camera.move(-event.rel[0] / camera.zoom, -event.rel[1] / camera.zoom)

    pygame.display.flip()
