import pygame
import sys
import random

# Inicialización de Pygame
pygame.init()

# Configuración de la pantalla
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Blueprint Interface")

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Clase Nodo
class Node:
    def __init__(self, x, y, width, height, name="Node", color=GRAY):
        self.rect = pygame.Rect(x, y, width, height)
        self.name = name
        self.color = color
        self.inputs = []
        self.outputs = []
        self.connections = []

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        font = pygame.font.Font(None, 24)
        text = font.render(self.name, True, BLACK)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)

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

    def add_input(self, name):
        self.inputs.append(name)

    def add_output(self, name):
        self.outputs.append(name)

    def is_over(self, pos):
        return self.rect.collidepoint(pos)

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

# Lista de nodos
nodes = []

# Lista de conexiones
connections = []

# Función para crear un nuevo nodo
def create_node(pos):
    color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
    node = Node(pos[0], pos[1], 150, 80, f"Node {len(nodes)}", color)
    node.add_input("In")
    node.add_output("Out")
    nodes.append(node)

# Variables para el arrastre de nodos
dragging = False
selected_node = None

# Creación de conexión
connecting = False
start_node = None
start_port = None

# Bucle principal
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Botón izquierdo
                for node in nodes:
                    if node.is_over(event.pos):
                        dragging = True
                        selected_node = node
                        offset_x = node.rect.x - event.pos[0]
                        offset_y = node.rect.y - event.pos[1]
                        break
                else:
                    # Si no se hizo clic en ningún nodo, crear uno nuevo
                    create_node(event.pos)
            elif event.button == 3:  # Botón derecho
                for node in nodes:
                    if node.is_over(event.pos):
                        connecting = True
                        start_node = node
                        # Determinar si se hizo clic en una entrada o salida
                        if event.pos[0] < node.rect.centerx:
                            start_port = (event.pos[1] - node.rect.top) // (node.rect.height // (len(node.inputs) + 1)) - 1
                        else:
                            start_port = (event.pos[1] - node.rect.top) // (node.rect.height // (len(node.outputs) + 1)) - 1
                        break
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Botón izquierdo
                dragging = False
                selected_node = None
            elif event.button == 3:  # Botón derecho
                if connecting:
                    for node in nodes:
                        if node.is_over(event.pos) and node != start_node:
                            if event.pos[0] < node.rect.centerx:
                                end_port = (event.pos[1] - node.rect.top) // (node.rect.height // (len(node.inputs) + 1)) - 1
                                connections.append(Connection(start_node, node, start_port, end_port))
                            else:
                                end_port = (event.pos[1] - node.rect.top) // (node.rect.height // (len(node.outputs) + 1)) - 1
                                connections.append(Connection(node, start_node, end_port, start_port))
                            break
                connecting = False
                start_node = None
        elif event.type == pygame.MOUSEMOTION:
            if dragging:
                selected_node.move(event.pos[0] - selected_node.rect.x + offset_x,
                                   event.pos[1] - selected_node.rect.y + offset_y)

    screen.fill(WHITE)

    # Dibujar conexiones
    for connection in connections:
        connection.draw(screen)

    # Dibujar nodos
    for node in nodes:
        node.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()
