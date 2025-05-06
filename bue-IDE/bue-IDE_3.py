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
PANEL_BACKGROUND = (40, 40, 40)
PANEL_TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (100, 100, 100)
BUTTON_TEXT_COLOR = (255, 255, 255)

font = pygame.font.Font(None, 24)

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

class Panel:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH - 300, 0, 300, HEIGHT)
        self.visible = False
        self.selected_node = None
        self.name_input = ""
    
    def show(self, node):
        self.visible = True
        self.selected_node = node
        self.name_input = node.name

    def hide(self):
        self.visible = False
        self.selected_node = None
    
    def draw(self, surface):
        if self.visible and self.selected_node:
            pygame.draw.rect(surface, PANEL_BACKGROUND, self.rect)
            pygame.draw.rect(surface, NODE_OUTLINE, self.rect, 2)
            
            # Draw labels and inputs
            name_label = font.render("Name:", True, PANEL_TEXT_COLOR)
            surface.blit(name_label, (self.rect.x + 20, self.rect.y + 20))

            # Draw input field for name
            name_input_box = pygame.Rect(self.rect.x + 100, self.rect.y + 20, 180, 30)
            pygame.draw.rect(surface, BUTTON_COLOR, name_input_box)
            name_text = font.render(self.name_input, True, BUTTON_TEXT_COLOR)
            surface.blit(name_text, (name_input_box.x + 10, name_input_box.y + 5))

            # Draw button to add input
            add_input_button = pygame.Rect(self.rect.x + 20, self.rect.y + 70, 260, 30)
            pygame.draw.rect(surface, BUTTON_COLOR, add_input_button)
            input_text = font.render("Add Input", True, BUTTON_TEXT_COLOR)
            surface.blit(input_text, (add_input_button.x + 100, add_input_button.y + 5))

            # Draw button to add output
            add_output_button = pygame.Rect(self.rect.x + 20, self.rect.y + 120, 260, 30)
            pygame.draw.rect(surface, BUTTON_COLOR, add_output_button)
            output_text = font.render("Add Output", True, BUTTON_TEXT_COLOR)
            surface.blit(output_text, (add_output_button.x + 100, add_output_button.y + 5))

    def handle_event(self, event):
        if not self.visible or not self.selected_node:
            return
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if self.rect.collidepoint(mouse_pos):
                # Click on name input box
                if pygame.Rect(self.rect.x + 100, self.rect.y + 20, 180, 30).collidepoint(mouse_pos):
                    self.name_input = ""  # Reset the input text

                # Add input button
                elif pygame.Rect(self.rect.x + 20, self.rect.y + 70, 260, 30).collidepoint(mouse_pos):
                    self.selected_node.add_input()

                # Add output button
                elif pygame.Rect(self.rect.x + 20, self.rect.y + 120, 260, 30).collidepoint(mouse_pos):
                    self.selected_node.add_output()

        if event.type == pygame.KEYDOWN:
            # Typing in the name input box
            if event.key == pygame.K_BACKSPACE:
                self.name_input = self.name_input[:-1]
            else:
                self.name_input += event.unicode

            # Update the node's name
            if self.selected_node:
                self.selected_node.name = self.name_input

nodes = []
connections = []
panel = Panel()
camera = pygame.Rect(0, 0, WIDTH, HEIGHT)
dragging = False
connecting = False
selected_node = None

def create_node(pos):
    node = Node(pos[0], pos[1], 200, 150)
    nodes.append(node)

def draw_grid(surface):
    for x in range(0, WIDTH, 50):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, 50):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (WIDTH, y))

running = True
while running:
    screen.fill(BACKGROUND)
    draw_grid(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                for node in nodes:
                    if node.is_over(event.pos):
                        selected_node = node
                        panel.show(node)
                        break
                else:
                    panel.hide()

        panel.handle_event(event)

    for node in nodes:
        node.draw(screen)

    panel.draw(screen)
    pygame.display.flip()

pygame.quit()
sys.exit()
