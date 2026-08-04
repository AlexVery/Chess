from button import *
from helper_functions import *

class AppState():
    def __init__(self, cur_game_state, buttons):
        self.valid_usernames = [False, False]
        self.box1_active, self.box2_active = False, False
        
        self.play_button, self.sign_up_p1_button, self.sign_up_p2_button, self.log_in_p1_button, self.log_in_p2_button = buttons
        
        self.display_text_usrnms = DisplayText("Usernames must be different! Users must be distinct!", 24, cur_game_state.res[0], 
                                               0.6*cur_game_state.res[1], pygame.Color("red"), backgr_color=pygame.Color("white"))
        
        self.valid_codes = [False, False]     # either through registration or log in
        
    def handle_login_signup(self, cur_game_state, game_data, event_list, username1, username2):
        
        if cur_game_state.first_time or (not self.play_button.pressed) or (not all(self.valid_usernames)):
            username1, username2, self.valid_usernames, self.box1_active, self.box2_active = username_input(cur_game_state, username1, username2, event_list, self)
            # the two usernames must be different, if a user using the username "Jim23" is logged in, no other log in
            # of the same username must be permitted
            different_usernames = username1 != username2
            # if the usernames are the same and they are both different than the empty string, display the error message
            self.display_text_usrnms.update((not different_usernames) and all([len(item) > 0 for item in (username1, username2)]))
            self.play_button.update(event_list, blocked=not all(self.valid_codes))
            active_user_buttons = [self.sign_up_p1_button if (self.valid_usernames[0] and (username1 not in game_data)) else self.log_in_p1_button, 
                                    self.sign_up_p2_button if (self.valid_usernames[1] and (username2 not in game_data)) else self.log_in_p2_button]
            for i, (valid_code, button, usrnm, valid_usrnm) in enumerate(zip(self.valid_codes, active_user_buttons, [username1, username2], self.valid_usernames)):
                if valid_usrnm and (not valid_code) and different_usernames:
                    button.args = [usrnm, game_data, cur_game_state]
                    button.update(event_list)
                    valid_registration = button.return_vals
                    self.valid_codes[i] = valid_registration[0] if (valid_registration is not None) else False
                    if (valid_registration is not None) and valid_registration[0]:
                        game_data[usrnm] = valid_registration[-1]
                        cur_game_state.save_username(i, usrnm)
                    button.draw(cur_game_state.screen)
            
            self.display_text_usrnms.draw(cur_game_state.screen)
            
        return username1, username2
    
    def reset_state_main_menu(self, cur_game_state):
        cur_game_state.first_time = True
        self.play_button.pressed = False
        self.play_button.return_vals = None
        
        self.box1_active, self.box2_active = False, False
        self.valid_usernames = [False, False]
        self.valid_codes = [False, False]
        
        username1 = ""
        username2 = ""
        
        return username1, username2      
        
    def run_app(self, game_data, cur_game_state):
        
        username1, username2 = cur_game_state.username1, cur_game_state.username2
        
        while True:
            white_won = None
            
            cur_game_state.clock.tick(60)
            
            event_list = pygame.event.get()
            for event in event_list:
                if event.type == pygame.QUIT:
                    cur_game_state.save_game_data(game_data)
                    pygame.quit()
                    sys.exit()
            
            username1, username2 = self.handle_login_signup(cur_game_state, game_data, event_list, username1, username2)
                
            if (not self.play_button.pressed) and (all(self.valid_codes)): self.play_button.draw(cur_game_state.screen)
            
            # the Button class has an attribute return_vals (can be seen in button.py) that stores the
            # values returned by the function it calls. For example self.play_button is the 'Play' button, and when
            # pressed calls the play function, which return -1, 0 or 1.
            white_won = self.play_button.return_vals # -1 = black won, 1 = white won, 0 draw: return value of play function
            if white_won == "R":
                username1, username2 = self.reset_state_main_menu(cur_game_state)
                continue
            
            cur_game_state.store_h2h_data(game_data, username1, username2, white_won)
            
            if not cur_game_state.first_time:
                return_val = try_again(cur_game_state, game_data, (username1, username2))
                if return_val == -1:
                    cur_game_state.save_game_data(game_data)
                    pygame.quit()
                    sys.exit()  
                elif return_val == 0:
                    username1, username2 = self.reset_state_main_menu(cur_game_state)
                elif return_val == 1:
                    white_won = play(cur_game_state, game_data)
                    if white_won == "R":
                        username1, username2 = self.reset_state_main_menu(cur_game_state)
                        continue
                    cur_game_state.store_h2h_data(game_data, username1, username2, white_won)
                
            pygame.display.flip()
