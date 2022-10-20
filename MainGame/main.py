import sys
import pygame
from button import *
from pieces import *
from settings import *

black_king_pos = (4, 0)
white_king_pos = (4, 7)

class block():
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = [color]

pygame.init()
pygame.display.set_caption('Chess')

black_piece_images = ['bK.png', 'bQ.png', 'bR.png', 'bB.png', 'bN.png', 'bp.png']
white_piece_images = ['wK.png', 'wQ.png', 'wR.png', 'wB.png', 'wN.png', 'wp.png']

pieces = ['king', 'queen', 'rook', 'bishop', 'knight', 'pawn']

to_place = {'r' + pieces[2]: (black_piece_images[2], white_piece_images[2], rook), 
            'r' + pieces[4]: (black_piece_images[4], white_piece_images[4], knight), 
            'r' + pieces[3]: (black_piece_images[3], white_piece_images[3], bishop), 
            pieces[1]: (black_piece_images[1], white_piece_images[1], queen), 
            pieces[0]: (black_piece_images[0], white_piece_images[0], king), 
            'l' + pieces[3]: (black_piece_images[3], white_piece_images[3], bishop), 
            'l' + pieces[4]: (black_piece_images[4], white_piece_images[4], knight), 
            'l' + pieces[2]: (black_piece_images[2], white_piece_images[2], rook)}

white_captured_piece = {'pawn' : [pygame.image.load(white_piece_images[-1]).convert_alpha(), 0], 
                        'knight' : [pygame.image.load(white_piece_images[4]).convert_alpha(), 0], 
                        'bishop' : [pygame.image.load(white_piece_images[3]).convert_alpha(), 0], 
                        'rook' : [pygame.image.load(white_piece_images[2]).convert_alpha(), 0], 
                        'queen' : [pygame.image.load(white_piece_images[1]).convert_alpha(), 0]}

black_captured_piece = {'pawn' : [pygame.image.load(black_piece_images[-1]).convert_alpha(), 0], 
                        'knight' : [pygame.image.load(black_piece_images[4]).convert_alpha(), 0], 
                        'bishop' : [pygame.image.load(black_piece_images[3]).convert_alpha(), 0], 
                        'rook' : [pygame.image.load(black_piece_images[2]).convert_alpha(), 0], 
                        'queen' : [pygame.image.load(black_piece_images[1]).convert_alpha(), 0]}

screen.fill(pygame.Color('white'))
font1 = pygame.font.SysFont('Arial', 30)
font = pygame.font.SysFont('Arial', 15)

def draw_images_of_captured():
    pygame.draw.rect(screen, pygame.Color('burlywood4'), (800, 0, 200, 800))

    j = 0
    for wp in white_captured_piece:
        im = pygame.transform.scale(white_captured_piece[wp][0], (40, 40))
        screen.blit(im, (820, 30 + 50 * j))
        j += 1

    j = 0
    for wp in black_captured_piece:
        im = pygame.transform.scale(black_captured_piece[wp][0], (40, 40))
        screen.blit(im, (910, 30 + 50 * j))
        j += 1

def draw_captured():
    draw_images_of_captured()
    for c in enumerate(white_captured_piece):
        text = font.render(f'{white_captured_piece[c[1]][1]}', True, pygame.Color('white'))
        screen.blit(text, (870, 40 + 50 * c[0]))
        
    for c in enumerate(black_captured_piece):
        text = font.render(f'{black_captured_piece[c[1]][1]}', True, pygame.Color('white'))
        screen.blit(text, (960, 40 + 50 * c[0]))

def change_captured(pos):
    color = board_pieces[pos].color
    captured = white_captured_piece if color == 'white' else black_captured_piece
    if board_pieces[pos].name == 'queen' or board_pieces[pos].name == 'pawn':
        captured[board_pieces[pos].name][1] += 1
    else:
        captured[board_pieces[pos].name[1:]][1] += 1

clock = pygame.time.Clock()

def create_and_place_pieces():
    global white_king_pos, black_king_pos
    board_pieces.clear()
    position_of_black_pieces.clear()
    position_of_white_pieces.clear()
    for i in range(8):
            start = 100 if i % 2 == 0 else 0
            left_for_white = start - 100 if start else start + 100
            for j in range(4):
                if i % 2 == 0:
                    block_list[i].append(block(left_for_white, i*100, 100, 100, pygame.Color('white')))
                    block_list[i].append(block(start, i*100, 100, 100, pygame.Color('grey30')))
                else:
                    block_list[i].append(block(start, i*100, 100, 100, pygame.Color('grey30')))
                    block_list[i].append(block(left_for_white, i*100, 100, 100, pygame.Color('white')))
                start += 200
                left_for_white += 200

    for i in range(8):
        p1 = pawn(i, 1, pygame.image.load(black_piece_images[-1]).convert_alpha(), 'black', 'pawn')
        p2 = pawn(i, 6, pygame.image.load(white_piece_images[-1]).convert_alpha(), 'white', 'pawn')
        board_pieces[(i,1)] = p1
        board_pieces[(i,6)] = p2
        position_of_black_pieces.add((i, 1))
        position_of_white_pieces.add((i, 6))

    i = 0
    for name in to_place:
        p1 = to_place[name][2](i, 0, pygame.image.load(to_place[name][0]).convert_alpha(), 'black', name)
        if p1.name == 'king':
            black_king_pos = (i, 0)
        p2 = to_place[name][2](i, 7, pygame.image.load(to_place[name][1]).convert_alpha(), 'white', name)
        if p2.name == 'king':
            white_king_pos = (i,7)
        board_pieces[(i,0)] = p1
        board_pieces[(i,7)] = p2
        position_of_black_pieces.add((i, 0))
        position_of_white_pieces.add((i, 7))
        i += 1

    for row in block_list:
        for column in row:
            pygame.draw.rect(screen, column.color[-1], column.rect)

    for p in board_pieces:
        screen.blit(board_pieces[p].image, (board_pieces[p].i * 100 + 15, board_pieces[p].j * 100 + 15))
        board_pieces[p].rect = board_pieces[p].image.get_rect()
        board_pieces[p].rect.topleft = (board_pieces[p].i * 100 + 15, board_pieces[p].j * 100 + 15)
        board_pieces[p].find_moves(black_king_pos, white_king_pos)

