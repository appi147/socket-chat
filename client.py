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
input_font = pygame.font.SysFont("Comic Sans MS", 10)
clock = pygame.time.Clock()
display_box = pygame.Rect(10, 10, 480, 420)
input_box = pygame.Rect(10, 450, 480, 40)
color_inactive = pygame.Color('grey')
color_active = pygame.Color('black')
color = color_inactive
active = False
text = ''

full_text = []

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


def multiLineSurface(input_lines: List, rect: pygame.rect.Rect):
    """https://stackoverflow.com/a/32624909/6771356
    Returns a surface containing the passed text string, reformatted
    to fit within the given rect, word-wrapping as necessary. The text
    will be anti-aliased.

    Parameters
    ----------
    requestedLines - List of tuple
    rect - a rect style giving the size of the surface requested.

    Returns
    -------
    Success - a surface object with the text rendered onto it.
    Failure - raises a TextRectException if the text won't fit onto the surface.
    """

    msg_font = pygame.font.SysFont("Comic Sans MS", 10)

    processed_lines = []
    for line in input_lines:
        final_lines = []
        if msg_font.size(line[2])[0] > rect.width:
            words = line.split(' ')
            # if any of our words are too long to fit, return.
            for word in words:
                if msg_font.size(word)[0] >= rect.width:
                    raise TextRectException(
                        f"The word {word} is too long to fit in the rect passed.")
            # Start a new line
            accumulated_line = ""
            for word in words:
                test_line = accumulated_line + word + " "
                # Build the line while the words fit.
                if msg_font.size(test_line)[0] < rect.width:
                    accumulated_line = test_line
                else:
                    final_lines.append(accumulated_line)
                    accumulated_line = word + " "
            final_lines.append(accumulated_line)
        else:
            final_lines.append(line[2])
        processed_lines.append((line[0], line[1], final_lines))

    return process_surface(processed_lines, rect, msg_font)


def process_surface(processed_lines, rect, msg_font):
    title_font = pygame.font.SysFont("Comic Sans MS", 10)
    font_color, bg_color = (0, 0, 0), (255, 255, 255)
    surface = pygame.Surface(rect.size)
    surface.fill(bg_color)

    accumulated_height = 0
    for processed_line in processed_lines:
        title_surface = title_font.render(processed_line[1], True, font_color)
        if processed_line[0] != player_id:
            surface.blit(title_surface, (0, accumulated_height))
        else:
            surface.blit(title_surface, (rect.width -
                                         title_surface.get_width(), accumulated_height))

        accumulated_height += title_font.size(processed_line[1])[1]
        for line in processed_line[2]:
            if accumulated_height + msg_font.size(line)[1] >= rect.height:
                raise TextRectException(
                    "Once word-wrapped, the text string was too tall to fit in the rect.")
            if line != "":
                tempSurface = msg_font.render(line, True, font_color)
            if processed_line[0] != player_id:
                surface.blit(tempSurface, (0, accumulated_height))
            else:
                surface.blit(tempSurface, (rect.width -
                                           tempSurface.get_width(), accumulated_height))
            accumulated_height += msg_font.size(line)[1]

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
            full_text.append((event[1], event[2], event[3]))

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
    txt_surface = input_font.render(text, True, color)
    incoming_surface = multiLineSurface(full_text[-17:], display_box)

    screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
    screen.blit(incoming_surface, (display_box.x + 1, display_box.y + 1))

    pygame.draw.rect(screen, color, input_box, 2)

    pygame.display.flip()
    clock.tick(30)


print("Bye Bye!!")
pygame.quit()
s.close()
sys.exit()
