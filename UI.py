import pygame

pygame.init()

screen_width = 700
screen_height = 700
screen = pygame.display.set_mode((screen_width, screen_height))

pygame.display.set_caption("Blanka")

background = pygame.image.load('C:/Codes/ChessEngine/scr/images/board/maple.jpg')

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.blit(background, (0, 0))
    pygame.display.update()

