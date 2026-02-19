import pygame
import time

pygame.init()

# Load the splash screen image
logo = pygame.image.load('logo.jpg')

# Resize the image
logo = pygame.transform.scale(logo, (400, 300))

# Create Window
screen = pygame.display.set_mode((400, 300), pygame.NOFRAME)

# Draw 
screen.blit(logo, (0, 0))
pygame.display.flip()

# Wait for 3 seconds
time.sleep(3)

# Quit Pygame
pygame.quit()