
from pydantic import BaseModel, Field
from os.path import exists
from typing import Any, TextIO
from enum import IntEnum

class FlyType(IntEnum):
    connection = 1
    start_hub = 2
    hub = 3
    end_hub = 4
FT = FlyType

LINK = 0
FTYPE = 1
DIST = 2
MAX = 3
ZONE = 4
NAME = 5
XY = 6
COLOR= 7

class ParserError(Exception):
    log: list[str] = []

    @classmethod
    def add_line(cls, line: int, message: str) -> None:
        cls.log.append(f"line: {str(line)}; {message}\n")

    @classmethod
    def get_log_message(cls) -> str:
        return "".join(cls.log)

    @classmethod
    def check_error(cls) -> None:
        if cls.log:
            raise cls(cls.get_log_message())

class FlyinParser():
    """parser class of the project"""

    def __init__(self, file_name: str) -> None:
        self.one_start: bool = False
        self.one_end: bool = False
        self.lnbr: int = 0

        if not exists(file_name):
            raise ParserError(f"the file '{file_name}' do not exist")
        file: TextIO
        with open(file_name, "r") as file:
            file_data: str = file.read()
        file_parsed: list[str] = file_data.split('\n')

        data: dict[FT, Any]
        elem: str
        for elem in file_parsed:
            self.lnbr += 1
            self.line_parser(elem)
        ParserError.check_error()

    all_data: list[list[int]] = []


    def options_check(self, data: list[str], clean_data: list[Any]) -> None:

        basic_colors: list[str] =[
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
            "beige"]
	
        check: bool = True
        for elem in data:
            sub_data = elem.split('=')
            print(sub_data)
            match sub_data[0]:
                case "color":
                    if sub_data[1] not in basic_colors:
                        ParserError.add_line(
                            self.lnbr,
                            f"use known color: {basic_colors}")
                case "zone":
                    match sub_data[1]:
                        case "normal":
                            pass
                        case "priority":
                            pass
                        case "restricted":
                            pass
                        case "blocked":
                            pass
                        case _:
                            ParserError.add_line(self.lnbr,
                        "use known zone: "
                        "normal, priority, restricted, blocked")

                case "max_drones":
                    pass
                case _:
                    ParserError.add_line(self.lnbr, self.ermsg)

    def hub_parser(self, data: list[str]) -> None:
        data = [elem for elem in data if elem]
        if len(data) < 2:
            ParserError.add_line(self.lnbr,
                                 "unsetted data")
            return
        self.ermsg = (
                f"{data[0]}: not correcly set"
                 "; format-> name: x(int) y(int) "
                 "[zone=.. color=.. max_drones=..](optional)" )
        clean_data: list[Any] = [None for _ in range(7)]

        sub_data: list[str] = data[1].split(' ')
        sub_data = [elem for elem in sub_data if elem]

        if len(sub_data) < 3:
            ParserError.add_line(self.lnbr, self.ermsg)
            return
        try:
            clean_data[NAME] = sub_data[0]
            clean_data[XY] = (int(sub_data[1]), int(sub_data[2]))
            if len(sub_data) > 3:
                sub_data[3] = sub_data[3][1:]
                case = len(sub_data) - 1
                sub_data[case] = sub_data[case][:len(sub_data[case]) - 1]
                self.options_check(sub_data[3:], clean_data)
        except Exception as e:
            #raise
            print(e)
            ParserError.add_line(self.lnbr, self.ermsg)
            return

        return clean_data

            


    def connection_parser(self, data: list[str]) -> None:
        pass

    def line_parser(self, line: str) -> None:
        if not line or line[0] == '\n':
            return

        data: list[str] = line.split(':')
        sub_data: list[str]
        match data[0]:
            case "hub":
                sub_data = self.hub_parser(data)
            case "connection":
                sub_data = self.connection_parser(data)
            case "start_hub":
                if self.c_start:
                    ParserError.add_line(self.lnbr, "only one start_hub is possible")
                self.one_start = True
            case "end_hub":
                if self.c_start:
                    self.log += "only one end_hub is possible\n"
                self.one_end = True
            case _:
                ParserError.add_line(self.lnbr,
                        f"Unknow key: '{data[0]}'" \
                        "; possible: hub, start_hub, end_hub, connection"
                                     )