def play():
    global black_king_pos, white_king_pos, first_time
    draw_captured()
    draw(black_king_pos, white_king_pos)

    moves = 0
    events_list = []
    count = 0
    while True:
        clock.tick(60)
        event_list = pygame.event.get()
        for event in event_list:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                events_list.append(mouse_pos)
                if len(events_list) == 1:
                    for bp in available_pieces(count):
                        if board_pieces[bp].rect.collidepoint(mouse_pos):
                            pam = print_available_moves(board_pieces[bp])
                            moves = (pam, board_pieces[bp])
                            break
                    else:
                        events_list.clear()
                if len(events_list) == 2:
                    for b in moves[0]:
                        if b.rect.collidepoint(events_list[-1]):
                        
                            count += 1
                        
                            position_of_same_color_pieces = position_of_black_pieces if moves[1].color == 'black' else position_of_white_pieces
                            position_of_opposite_color_pieces = position_of_black_pieces if moves[1].color == 'white' else position_of_white_pieces
                            position_of_same_color_pieces.remove((moves[1].i, moves[1].j))
                            set_move(moves[1], events_list[-1][0]//100, events_list[-1][1]//100, black_king_pos, white_king_pos)
                        
                            if (events_list[-1][0]//100, events_list[-1][1]//100) in position_of_opposite_color_pieces:
                                position_of_opposite_color_pieces.remove((events_list[-1][0]//100, events_list[-1][1]//100))
                                change_captured((events_list[-1][0]//100, events_list[-1][1]//100))
                            position_of_same_color_pieces.add((moves[1].i, moves[1].j))
                            board_pieces[(events_list[-1][0]//100, events_list[-1][1]//100)] = board_pieces[bp]
                            del board_pieces[bp]

                            if board_pieces[(events_list[-1][0]//100, events_list[-1][1]//100)].name == 'king':
                                if board_pieces[(events_list[-1][0]//100, events_list[-1][1]//100)].color == 'black':
                                    black_king_pos = (board_pieces[(events_list[-1][0]//100, events_list[-1][1]//100)].i, board_pieces[(events_list[-1][0]//100, events_list[-1][1]//100)].j)
                                elif board_pieces[(events_list[-1][0]//100, events_list[-1][1]//100)].color == 'white':
                                    white_king_pos = (board_pieces[(events_list[-1][0]//100, events_list[-1][1]//100)].i, board_pieces[(events_list[-1][0]//100, events_list[-1][1]//100)].j)

                            events_list.clear()

                            for b in board_pieces:
                                board_pieces[b].find_moves(black_king_pos, white_king_pos)

                            is_king_checked(board_pieces[black_king_pos])
                            is_king_checked(board_pieces[white_king_pos])
                            board_pieces[black_king_pos].update_moves()
                            board_pieces[white_king_pos].update_moves()
                            
                            if board_pieces[white_king_pos].is_checked:
                                find_pieces_if_king_is_checked(board_pieces[white_king_pos], black_king_pos, white_king_pos)
                            if board_pieces[black_king_pos].is_checked:
                                find_pieces_if_king_is_checked(board_pieces[black_king_pos], black_king_pos, white_king_pos)
                        
                            num = num_of_pieces_with_moves(board_pieces[white_king_pos])
                            num2 = num_of_pieces_with_moves(board_pieces[black_king_pos])

                            if not num2 and board_pieces[black_king_pos].is_checked and not board_pieces[black_king_pos].moves:
                                draw(black_king_pos, white_king_pos)
                                first_time = False
                                return 
                            if not num and board_pieces[white_king_pos].is_checked and not board_pieces[white_king_pos].moves:
                                draw(black_king_pos, white_king_pos)
                                first_time = False
                                return 

                            draw(black_king_pos, white_king_pos)
                            draw_captured()
                            
                            break
                        
                    else:
                        events_list.clear()
                        draw(black_king_pos, white_king_pos)

        pygame.display.flip()
    
b1 = Button(300, 650, 100, 50, 'Play', play)
b2 = Button(825, 650, 100, 50, 'Try Again', play)
first_time = True

def main_loop():
    while True:
        clock.tick(60)
        event_list = pygame.event.get()
        for event in event_list:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if first_time:
            b1.process(screen, create_and_place_pieces, fill_surface=True)
        if not first_time:
            b2.process(screen, create_and_place_pieces, fill_surface=False)
        pygame.display.flip()

main_loop()
