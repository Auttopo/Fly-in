
from os.path import exists
from typing import Any, TextIO

# FTYPE
HUB: int = 1
START_HUB: int = 2
END_HUB: int = 3

# algo core
LINK: int = 0
DIST: int = 1
MAX: int = 2
DRONES: int = 3
COST: int = 4
PAST: int = 5
FUTUR: int = 6
TWIN: int = 7
# display core
FTYPE: int = 8
ZONE: int = 9
NAME: int = 10
XY: int = 11
COLOR: int = 12
# init core
TOTAL: int = 13


class ParserError(Exception):
    """ log of errors encounter"""
    log: list[str] = []

    @classmethod
    def add_line(cls, line: int, message: str) -> None:
        """ add a line to the log """
        cls.log.append(f"line: {str(line)}; {message}\n")

    @classmethod
    def add_msg(cls, message: str) -> None:
        """ add a message to the log """
        cls.log.append(f"{message}\n")

    @classmethod
    def get_log_message(cls) -> str:
        """ return full log """
        return "".join(cls.log)

    @classmethod
    def check_error(cls) -> None:
        """ check log presence """
        if cls.log:
            raise cls(cls.get_log_message())


class FlyinParser():
    """parser class of the project"""

    class CommonData:
        """ max value object to create a commun value of two lists """

        def __init__(self, value: int | float) -> None:
            """ basic init with the max value """
            self.common: int | float = value

    def __init__(self, file_name: str) -> None:
        """ init object and parse data of the file designed """

        self.all_data: list[list[Any]] = []
        self.all_links: set[frozenset[str]] = set()
        self.all_bridge: list[list[Any]] = []
        self.one_start: bool = False
        self.one_end: bool = False
        self.nb_nbd: bool = False
        self.lnbr: int = 0
        self.nb_drones: int = 0
        self.futur: FlyinParser.CommonData = self.CommonData(0)
        self.start: list[Any]
        self.end: list[Any]
        self.ermsg: str

        if not exists(file_name):
            raise ParserError(f"the file '{file_name}' do not exist")
        file: TextIO
        with open(file_name, "r") as file:
            file_data: str = file.read()
        file_parsed: list[str] = file_data.split('\n')

        elem: str
        for elem in file_parsed:
            self.lnbr += 1
            if self.lnbr == 1 and elem and elem[0] == "#":
                self.lnbr = 0
            self.line_parser(elem)
        if self.nb_drones == 0:
            ParserError.add_msg(
                    "the first line need to be -> "
                    "nb_drones: 'positive integer'")
        if not (self.one_start and self.one_end):
            ParserError.add_msg("one start_hub and one end_hub needed")

        nod: list[Any]
        for nod in self.all_data:
            if len(nod[LINK]) < 1:
                ParserError.add_msg(f"{nod[NAME]} not linked")
        ParserError.check_error()

    def get_one(self, ftype: int) -> list[Any]:
        """ return the first nod of the type needed """
        """ usefull for start / end """

        return next(
                (nod for nod in self.all_data if nod[FTYPE] == ftype))

    def create_nod(self) -> list[Any]:
        """ create a basic nod for the graph """
        nod: list[Any] = [None for _ in range(TOTAL)]
        nod[DRONES] = self.CommonData(0)
        nod[TWIN] = []
        nod[LINK] = []
        nod[DIST] = 0
        nod[COST] = 1
        nod[FUTUR] = self.futur
        return nod

    def options_check(self, data: list[str], clean_data: list[Any]) -> None:
        """ checks options of a classic hub nod """

        basic_colors: list[str] = [
            "red",
            "blue",
            "green",
            "yellow",
            "orange",
            "purple",
            "pink",
            "brown",
            "black",
            "white",
            "grey",
            "violet",
            "cyan",
            "lime",
            "magenta",
            "gold",
            "maroon",
            "darkred",
            "crimson",
            "rainbow",
            "beige"]

        duplicate_ermsg: str = "duplicate parameter not alowed"
        elem: str
        for elem in data:
            sub_data: list[str] = elem.split('=')
            match sub_data[0]:
                case "color":
                    if clean_data[COLOR]:
                        ParserError.add_line(self.lnbr, duplicate_ermsg)
                    if sub_data[1] not in basic_colors:
                        ParserError.add_line(
                            self.lnbr,
                            f"{sub_data[1]} not listed; "
                            "use known color: {basic_colors}")
                    if sub_data[1] == "rainbow":
                        print("Rainbow represent "
                              "all colors of the light spectrum right ? "
                              "The withe color contain "
                              "all colors of the light spectrum !"
                              f"{clean_data[NAME]} color set to white"
                              )
                        sub_data[1] = "white"

                    clean_data[COLOR] = sub_data[1]
                case "zone":
                    if clean_data[ZONE]:
                        ParserError.add_line(self.lnbr, duplicate_ermsg)
                    if sub_data[1] not in {
                             "normal",
                             "priority",
                             "restricted",
                             "blocked"}:
                        ParserError.add_line(
                            self.lnbr,
                            "use known zone: "
                            "normal, priority, restricted, blocked")
                    clean_data[ZONE] = sub_data[1]
                case "max_drones":
                    if clean_data[MAX]:
                        ParserError.add_line(self.lnbr, duplicate_ermsg)
                    try:
                        drone_nbr: int = int(sub_data[1])
                        if drone_nbr < 1:
                            raise
                        clean_data[MAX] = self.CommonData(drone_nbr)
                    except Exception:
                        ParserError.add_line(
                                self.lnbr,
                                "drones number is not an positive integer")
                case _:
                    ParserError.add_line(self.lnbr,
                                         f"unknow option '{sub_data[0]}'"
                                         " ; use : color, zone, "
                                         "or max_drones"
                                         )

    def hub_parser(self, data: list[str]) -> tuple[list[Any], bool]:
        """ parse data of a hub setting """

        max_log: bool = True
        self.ermsg = (
                f"{data[0]}: not correcly set"
                "; format-> 'hub_type': name x(int) y(int) "
                "[zone=.. color=.. max_drones=..](optionals)")

        clean_data: list[Any] = self.create_nod()

        data = [elem for elem in data if elem]
        if len(data) < 2:
            ParserError.add_line(self.lnbr,
                                 "unsetted data")
            return (clean_data, max_log)

        sub_data: list[str] = data[1].split(' ')
        sub_data = [elem for elem in sub_data if elem]

        if len(sub_data) < 3:
            ParserError.add_line(self.lnbr, self.ermsg)
            return (clean_data, max_log)

        if '\\' in sub_data[0] or '/' in sub_data[0]:
            ParserError.add_line(self.lnbr, "name can't contain dash")

        if any(sub_data[0] == elem[NAME] for elem in self.all_data):
            ParserError.add_line(self.lnbr, "this name is already used")

        try:
            clean_data[NAME] = sub_data[0]
            xy: tuple[int, int] = (int(sub_data[1]), int(sub_data[2]))
            if any(xy == elem[XY] for elem in self.all_data):
                ParserError.add_line(self.lnbr, "coordinates already used")
                return (clean_data, max_log)
            clean_data[XY] = xy

            if len(sub_data) > 3:
                if sub_data[3][0] == '[':
                    sub_data[3] = sub_data[3][1:]
                else:
                    raise
                case: int = len(sub_data) - 1
                if sub_data[case][len(sub_data[case]) - 1] == ']':
                    sub_data[case] = sub_data[case][:len(sub_data[case]) - 1]
                else:
                    raise
                self.options_check(sub_data[3:], clean_data)
        except Exception:
            ParserError.add_line(self.lnbr, self.ermsg)
        if not clean_data[ZONE]:
            clean_data[ZONE] = "normal"
        if not clean_data[COLOR]:
            clean_data[COLOR] = "blue"
        if not clean_data[MAX]:
            max_log = False
            clean_data[MAX] = self.CommonData(1)
        return (clean_data, max_log)

    def linking_futur(
            self, futur: list[Any], operator: list[Any]) -> list[Any]:
        """ linking all nodes to futur state """

        nod_2: list[Any]
        new_operator: list[Any]

        elem: list[Any]
        for elem in self.all_data:
            nod_2 = next(
                    (nod for nod in futur if nod[NAME] == elem[NAME]))
            elem[LINK].append(nod_2)
            nod_2[PAST] = elem
            if elem[NAME] == operator[NAME]:
                new_operator = nod_2
        return new_operator

    def create_bridge(
            self, dest: list[Any], src: list[Any],
            shared_max: Any, name: str) -> list[Any]:
        """ link a nod to another  """

        cost: float = 0
        if dest[ZONE] == "restricted":
            cost = 1
        elif dest[ZONE] == "priority":
            cost = -0.5

        bridge: list[Any] = self.create_nod()
        if not dest[ZONE] == "blocked":
            bridge[LINK].append(dest)
        bridge[MAX] = shared_max
        bridge[COST] = cost
        bridge[NAME] = name
        src[LINK].append(bridge)

        self.all_bridge.append(bridge)
        bridge[ZONE] = dest[ZONE]
        return bridge

    def linking(self, name1: str, name2: str, max_drones: float) -> None:
        """ linking properly two nodes """

        nod_1: list[Any] = next(
                (elem for elem in self.all_data if elem[NAME] == name1))
        nod_2: list[Any] = next(
                (elem for elem in self.all_data if elem[NAME] == name2))

        x1: int
        x2: int
        y1: int
        y2: int
        x1, y1 = nod_1[XY]
        x2, y2 = nod_2[XY]
        midx: float = (x1 + x2) / 2
        midy: float = (y1 + y2) / 2
        sep: float = 0.015

        shared_max: FlyinParser.CommonData = self.CommonData(max_drones)

        bridge: list[Any] = self.create_bridge(
                        nod_1, nod_2, shared_max,
                        name2 + '-' + name1)
        bridge[XY] = (midx + sep, midy + sep)

        bridge2: list[Any] = self.create_bridge(
                        nod_2, nod_1, shared_max,
                        name1 + '-' + name2)

        bridge2[XY] = (midx - sep, midy - sep)
        bridge[TWIN] = bridge2
        bridge2[TWIN] = bridge
        bridge[DRONES] = bridge2[DRONES]

    def connection_parser(self, data: list[str]) -> None:
        """ parse data of a connection setting """

        max_drones: int = 1
        self.ermsg = (
                f"{data[0]}: not correcly set"
                "; format-> connection: 'name_hub_1'-'name_hub_2' "
                "[max_link_capacity=..](optional)"
                        )
        data = [elem for elem in data if elem]
        if len(data) < 2:
            ParserError.add_line(self.lnbr,
                                 "unsetted data")
            return
        sub_data: list[str] = data[1].split(' ')
        sub_data = [elem for elem in sub_data if elem]
        try:
            names: list[str] = sub_data[0].split('-')
            if not any(names[0] == elem[NAME] for elem in self.all_data):
                ParserError.add_line(
                        self.lnbr, f"{names[0]} not found in data base")
                return
            if not any(names[1] == elem[NAME] for elem in self.all_data):
                ParserError.add_line(
                        self.lnbr, f"{names[1]} not found in data base")
                return
            link: frozenset[str] = frozenset((names[0], names[1]))
            if link in self.all_links:
                ParserError.add_line(self.lnbr, "this link already exist")
                return
            self.all_links.update({link})

            if len(sub_data) > 1:
                if len(sub_data) > 2:
                    raise
                option: list[str] = sub_data[1].split('=')
                if option[0] != "[max_link_capacity":
                    raise
                option[1] = option[1][:len(option) - 1]
                if option[1].isdigit() and int(option[1]) < 1:
                    ParserError.add_line(
                            self.lnbr,
                            "max_link_capacity is not an positive integer")
                    return
                max_drones = int(option[1])
            self.linking(names[0], names[1], max_drones)
        except Exception:
            ParserError.add_line(self.lnbr, self.ermsg)

        return

    def nb_drones_parser(self, data: str) -> int:
        """ parse data of the number of drone line """

        clean_data: str = "".join([elem for elem in data if elem != ' '])
        try:
            nbr = int(clean_data)
            if nbr < 0:
                raise
        except Exception:
            ParserError.add_line(1, "nb_drones must be positive integer")
            return 0
        return nbr

    def line_parser(self, line: str) -> None:
        """ parse data depending of the type of line """

        if not line or line[0] == '#':
            return
        max_log: bool

        data: list[str] = line.split(':')
        match data[0]:
            case "nb_drones":
                if self.nb_nbd:
                    ParserError.add_line(
                            self.lnbr, "only one nb_drones line is possible")
                self.nb_nbd = True
                if self.lnbr == 1:
                    self.nb_drones = self.nb_drones_parser(data[1])
            case "hub":
                clean_data, max_log = self.hub_parser(data)
                clean_data[FTYPE] = HUB
                self.all_data.append(clean_data)
            case "connection":
                self.connection_parser(data)
            case "start_hub":
                if self.one_start:
                    ParserError.add_line(
                            self.lnbr, "only one start_hub is possible")
                self.one_start = True
                clean_data, max_log = self.hub_parser(data)
                if not max_log:
                    clean_data[MAX].common = self.nb_drones
                if clean_data[MAX] and \
                        clean_data[MAX].common < self.nb_drones:
                    ParserError.add_line(
                            self.lnbr,
                            "max_drones on start_hub "
                            "impossible for drones number")
                clean_data[FTYPE] = START_HUB
                self.all_data.append(clean_data)
                self.start = clean_data
            case "end_hub":
                if self.one_end:
                    ParserError.add_line(
                            self.lnbr, "only one end_hub is possible")
                self.one_end = True

                clean_data, max_log = self.hub_parser(data)
                if not max_log:
                    clean_data[MAX].common = self.nb_drones
                if clean_data[MAX] and \
                        clean_data[MAX].common < self.nb_drones:
                    ParserError.add_line(
                            self.lnbr,
                            "max_drones on end_hub "
                            "impossible for drones number")
                clean_data[FTYPE] = END_HUB
                self.all_data.append(clean_data)
                self.end = clean_data
            case _:
                ParserError.add_line(
                        self.lnbr,
                        f"unknow key: '{data[0]}' "
                        "possible: hub, start_hub, end_hub, connection"
                        ", nb_drones"
                                     )
