import sys
import socket
import select
import pickle
from typing import List
import pygame

BUFFERSIZE = 2048
WIDTH = 500
HEIGHT = 500

name = input("Enter your name: ")

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(f"Chatting as {name}")
font = pygame.font.SysFont("Comic Sans MS", 10)
clock = pygame.time.Clock()
display_box = pygame.Rect(10, 10, 480, 250)
output_box = pygame.Rect(10, 270, 480, 170)
input_box = pygame.Rect(10, 450, 480, 40)
color_inactive = pygame.Color('grey')
color_active = pygame.Color('black')
color = color_inactive
active = False
text = ''
full_text_incoming = []
full_text_outgoing = []

server_addr = "127.0.0.1"
if len(sys.argv) == 2:
    serverAddr = sys.argv[1]
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((server_addr, 4321))

player_id = 0


class TextRectException:
    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        return self.message


def multiLineSurface(requestedLines: List, font: pygame.font.Font, rect: pygame.rect.Rect, fontColour: tuple, BGColour: tuple, justification=0):
    """https://stackoverflow.com/a/32624909/6771356
    Returns a surface containing the passed text string, reformatted
    to fit within the given rect, word-wrapping as necessary. The text
    will be anti-aliased.

    Parameters
    ----------
    requestedLines - List of lines
    font - a Font object
    rect - a rect style giving the size of the surface requested.
    fontColour - a three-byte tuple of the rgb value of the
             text color. ex (0, 0, 0) = BLACK
    BGColour - a three-byte tuple of the rgb value of the surface.
    justification - 0 (default) left-justified
                1 horizontally centered
                2 right-justified

    Returns
    -------
    Success - a surface object with the text rendered onto it.
    Failure - raises a TextRectException if the text won't fit onto the surface.
    """

    finalLines = []
    # Create a series of lines that will fit on the provided
    # rectangle.
    for requestedLine in requestedLines:
        if font.size(requestedLine)[0] > rect.width:
            words = requestedLine.split(' ')
            # if any of our words are too long to fit, return.
            for word in words:
                if font.size(word)[0] >= rect.width:
                    raise TextRectException(
                        "The word " + word + " is too long to fit in the rect passed.")
            # Start a new line
            accumulatedLine = ""
            for word in words:
                testLine = accumulatedLine + word + " "
                # Build the line while the words fit.
                if font.size(testLine)[0] < rect.width:
                    accumulatedLine = testLine
                else:
                    finalLines.append(accumulatedLine)
                    accumulatedLine = word + " "
            finalLines.append(accumulatedLine)
        else:
            finalLines.append(requestedLine)

    # Let's try to write the text out on the surface.
    surface = pygame.Surface(rect.size)
    surface.fill(BGColour)
    accumulatedHeight = 0

    for line in finalLines:
        if accumulatedHeight + font.size(line)[1] >= rect.height:
            raise TextRectException(
                "Once word-wrapped, the text string was too tall to fit in the rect.")
        if line != "":
            tempSurface = font.render(line, True, fontColour)
        if justification == 0:
            surface.blit(tempSurface, (0, accumulatedHeight))
        elif justification == 1:
            surface.blit(
                tempSurface, ((rect.width - tempSurface.get_width()) / 2, accumulatedHeight))
        elif justification == 2:
            surface.blit(tempSurface, (rect.width -
                                       tempSurface.get_width(), accumulatedHeight))
        else:
            raise TextRectException(
                "Invalid justification argument: " + str(justification))
        accumulatedHeight += font.size(line)[1]
    return surface


running = True
while running:
    ins, outs, ex = select.select([s], [], [], 0)
    for inm in ins:
        event = pickle.loads(inm.recv(BUFFERSIZE))
        if event[0] == "id update":
            player_id = event[1]
            s.send(pickle.dumps(["new", player_id, name]))
        elif event[0] == "message":
            if event[1] != player_id:
                full_text_incoming.append(event[2])
            else:
                full_text_outgoing.append(event[2])

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rectangle
            if input_box.collidepoint(event.pos):
                # Toggle the active variable.
                active = not active
            else:
                active = False
            # Change the current color of the input box.
            color = color_active if active else color_inactive
        if event.type == pygame.KEYDOWN:
            if active:
                if event.key == pygame.K_RETURN:
                    s.send(pickle.dumps(["message", player_id, text]))
                    text = ''
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    text += event.unicode

    screen.fill((255, 255, 255))
    txt_surface = font.render(text, True, color)
    incoming_surface = multiLineSurface(full_text_incoming[-17:], font, display_box,
                                        (0, 0, 0), (255, 255, 255), 0)

    outgoing_surface = multiLineSurface(full_text_outgoing[-11:], font, output_box,
                                        (0, 0, 0), (255, 255, 255), 2)

    screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
    screen.blit(incoming_surface, (display_box.x + 1, display_box.y + 1))
    screen.blit(outgoing_surface, (output_box.x + 1, output_box.y + 1))

    pygame.draw.rect(screen, color, input_box, 2)
    # pygame.draw.rect(screen, color, display_box, 2)
    # pygame.draw.rect(screen, color, output_box, 2)


    pygame.display.flip()
    clock.tick(30)


print("Bye Bye!!")
pygame.quit()
s.close()
sys.exit()
