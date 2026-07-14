import sys
import pygame
from button import *
from load_save_game_data import *
from game_state import *
from app_state import *

pygame.init()
pygame.display.set_caption('Chess')

from pieces import *

def create_buttons(cur_game_state, game_data):
    
    res = cur_game_state.res
    b_w, b_h = cur_game_state.b_w, cur_game_state.b_h
    
    b1 = Button(res[0]//2-b_w//2, res[1]*0.9-b_h, b_w, b_h, 'Play', play, args=[cur_game_state, game_data])
    b3 = Button(res[0]*0.65+250-20, res[1]*0.3, b_w, b_h, 'Sign up', handle_username_password)
    b4 = Button(res[0]*0.65+250-20, res[1]*0.3+b_h*2, b_w, b_h, 'Sign up', handle_username_password)
    b5 = Button(res[0]*0.65+250-20, res[1]*0.3, b_w, b_h, 'Log in', handle_username_password)
    b6 = Button(res[0]*0.65+250-20, res[1]*0.3+b_h*2, b_w, b_h, 'Log in', handle_username_password)
    
    return [b1, b3, b4, b5, b6]

try:
    game_data = open_game_data()
except FileNotFoundError:
    save_game_data({})
    game_data = open_game_data()

def main_loop():
    chess_game_state = GameState()
    
    buttons = create_buttons(chess_game_state, game_data)
    app_state = AppState(chess_game_state, buttons)
    
    print(game_data)
    app_state.run_app(game_data, chess_game_state)

main_loop()
