
from typing import Any, Callable
import parser as FP
import numpy as np
import functools

import ursina
from ursina import Ursina, Entity, Sky, Text
from ursina import window, color, Vec3, Mesh, held_keys, time, destroy
from ursina.prefabs.first_person_controller import FirstPersonController


class StopUpdate(Exception):
    """ basic class to stop ursina """
    pass


def arc_entity(x1: int, z1: int, y1: int, x2: int, z2: int, y2: int) -> Any:
    """ create an ursina arc beetwin two points """

    points: list[Any] = []
    dx: int
    dy: int
    dx, dy = x2 - x1, y2 - y1
    d: float = np.sqrt(dx**2 + dy**2)

    h: float = d / 2 / 2
    i: float = 0
    while i <= 1.01:
        px = x1 + (x2 - x1) * i
        py = y1 + (y2 - y1) * i
        pz = z2 + (z1 - z2) * i
        pz = pz + h * (1 - ((i * 2 - 1) ** 2))
        points.append(Vec3(px, pz, py))
        i += 0.01

    return Entity(model=Mesh(vertices=points, mode='line', thickness=2))


def get_colors() -> dict[str, tuple[float, float, float]]:
    """ return all colors handle """

    data: dict[str, tuple[float, float, float]] = {
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
        "beige": (210, 180, 140), }

    elem: str
    for elem in data.keys():
        data[elem] = (
                data[elem][0] / 255, data[elem][1] / 255, data[elem][2] / 255)
    return data


def get_type_color() -> dict[str, tuple[float, float, float]]:
    """ return all color dependingly of the zone type """

    return {
            "priority": (220 / 255, 220 / 255, 220 / 255),  # white
            "restricted": (0, 0, 0),  # black
            "normal": (110 / 255, 110 / 255, 110 / 255),  # grey
            "blocked": (220 / 255, 15 / 255, 15 / 255),  # red
            }


class InputHandler(ursina.Entity):  # type: ignore[misc, unused-ignore]
    """ class to define keys beheviors """

    def __init__(self, display: Any) -> None:
        """ basic init of the class """

        super().__init__()
        self.stop: bool = False
        self.d: Any = display
        self.vis: int = 0

    def destroy_all(self) -> None:
        """ destroy all created ursina entities """

        for nod in self.d.all_dist:
            destroy(nod)
        for nod in self.d.all_max:
            destroy(nod)
        for nod in self.d.nods:
            destroy(nod)
        for nod in self.d.nods_dist:
            destroy(nod)
        for nod in self.d.arcs_list:
            destroy(nod)
        for nod in self.d.rest:
            destroy(nod)

    def input(self, key: Any) -> None:
        """ add keys behaviors """

        if key == 'escape':
            self.d.i[1] = "stop"
            self.stop = True

        if key == 'o':
            for nod in self.d.nods_dist:
                nod.visible = not nod.visible
            for nod in self.d.nods:
                nod.visible = not nod.visible

        if key == 'i':

            self.vis += 1
            if self.vis == 1:
                for nod in self.d.all_dist:
                    nod.visible = True
                for nod in self.d.all_max:
                    nod.visible = False
            elif self.vis == 2:
                for nod in self.d.all_dist:
                    nod.visible = False
                for nod in self.d.all_max:
                    nod.visible = True
            elif self.vis == 3:
                for nod in self.d.all_dist:
                    nod.visible = False
                for nod in self.d.all_max:
                    nod.visible = False

            if self.vis == 3:
                self.vis = 0

        if key == 'n':
            if self.d.i[0] <= len(self.d.states) - 2:
                self.d.i[0] += 1
                self.stop = True

        if key == 'b':
            if self.d.i[0] > 0:
                self.d.i[0] -= 1
                self.stop = True

        if key == 'm':
            if self.d.i[0] != len(self.d.states) - 1:
                self.d.i[0] += 10
                if self.d.i[0] >= len(self.d.states):
                    self.d.i[0] = len(self.d.states) - 1
                self.stop = True

        if key == 'v':
            if self.d.i[0] != 0:
                self.d.i[0] -= 10
                if self.d.i[0] < 0:
                    self.d.i[0] = 0
                self.stop = True

    def update(self) -> None:
        """ change ursina update behaviors """

        if self.stop:
            self.destroy_all()
            self.d.app.destroy()
            raise StopUpdate("stop update")

        self.d.player.speed = 40
        if held_keys['space']:
            self.d.player.y += 40 * time.dt
        if held_keys['shift']:
            self.d.player.y -= 40 * time.dt


