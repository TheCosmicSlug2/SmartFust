from email.mime import image
import random
from random import randint
import smartfust as sf
import pygame as pg

#texture1 = sf.load_texture(r"smartfust/rsc/celeste.png", smoothscale=0.1)

dic = {
    0: sf.Label((100, 50), (100, 30), "Label", (0, 0, 0), colors=[(0, 255, 255), (255, 255, 0)], text_height=15),
    1: sf.Button((100, 100), (100, 100), "Button QUIT", sf.GLOBAL_QUIT, (255, 255, 255), colors=[(0, 0, 0), (255, 0, 0)], animation={"size": (2, 2), "color": 6, "duration": 10}, text_height=13),
    2: sf.Checkbox((100, 220), (50, 50), colors=[(0, 150, 150), (150, 150, 0)], borders=[3]),
    3: sf.Entry((100, 300), (200, 30), inner_text="click here to change"),
    5: sf.Slider((400, 300), (100, 30)),
    6: sf.List((400, 100), (100, 30))
}



class Player:
    def __init__(self) -> None:
        self.posx = 0
        self.posy = 0
        self.texture = pg.Surface((20, 20))
        self.texture.fill(sf.BLACK)
    
    def update(self):
        keys = pg.key.get_pressed()

        if keys[pg.K_LEFT]:
            self.posx -= 10
        if keys[pg.K_RIGHT]:
            self.posx += 10
        if keys[pg.K_UP]:
            self.posy -= 10
        if keys[pg.K_DOWN]:
            self.posy += 10

    @property
    def pos(self):
        return self.posx, self.posy
    


def main():
    clock = pg.time.Clock()
    screen = pg.display.set_mode((600, 400))
    sf_display = sf.Display(screen)
    sf_display.add_widgets(dic)
    sf_display.set_bg("image", image_path="img.jpg")
    player = Player()

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
        
        if sf_display.widget_values()[1] == sf.GLOBAL_QUIT:
            running = False
        sf_display.change_widget(0, f"fps : {round(clock.get_fps(), 2)}")
        player.update()
        screen.fill((255, 255, 255))
        sf_display.update()
        screen.blit(player.texture, (player.pos))

        pg.display.flip()
        clock.tick(30)

main()

    # display.add_widgets(dic)
    # display.set_bg("custom", array=[[(0 + i)%3, (1 + i)%3, (2+i)%3] * 10 for i in range(30)], colors=((255, 0, 0), (0, 255, 0), (0, 0, 255)), shadow={"sign": (-1, 1),"mult": 10})
    # display.mainloop()

    # outputs = display.get_output()
    # for id, value in outputs.items():
    #     print(id, value)
