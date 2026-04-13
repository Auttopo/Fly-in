
from ursina import *
import parser as FP
from ursina.prefabs.first_person_controller import FirstPersonController
from typing import Any

def get_colors() -> dict[tuple[int, int, int]]:
    return {
    "red": (220, 30, 30),
    "blue": (30, 100, 220),
    "green": (34, 139, 34),
    "yellow": (220, 210, 30),
    "orange": (220, 120, 30),
    "purple": (120, 30, 180),
    "pink": (220, 100, 150),
    "brown": (101, 67, 33),
    "black": (20, 20, 20),
    "white": (240, 240, 240),
    "grey": (130, 130, 130),
    "violet": (138, 43, 226),
    "cyan": (30, 200, 210),
    "lime": (50, 205, 50),
    "magenta": (210, 30, 210),
    "gold": (212, 175, 55),
    "maroon": (88, 20, 20),
    "darkred": (139, 0, 0),
    "crimson": (180, 20, 45),
    "rainbow": (255, 255, 255),
    "beige": (210, 180, 140),}

class InputHandler(Entity):

    def __init__(self, player: Any, nods: list[Any]) -> None:
        super().__init__()
        self.player = player
        self.nods = nods

    def input(self, key: Any) -> None:
        if key == 'escape':
            application.quit()
        if key == 'o':
            for nod in self.nods:
                nod.visible = not nod.visible

    def update(self):
        if held_keys['space']:
            self.player.y += 5 * time.dt
        if held_keys['shift']:
            self.player.y -= 5 * time.dt


class FlyinDisplay:

    def __init__(self, mydata: list[str]) -> None:
        """ init and display the graph """
        mycolors = get_colors()

        app = Ursina()

        # sol
        ground = Entity(
            model='plane',
            scale=100,
            texture='grass',
            texture_scale=(50, 50),
            collider='box'
        )
        
        nods: list[Any] = []
        for elem in mydata:
            x,y = elem[FP.XY]
            col = mycolors[elem[FP.COLOR]]
            nod = Entity(
                model='sphere',

                color=color.rgb(col[0] / 255, col[1] / 255, col[2] / 255),
                position=(x * 6, 1, y * 6)
            )
            nods.append(nod)

        for elem in mydata:
            x,y = elem[FP.XY]
            drones = elem[FP.DRONES]
            if drones:
                txt = Entity(position=(x * 6, 2.5, y * 6), billboard=True)
                Text(text=str(drones), parent=txt, scale=20, origin=(0,0))

                drones_balls = Entity(
                    model='sphere',
                    world_space=True,
                    scale=0.3,
                    texture='shore',
                    position=(x * 6, 2.2, y * 6)
                )


        Sky()

        window.exit_button.visible = False

        # joueur FPS
        player = FirstPersonController()
        player.gravity = 0
        InputHandler(player, nods) 
        app.run()
    