class FlyinDisplay:
    """ main class of the file """

    def set_state(self) -> None:
        """ create all 3d objects of the graph """

        mycolors: dict[str, tuple[float, float, float]] = get_colors()
        mycolors_dist: dict[str, tuple[float, float, float]] = get_type_color()
        self.nods: list[Any] = []
        self.nods_dist: list[Any] = []
        self.mydata: Any = self.states[self.i[0]]
        link_h: int = 4
        espace: int = 8
        arcs_list: list[Any] = []
        self.all_dist: list[Any] = []
        self.all_max: list[Any] = []
        str_dist: str
        str_max: str
        dist: Entity
        maxi: Entity
        d: Text
        m: Text
        txt: Entity
        d_n: Text

        ui: Text = Text(
            text=str(self.i[0]),
            texture_scale=(50, 50),
            scale=1,
            origin=(-9, 0))
        self.rest.append(ui)

        elem: list[Any]
        for elem in self.mydata.all_data:
            # COLORED BASIC HUBS
            x: int
            y: int

            x, y = elem[FP.XY]
            x = x * espace
            y = y * espace
            col: tuple[float, float, float] = mycolors[elem[FP.COLOR]]
            nod: Entity = Entity(
                model='sphere',
                color=color.rgb(col[0], col[1], col[2]),
                position=(x, 1, y)
            )
            self.nods.append(nod)

            str_dist = str(elem[FP.DIST])
            dist = Entity(position=(x, 2.5, y), billboard=True)
            d = Text(text=str_dist, parent=dist, scale=20, origin=(0, 0))
            dist.visible = False
            d.visible = False
            self.all_dist.append(dist)
            self.all_dist.append(d)

            str_max = str(elem[FP.MAX].common)
            maxi = Entity(position=(x, 2.5, y), billboard=True)
            m = Text(text=str_max, parent=maxi, scale=20, origin=(0, 0))
            maxi.visible = False
            m.visible = False
            self.all_max.append(maxi)
            self.all_max.append(m)

            # ZONE TYPE COLOR HUBS
            col = mycolors_dist[elem[FP.ZONE]]
            nod = Entity(
                model='sphere',

                color=color.rgb(col[0], col[1], col[2]),
                position=(x, 1, y)
            )
            nod.visible = not nod.visible
            self.nods_dist.append(nod)

            # LINES CONNECTION
            link: list[Any]
            for link in elem[FP.LINK]:
                x2: int
                y2: int
                x2, y2 = link[FP.XY]
                if link[FP.NAME] != elem[FP.NAME]:
                    arcs_list.append(
                            arc_entity(
                                x, link_h, y, x2 * espace, 1, y2 * espace))

            # DRONES BALLS
            drones: int = elem[FP.DRONES].common
            if drones:
                drones_balls: Entity = Entity(
                    model='sphere',
                    world_space=True,
                    scale=0.3,
                    texture='shore',
                    position=(x, 3, y)
                )
                self.rest.append(drones_balls)

                txt = Entity(position=(x, 3.2, y), billboard=True)
                d_n = Text(
                        text=str(drones), parent=txt, scale=20, origin=(0, 0))
                self.rest.append(txt)
                self.rest.append(d_n)

        # LINKS
        for elem in self.mydata.all_bridge:
            drones = elem[FP.DRONES].common

            x, y = elem[FP.XY]
            x = x * espace
            y = y * espace
            col = mycolors_dist[elem[FP.ZONE]]

            nod = Entity(
                model='sphere',
                scale=0.4,

                color=color.rgb(col[0], col[1], col[2]),
                position=(x, link_h, y)
            )
            self.rest.append(nod)

            if drones:
                drones_balls = Entity(
                    model='sphere',
                    world_space=True,
                    scale=0.3,
                    texture='shore',
                    position=(x, link_h + 1.5, y)
                )
                self.rest.append(drones_balls)
                txt = Entity(position=(x, link_h + 1.7, y), billboard=True)
                d_n = Text(
                        text=str(drones), parent=txt, scale=20, origin=(0, 0))
                self.rest.append(txt)
                self.rest.append(d_n)

            str_dist = str(elem[FP.DIST])
            dist = Entity(position=(x, link_h + 1, y), billboard=True)
            d = Text(text=str_dist, parent=dist, scale=20, origin=(0, 0))
            dist.visible = False
            d.visible = False
            self.all_dist.append(dist)
            self.all_dist.append(d)

            str_max = str(elem[FP.MAX].common)
            maxi = Entity(position=(x, link_h + 1, y), billboard=True)
            m = Text(text=str_max, parent=maxi, scale=20, origin=(0, 0))
            maxi.visible = False
            m.visible = False
            self.all_max.append(maxi)
            self.all_max.append(m)

        self.arcs_list = arcs_list

    def __init__(self, states: list[Any], i: list[int | str]) -> None:
        """ init and display the graph """
        self.states: list[Any] = states
        self.rest: list[Any] = []
        self.i: list[int]
        self.app: Ursina
        self.player: FirstPersonController

        def show(self: Any) -> None:
            """ main funtion, process all the diplay """
            self.i = i

            self.app = Ursina()
            sky: Sky = Sky()
            self.rest.append(sky)

            ground: Entity = Entity(
                model='plane',
                scale=400,
                texture='grass',
                texture_scale=(50, 50),
                collider='box'
            )
            self.rest.append(ground)

            window.exit_button.visible = False

            self.set_state()
            self.player = FirstPersonController()
            self.rest.append(self.player)
            self.player.gravity = 0
            InputHandler(self)
            self.app.run()

        self.show: Callable[..., None] = functools.partial(show, self)
