import pygame
import sys
import random
import json

pygame.init()
pygame.SRCALPHA

WIDTH, HEIGHT = 1500, 800
PANEL_WIDTH = 300
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

# Node class with customizable properties
class Node:
    def __init__(self, x, y, width, height, name="Node"):
        self.rect = pygame.Rect(x, y, width, height)
        self.name = name
        self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
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
            pygame.draw.circle(surface, self.input_colors[i], (scaled_rect.left, int(y)), int(8 * camera.zoom))
            text = font.render(input_name, True, NODE_TEXT)
            surface.blit(text, (scaled_rect.left + 15 * camera.zoom, int(y) - 10 * camera.zoom))

        for i, output_name in enumerate(self.outputs):
            y = scaled_rect.top + (40 + i * 30) * camera.zoom
            pygame.draw.circle(surface, self.output_colors[i], (scaled_rect.right, int(y)), int(8 * camera.zoom))
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

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def add_input(self):
        self.inputs.append(f"In{len(self.inputs) + 1}")
        self.input_colors.append((0, 174, 255))  # Add default color for new input

    def add_output(self):
        self.outputs.append(f"Out{len(self.outputs) + 1}")
        self.output_colors.append((0, 174, 255))  # Add default color for new output

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
            "symbol_color": node.symbol_color
        }

    def _connection_to_dict(self, connection):
        return {
            "start_node": self.nodes.index(connection.start_node),
            "end_node": self.nodes.index(connection.end_node),
            "start_port": connection.start_port,
            "end_port": connection.end_port
        }

    def _dict_to_node(self, data):
        node = Node(data["x"], data["y"], data["width"], data["height"], data["name"])
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
                         ((x - camera.rect.x) * camera.zoom, 0), 
                         ((x - camera.rect.x) * camera.zoom, HEIGHT))
    for y in range(0, HEIGHT, 50):
        pygame.draw.line(surface, GRID_COLOR, 
                         (0, (y - camera.rect.y) * camera.zoom), 
                         (WIDTH, (y - camera.rect.y) * camera.zoom))

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
        add_input_button = pygame.Rect(WIDTH - PANEL_WIDTH + 80, 100, 20, 20)
        pygame.draw.rect(surface, BUTTON_COLOR, add_input_button)
        add_input_text = font.render("+", True, PANEL_TEXT_COLOR)
        surface.blit(add_input_text, (add_input_button.x + 5, add_input_button.y + 2))
        for i, input_name in enumerate(node.inputs):
            input_text = font.render(f"{i+1}. {input_name}", True, PANEL_TEXT_COLOR)
            surface.blit(input_text, (WIDTH - PANEL_WIDTH + 40, 130 + i * 30))
        
        # Output names
        output_title = font.render("Outputs:", True, PANEL_TEXT_COLOR)
        surface.blit(output_title, (WIDTH - PANEL_WIDTH + 20, max(200, 130 + len(node.inputs) * 30 + 40)))
        add_output_button = pygame.Rect(WIDTH - PANEL_WIDTH + 90, max(200, 130 + len(node.inputs) * 30 + 40), 20, 20)
        pygame.draw.rect(surface, BUTTON_COLOR, add_output_button)
        add_output_text = font.render("+", True, PANEL_TEXT_COLOR)
        surface.blit(add_output_text, (add_output_button.x + 5, add_output_button.y + 2))
        for i, output_name in enumerate(node.outputs):
            output_text = font.render(f"{i+1}. {output_name}", True, PANEL_TEXT_COLOR)
            surface.blit(output_text, (WIDTH - PANEL_WIDTH + 40, max(230, 160 + len(node.inputs) * 30 + 40) + i * 30))
        
        # Content
        content_text = font.render(f"Content: {node.content}", True, PANEL_TEXT_COLOR)
        surface.blit(content_text, (WIDTH - PANEL_WIDTH + 20, max(300, 190 + (len(node.inputs) + len(node.outputs)) * 30 + 40)))

        return add_input_button, add_output_button

    return None, None

# Main loop and event handling
nodes = []
connections = []
camera = Camera(WIDTH, HEIGHT)
selected_node = None
dragging_node = None
dragging_offset = (0, 0)
connecting = False
start_node = None
start_port = None
is_output = False

while True:
    screen.fill(BACKGROUND)
    
    # Grid
    draw_grid(screen, camera)
    
    # Nodes
    for node in nodes:
        node.draw(screen, camera)
    
    # Connections
    for connection in connections:
        connection.draw(screen, camera)

    # Draw the panel if a node is selected
    add_input_button, add_output_button = draw_panel(screen, selected_node, pygame.mouse.get_pos())
    
    # Draw connection in progress
    if connecting:
        start_pos = (
            (start_node.rect.right - camera.rect.x) * camera.zoom if is_output else (start_node.rect.left - camera.rect.x) * camera.zoom,
            (start_node.rect.top + 40 + start_port * 30 - camera.rect.y) * camera.zoom
        )
        end_pos = pygame.mouse.get_pos()
        pygame.draw.line(screen, CONNECTOR_COLOR, start_pos, end_pos, 2)

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
                        if node.is_over(event.pos, camera):
                            selected_node = node
                            output_port = node.get_output_port(event.pos, camera)
                            input_port = node.get_input_port(event.pos, camera)
                            if output_port is not None:
                                connecting = True
                                start_node = node
                                start_port = output_port
                                is_output = True
                                break
                            elif input_port is not None:
                                connecting = True
                                start_node = node
                                start_port = input_port
                                is_output = False
                                break
                            else:
                                dragging_node = node
                                dragging_offset = (
                                    node.rect.x - (event.pos[0] + camera.rect.x) / camera.zoom,
                                    node.rect.y - (event.pos[1] + camera.rect.y) / camera.zoom
                                )
                            break
            elif event.button == 3:  # Right click
                pass  # Implement context menu here
            elif event.button == 4:  # Scroll up
                camera.zoom_in(1.1)
            elif event.button == 5:  # Scroll down
                camera.zoom_out(1.1)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left click release
                dragging_node = None
                if connecting:
                    for node in nodes:
                        if node != start_node and node.is_over(event.pos, camera):
                            if is_output:
                                end_port = node.get_input_port(event.pos, camera)
                                if end_port is not None:
                                    connections.append(Connection(start_node, node, start_port, end_port))
                            else:
                                end_port = node.get_output_port(event.pos, camera)
                                if end_port is not None:
                                    connections.append(Connection(node, start_node, end_port, start_port))
                    connecting = False
                    start_node = None
                    start_port = None
                    is_output = False
        elif event.type == pygame.MOUSEMOTION:
            if dragging_node:
                dragging_node.move(
                    (event.pos[0] + camera.rect.x) / camera.zoom - dragging_node.rect.x - dragging_offset[0],
                    (event.pos[1] + camera.rect.y) / camera.zoom - dragging_node.rect.y - dragging_offset[1]
                )
            elif pygame.mouse.get_pressed()[0]:  # Left mouse button held down
                camera.move(-event.rel[0] / camera.zoom, -event.rel[1] / camera.zoom)

    pygame.display.flip()
