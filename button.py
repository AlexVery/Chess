import pygame

class Button():
    def __init__(self, x, y, width, height, text, functocall, args=None):
        self.x = x
        self.y = y
        self.text = text
        self.pressed = False
        self.hover = False
        self.width = width
        self.height = height
        # func = function to call when button is pressed
        self.func = functocall
        self.args = args
        self.font = pygame.font.SysFont('Arial', 31)
        self.return_vals = None

        self.colours = {
            "normal":pygame.Color("green"),
            "hover": pygame.Color("grey"),
        }
        
        self.sur = pygame.Surface((self.width, self.height))
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.butsurf = self.font.render(text, True, (20, 20, 20))

    def update(self, events, callback=None, blocked=False):
        if blocked: return
        
        if callback is not None:
            callback()
            
        self.hover = self.rect.collidepoint(pygame.mouse.get_pos())
        
        for event in events:
            if (event.type == pygame.MOUSEBUTTONDOWN) and (event.button == 1) and self.hover:
                self.pressed = True
                if self.args is None:
                    self.return_vals = self.func()
                    break
                else:
                    self.return_vals = self.func(*self.args)
                    break
                
    def draw(self, screen):
        
        self.sur.fill(self.colours['normal'])
        color = self.colours["hover"] if self.hover else self.colours["normal"]
        self.sur.fill(color)
        
        self.sur.blit(self.butsurf,
            [self.rect.width/2 - self.butsurf.get_rect().width/2, self.rect.height/2 - self.butsurf.get_rect().height/2])
        screen.blit(self.sur, self.rect)
        
        
