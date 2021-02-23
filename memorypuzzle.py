"""Memory Puzzle Program"""

import random
import sys

import pygame
from pygame.locals import *

FPS = 30
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
REVEALSPEED = 8
BOXSIZE = 40
GAPSIZE = 10
BOARDWIDTH = 10
BOARDHEIGHT = 7
assert (BOARDWIDTH * BOARDHEIGHT) % 2 == 0, "Board needs to have an even number of boxes for pairs of matches."
XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH * (BOXSIZE + GAPSIZE))) / 2)
YMARGIN = int((WINDOWHEIGHT - (BOARDHEIGHT * (BOXSIZE + GAPSIZE))) / 2)

#       R    G    B
GRAY = (100, 100, 100)
NAVYBLUE = (60, 60, 100)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 128, 0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)

BGCOLOR = NAVYBLUE
LIGHTBGCOLOR = GRAY
BOXCOLOR = WHITE
HIGHLIGHTCOLOR = BLUE

DONUT = "donut"
SQUARE = "square"
DIAMOND = "diamond"
LINES = "lines"
OVAL = "oval"

ALLCOLORS = (RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, CYAN)
ALLSHAPES = (DONUT, SQUARE, DIAMOND, LINES, OVAL)
assert len(ALLCOLORS) * len(ALLSHAPES) * 2 >= BOARDWIDTH * BOARDHEIGHT, "Board is too big for the number of shapes/colors defined."


def main():
	"""

	:return:
	:rtype:
	"""
	global FPSCLOCK, DISPLAYSURF
	pygame.init()
	FPSCLOCK = pygame.time.Clock()
	DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

	mousex = 0
	mousey = 0
	pygame.display.set_caption("Memory Game")

	main_board = get_randomized_board()
	revealed_boxes = generate_revealed_boxes_data(False)

	first_selection = None

	DISPLAYSURF.fill(BGCOLOR)
	start_game_animation(main_board)

	while True:
		mouse_clicked = False

		DISPLAYSURF.fill(BGCOLOR)
		draw_board(main_board, revealed_boxes)

		for event in pygame.event.get():
			if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
				pygame.quit()
				sys.exit()
			elif event.type == MOUSEMOTION:
				mousex, mousey = event.pos
			elif event.type == MOUSEBUTTONUP:
				mousex, mousey = event.pos
				mouse_clicked = True

		boxx, boxy = get_box_at_pixel(mousex, mousey)
		if boxx != None and boxy != None:
			if not revealed_boxes[boxx][boxy]:
				draw_highlight_box(boxx, boxy)
			if not revealed_boxes[boxx][boxy] and mouse_clicked:
				reveal_boxes_animation(main_board, [(boxx, boxy)])
				revealed_boxes[boxx][boxy] = True
				if first_selection == None:
					first_selection = (boxx, boxy)
				else:
					icon1shape, icon1color = get_shape_and_color(
						main_board,
						first_selection[0],
						first_selection[1]
					)
					icon2shape, icon2color = get_shape_and_color(main_board, boxx, boxy)

					if icon1shape != icon2shape or icon1color != icon2color:
						pygame.time.wait(1000)
						cover_boxes_animation(main_board,
							[(first_selection[0], first_selection[1]), (boxx, boxy)])
						revealed_boxes[first_selection[0]][first_selection[1]] = False
						revealed_boxes[boxx][boxy] = False
					elif has_won(revealed_boxes):
						game_won_animation(main_board)
						pygame.time.wait(2000)

						main_board = get_randomized_board()
						revealed_boxes = generate_revealed_boxes_data(False)

						draw_board(main_board, revealed_boxes)
						pygame.display.update()
						pygame.time.wait(1000)

						start_game_animation(main_board)
					first_selection = None

		pygame.display.update()
		FPSCLOCK.tick(FPS)


def generate_revealed_boxes_data(val):
	"""

	:param val:
	:type val:
	:return:
	:rtype:
	"""
	revealed_boxes = []
	for i in range(BOARDWIDTH):
		revealed_boxes.append([val] * BOARDHEIGHT)
	return revealed_boxes


def get_randomized_board():
	"""

	:return:
	:rtype:
	"""
	icons = []
	for color in ALLCOLORS:
		for shape in ALLSHAPES:
			icons.append((shape, color))

	random.shuffle(icons)
	num_icons_used = int(BOARDWIDTH * BOARDHEIGHT / 2)
	icons = icons[:num_icons_used] * 2
	random.shuffle(icons)

	board = []
	for x in range(BOARDWIDTH):
		column = []
		for y in range(BOARDHEIGHT):
			column.append(icons[0])
			del icons[0]
		board.append(column)
	return board


def split_into_groups_of(group_size, the_list):
	"""

	:param group_size:
	:type group_size:
	:param the_list:
	:type the_list:
	:return:
	:rtype:
	"""
	result = []
	for i in range(0, len(the_list), group_size):
		result.append(the_list[i:i + group_size])
	return result


def left_top_coordinates_of_box(boxx, boxy):
	"""

	:param boxx:
	:type boxx:
	:param boxy:
	:type boxy:
	:return:
	:rtype:
	"""
	left = boxx * (BOXSIZE + GAPSIZE) + XMARGIN
	top = boxy * (BOXSIZE + GAPSIZE) + YMARGIN
	return left, top


def get_box_at_pixel(x, y):
	"""

	:param x:
	:type x:
	:param y:
	:type y:
	:return:
	:rtype:
	"""
	for boxx in range(BOARDWIDTH):
		for boxy in range(BOARDHEIGHT):
			left, top = left_top_coordinates_of_box(boxx, boxy)
			box_rect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
			if box_rect.collidepoint(x, y):
				return boxx, boxy
	return None, None


