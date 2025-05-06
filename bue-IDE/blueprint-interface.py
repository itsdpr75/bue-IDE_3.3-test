import pygame
import sys

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

# Clase Nodo
class Node:
    def __init__(self, x, y, width, height, name="Node", color=GRAY):
        self.rect = pygame.Rect(x, y, width, height)
        self.name = name
        self.color = color
        self.inputs = []
        self.outputs = []

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        font = pygame.font.Font(None, 24)
        text = font.render(self.name, True, BLACK)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)

    def add_input(self, name):
        self.inputs.append(name)

    def add_output(self, name):
        self.outputs.append(name)

# Lista de nodos
nodes = [
    Node(100, 100, 150, 80, "Input Node"),
    Node(400, 200, 150, 80, "Process Node"),
    Node(600, 300, 150, 80, "Output Node")
]

# Agregar entradas y salidas de ejemplo
nodes[0].add_output("Out")
nodes[1].add_input("In")
nodes[1].add_output("Out")
nodes[2].add_input("In")

# Bucle principal
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(WHITE)

    # Dibujar nodos
    for node in nodes:
        node.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()
