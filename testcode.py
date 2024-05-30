import pygame

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Display Image Example")

# Load the image
image = pygame.image.load("images/dawn.jpg")

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))  # Fill the screen with white
    screen.blit(image, (100, 100))  # Blit the image at (100, 100)
    pygame.display.flip()  # Update the display

pygame.quit()
