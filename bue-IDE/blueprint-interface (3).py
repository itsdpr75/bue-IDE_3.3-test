import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Blueprint Interface")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

class Node:
    def __init__(self, x, y, width, height, name="Node", color=GRAY):
        self.rect = pygame.Rect(x, y, width, height)
        self.name = name
        self.color = color
        self.inputs = ["In1"]
        self.outputs = ["Out1"]
        self.content = "Content"

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        font = pygame.font.Font(None, 24)
        
        text = font.render(self.name, True, BLACK)
        text_rect = text.get_rect(center=(self.rect.centerx, self.rect.top + 20))
        surface.blit(text, text_rect)
        
        content_text = font.render(self.content, True, BLACK)
        content_rect = content_text.get_rect(center=self.rect.center)
        surface.blit(content_text, content_rect)

        for i, input_name in enumerate(self.inputs):
            y = self.rect.top + (i + 1) * self.rect.height / (len(self.inputs) + 1)
            pygame.draw.circle(surface, RED, (self.rect.left, int(y)), 5)
            text = font.render(input_name, True, BLACK)
            surface.blit(text, (self.rect.left + 10, int(y) - 10))

        for i, output_name in enumerate(self.outputs):
            y = self.rect.top + (i + 1) * self.rect.height / (len(self.outputs) + 1)
            pygame.draw.circle(surface, GREEN, (self.rect.right, int(y)), 5)
            text = font.render(output_name, True, BLACK)
            surface.blit(text, (self.rect.right - 50, int(y) - 10))

    def is_over(self, pos):
        return self.rect.collidepoint(pos)

    def get_input_port(self, pos):
        for i in range(len(self.inputs)):
            y = self.rect.top + (i + 1) * self.rect.height / (len(self.inputs) + 1)
            if pygame.Rect(self.rect.left - 5, y - 5, 10, 10).collidepoint(pos):
                return i
        return None

    def get_output_port(self, pos):
        for i in range(len(self.outputs)):
            y = self.rect.top + (i + 1) * self.rect.height / (len(self.outputs) + 1)
            if pygame.Rect(self.rect.right - 5, y - 5, 10, 10).collidepoint(pos):
                return i
        return None

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

class Connection:
    def __init__(self, start_node, end_node, start_port, end_port):
        self.start_node = start_node
        self.end_node = end_node
        self.start_port = start_port
        self.end_port = end_port

    def draw(self, surface):
        start_pos = (self.start_node.rect.right, 
                     self.start_node.rect.top + (self.start_port + 1) * self.start_node.rect.height / (len(self.start_node.outputs) + 1))
        end_pos = (self.end_node.rect.left, 
                   self.end_node.rect.top + (self.end_port + 1) * self.end_node.rect.height / (len(self.end_node.inputs) + 1))
        pygame.draw.line(surface, BLUE, start_pos, end_pos, 2)

class ContextMenu:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, 150, 100)
        self.visible = False
        self.options = ["Create Node", "Edit Node", "Change Color"]

    def show(self, pos):
        self.rect.topleft = pos
        self.visible = True

    def hide(self):
        self.visible = False

    def draw(self, surface):
        if self.visible:
            pygame.draw.rect(surface, WHITE, self.rect)
            pygame.draw.rect(surface, BLACK, self.rect, 2)
            font = pygame.font.Font(None, 24)
            for i, option in enumerate(self.options):
                text = font.render(option, True, BLACK)
                surface.blit(text, (self.rect.x + 10, self.rect.y + 10 + i * 30))

    def get_option(self, pos):
        if self.visible and self.rect.collidepoint(pos):
            index = (pos[1] - self.rect.y - 10) // 30
            if 0 <= index < len(self.options):
                return self.options[index]
        return None

nodes = []
connections = []
context_menu = ContextMenu()
dragging = False
connecting = False
selected_node = None
start_node = None
start_port = None

def create_node(pos):
    color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
    node = Node(pos[0], pos[1], 150, 100, f"Node {len(nodes)}", color)
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
                        create_node(event.pos)
                    elif option == "Edit Node" and selected_node:
                        edit_node(selected_node)
                    elif option == "Change Color" and selected_node:
                        change_node_color(selected_node)
                    context_menu.hide()
                else:
                    for node in nodes:
                        if node.is_over(event.pos):
                            output_port = node.get_output_port(event.pos)
                            if output_port is not None:
                                connecting = True
                                start_node = node
                                start_port = output_port
                            else:
                                dragging = True
                                selected_node = node
                                offset_x = node.rect.x - event.pos[0]
                                offset_y = node.rect.y - event.pos[1]
                            break
            elif event.button == 3:  # Right click
                context_menu.show(event.pos)
                for node in nodes:
                    if node.is_over(event.pos):
                        selected_node = node
                        break
                else:
                    selected_node = None

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                dragging = False
                if connecting:
                    for node in nodes:
                        if node != start_node and node.is_over(event.pos):
                            input_port = node.get_input_port(event.pos)
                            if input_port is not None:
                                connections.append(Connection(start_node, node, start_port, input_port))
                            break
                    connecting = False
                    start_node = None
                    start_port = None

        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                selected_node.move(event.pos[0] - selected_node.rect.x + offset_x,
                                   event.pos[1] - selected_node.rect.y + offset_y)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                context_menu.hide()
                connecting = False
                start_node = None
                start_port = None

    screen.fill(WHITE)

    for connection in connections:
        connection.draw(screen)

    for node in nodes:
        node.draw(screen)

    if connecting:
        start_pos = (start_node.rect.right, 
                     start_node.rect.top + (start_port + 1) * start_node.rect.height / (len(start_node.outputs) + 1))
        pygame.draw.line(screen, BLUE, start_pos, pygame.mouse.get_pos(), 2)

    context_menu.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()
