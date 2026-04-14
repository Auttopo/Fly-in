
from ursina import *
import parser as FP
from ursina.prefabs.first_person_controller import FirstPersonController
from typing import Any
import numpy as np


def arc_entity(x1, y1, z1, x2, y2, z2, bulge=0.2, n=50, **kwargs):
    dx, dz = x2 - x1, z2 - z1  # plan XZ
    d = np.sqrt(dx**2 + dz**2)
    
    if abs(bulge) < 0.01 or d < 0.0001:
        verts = [Vec3(x1, y1, z1), Vec3(x2, y2, z2)]
        return Entity(model=Mesh(vertices=verts, mode='line', thickness=2), **kwargs)
    
    h = bulge * d / 2
    r = (d**2 / 4 + h**2) / (2 * h)
    mx, mz = (x1 + x2) / 2, (z1 + z2) / 2
    px, pz = -dz / d, dx / d          # perpendiculaire dans XZ
    cx = mx + (r - h) * px
    cz = mz + (r - h) * pz
    angle1 = np.arctan2(z1 - cz, x1 - cx)
    angle2 = np.arctan2(z2 - cz, x2 - cx)
    if bulge > 0 and angle2 < angle1:
        angle2 += 2 * np.pi
    if bulge < 0 and angle2 > angle1:
        angle2 -= 2 * np.pi
    angles = np.linspace(angle1, angle2, n)

    # Y monte en cloche au milieu
    ys = np.sin(np.linspace(0, np.pi, n)) * bulge * d + y1

    verts = [Vec3(cx + r * np.cos(a), y, cz + r * np.sin(a)) for a, y in zip(angles, ys)]
    return Entity(model=Mesh(vertices=verts, mode='line', thickness=2), **kwargs)

def get_colors() -> dict[tuple[int, int, int]]:
    data = {
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
    for elem in data.keys():
        data[elem] = (data[elem][0] / 255, data[elem][1] / 255, data[elem][2] / 255)
    return data

def get_type_color() -> dict[tuple[int, int, int]]:
    return {
            "priority": (220 / 255, 220 / 255, 220 / 255), # white
            "restricted": (0, 0, 0), # black
            "normal": (110 / 255, 110 / 255, 110 / 255), # grey
            "blocked": (220 / 255, 15 / 255, 15 / 255), # red
            }

class InputHandler(Entity):

    def __init__(self, player: Any, nods: list[Any], nods_dist: list[Any]) -> None:
        super().__init__()
        self.player = player
        self.nods = nods
        self.nods_dist = nods_dist

    def input(self, key: Any) -> None:
        if key == 'escape':
            application.quit()
        if key == 'o':
            for nod in self.nods:
                nod.visible = not nod.visible
        if key == 'o':
            for nod in self.nods_dist:
                nod.visible = not nod.visible

    def update(self):
        if held_keys['space']:
            self.player.y += 5 * time.dt
        if held_keys['shift']:
            self.player.y -= 5 * time.dt


class FlyinDisplay:


    def show_dist(self) -> None:
        pass

    
    def show_state(self) -> Any:

        mycolors = get_colors()
        mycolors_dist = get_type_color()
        self.nods: list[Any] = []
        self.nods_dist: list[Any] = []
        self.mydata = self.origin_data[0]

        link_h:int = 3
        espace = 8
        arcs_list: list[Any] = []

        for elem in self.mydata.all_data:
        # COLORED BASIC HUBS
            x,y = elem[FP.XY]
            x = x * espace
            y = y * espace
            col = mycolors[elem[FP.COLOR]]
            nod = Entity(
                model='sphere',

                color=color.rgb(col[0], col[1], col[2]),
                position=(x, 1, y)
            )

            str_dist = str(elem[FP.DIST])
            dist = Entity(position=(x, 2.5, y), billboard=True)
            Text(text=str_dist, parent=dist, scale=20, origin=(0,0))

            self.nods.append(nod)


        # ZONE TYPE COLOR HUBS
            col = mycolors_dist[elem[FP.ZONE]]
            nod = Entity(
                model='sphere',

                color=color.rgb(col[0], col[1], col[2]),
                position=(x, 1, y)
            )

            str_dist = str(elem[FP.DIST])
            dist = Entity(position=(x, 2.5, y), billboard=True)
            Text(text=str_dist, parent=dist, scale=20, origin=(0,0))
            nod.visible = not nod.visible

            self.nods_dist.append(nod)
        
        # DIST NBR AND LINES

            for link in elem[FP.LINK]:
                x2, y2 = link[FP.XY]
                arcs_list.append(arc_entity(x, link_h, y, x2 * espace, 1, y2 * espace))

            drones = elem[FP.DRONES]
            if drones:
                txt = Entity(position=(x, 3.2, y), billboard=True)
                Text(text=str(drones), parent=txt, scale=20, origin=(0,0))

                drones_balls = Entity(
                    model='sphere',
                    world_space=True,
                    scale=0.3,
                    texture='shore',
                    position=(x, 3, y)
                )

        # LINKS COLORED
        for elem in self.mydata.all_bridge:
            x,y = elem[FP.XY]
            x = x * espace
            y = y * espace
            col = mycolors_dist[elem[FP.ZONE]]
            nod = Entity(
                model='sphere',
                scale=0.4,

                color=color.rgb(col[0], col[1], col[2]),
                position=(x, link_h, y)
            )

            str_dist = str(elem[FP.DIST])
            dist = Entity(position=(x, link_h + 1, y), billboard=True)
            Text(text=str_dist, parent=dist, scale=20, origin=(0,0))

        self.arcs_list = arcs_list
        return arcs_list

    def __init__(self, origin_data: list[str]) -> None:
        """ init and display the graph """
        app = Ursina()
        Sky()

        self.origin_data = origin_data
        # sol
        ground = Entity(
            model='plane',
            scale=400,
            texture='grass',
            texture_scale=(50, 50),
            collider='box'
        )
        

        self.show_state()


        window.exit_button.visible = False

        # joueur FPS
        player = FirstPersonController()
        player.gravity = 0
        InputHandler(player, self.nods, self.nods_dist) 
        app.run()
    
