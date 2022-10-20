import pygame

class Button():
    def __init__(self, x, y, width, height, text, functocall, secondary_fun=None, third_fun=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.func = functocall
        self.sec_fun = secondary_fun
        self.third_fun = third_fun
        self.font = pygame.font.SysFont('Arial', 31)

        self.colours = {
            "normal":pygame.Color("green"),
            "hover": pygame.Color("grey"),
        }
        
        self.sur = pygame.Surface((self.width, self.height))
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.butsurf = self.font.render(text, True, (20, 20, 20))


    def process(self, screen, restart_fun=None, fill_surface=True):
        if fill_surface:
            screen.fill(pygame.Color('black'))
        if self.sec_fun and self.third_fun:
            self.sec_fun()
            self.third_fun()
        mouse_pos = pygame.mouse.get_pos()
        self.sur.fill(self.colours['normal'])
        if self.rect.collidepoint(mouse_pos):
            self.sur.fill(self.colours['hover'])
            if pygame.mouse.get_pressed()[0]:
                if restart_fun:
                    restart_fun()
                self.func()

        self.sur.blit(self.butsurf,
            [self.rect.width/2 - self.butsurf.get_rect().width/2, self.rect.height/2 - self.butsurf.get_rect().height/2])
        screen.blit(self.sur, self.rect)