def draw_icon(shape, color, boxx, boxy):
	"""

	:param shape:
	:type shape:
	:param color:
	:type color:
	:param boxx:
	:type boxx:
	:param boxy:
	:type boxy:
	:return:
	:rtype:
	"""
	quarter = int(BOXSIZE * 0.25)
	half = int(BOXSIZE * 0.5)

	left, top = left_top_coordinates_of_box(boxx, boxy)
	if shape == DONUT:
		pygame.draw.circle(DISPLAYSURF, color, (left + half, top + half), half - 5)
		pygame.draw.circle(DISPLAYSURF, BGCOLOR, (left + half, top + half), quarter - 5)
	elif shape == SQUARE:
		pygame.draw.rect(DISPLAYSURF, color,
			(left + quarter, top + quarter, BOXSIZE - half, BOXSIZE - half))
	elif shape == DIAMOND:
		pygame.draw.polygon(DISPLAYSURF, color, (
		(left + half, top), (left + BOXSIZE - 1, top + half), (left + half, top + BOXSIZE - 1),
		(left, top + half)))
	elif shape == LINES:
		for i in range(0, BOXSIZE, 4):
			pygame.draw.line(DISPLAYSURF, color, (left, top + i), (left + i, top))
			pygame.draw.line(DISPLAYSURF, color, (left + i, top + BOXSIZE - 1),
				(left + BOXSIZE - 1, top + i))
	elif shape == OVAL:
		pygame.draw.ellipse(DISPLAYSURF, color, (left, top + quarter, BOXSIZE, half))


def get_shape_and_color(board, boxx, boxy):
	"""

	:param board:
	:type board:
	:param boxx:
	:type boxx:
	:param boxy:
	:type boxy:
	:return:
	:rtype:
	"""
	return board[boxx][boxy][0], board[boxx][boxy][1]


def draw_box_covers(board, boxes, coverage):
	"""

	:param board:
	:type board:
	:param boxes:
	:type boxes:
	:param coverage:
	:type coverage:
	:return:
	:rtype:
	"""
	for box in boxes:
		left, top = left_top_coordinates_of_box(box[0], box[1])
		pygame.draw.rect(DISPLAYSURF, BGCOLOR, (left, top, BOXSIZE, BOXSIZE))
		shape, color = get_shape_and_color(board, box[0], box[1])
		draw_icon(shape, color, box[0], box[1])
		if coverage > 0:
			pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, coverage, BOXSIZE))
	pygame.display.update()
	FPSCLOCK.tick(FPS)


def reveal_boxes_animation(board, boxes_to_reveal):
	"""

	:param board:
	:type board:
	:param boxes_to_reveal:
	:type boxes_to_reveal:
	:return:
	:rtype:
	"""
	for coverage in range(BOXSIZE, (-REVEALSPEED) - 1, -REVEALSPEED):
		draw_box_covers(board, boxes_to_reveal, coverage)


def cover_boxes_animation(board, boxes_to_cover):
	"""

	:param board:
	:type board:
	:param boxes_to_cover:
	:type boxes_to_cover:
	:return:
	:rtype:
	"""
	for coverage in range(0, BOXSIZE + REVEALSPEED, REVEALSPEED):
		draw_box_covers(board, boxes_to_cover, coverage)


def draw_board(board, revealed):
	"""

	:param board:
	:type board:
	:param revealed:
	:type revealed:
	:return:
	:rtype:
	"""
	for boxx in range(BOARDWIDTH):
		for boxy in range(BOARDHEIGHT):
			left, top = left_top_coordinates_of_box(boxx, boxy)
			if not revealed[boxx][boxy]:
				pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, BOXSIZE, BOXSIZE))
			else:
				shape, color = get_shape_and_color(board, boxx, boxy)
				draw_icon(shape, color, boxx, boxy)


def draw_highlight_box(boxx, boxy):
	"""

	:param boxx:
	:type boxx:
	:param boxy:
	:type boxy:
	:return:
	:rtype:
	"""
	left, top = left_top_coordinates_of_box(boxx, boxy)
	pygame.draw.rect(DISPLAYSURF, HIGHLIGHTCOLOR, (left - 5, top - 5, BOXSIZE + 10, BOXSIZE + 10),
		4)


def start_game_animation(board):
	"""

	:param board:
	:type board:
	:return:
	:rtype:
	"""
	covered_boxes = generate_revealed_boxes_data(False)
	boxes = []
	for x in range(BOARDWIDTH):
		for y in range(BOARDHEIGHT):
			boxes.append((x, y))
	random.shuffle(boxes)
	box_groups = split_into_groups_of(8, boxes)

	draw_board(board, covered_boxes)
	for boxGroup in box_groups:
		reveal_boxes_animation(board, boxGroup)
		cover_boxes_animation(board, boxGroup)


def game_won_animation(board):
	"""

	:param board:
	:type board:
	:return:
	:rtype:
	"""
	covered_boxes = generate_revealed_boxes_data(True)
	color1 = LIGHTBGCOLOR
	color2 = BGCOLOR

	for i in range(13):
		color1, color2 = color2, color1
		DISPLAYSURF.fill(color1)
		draw_board(board, covered_boxes)
		pygame.display.update()
		pygame.time.wait(300)


def has_won(revealed_boxes):
	"""

	:param revealed_boxes:
	:type revealed_boxes:
	:return:
	:rtype:
	"""
	for i in revealed_boxes:
		if False in i:
			return False
	return True


if __name__ == "__main__":
	main()
