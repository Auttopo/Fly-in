
from parser import FlyinParser
import parser as FP
from typing import Any
import copy

class FlyinAlgorithm:
    """ resolve the graph problem """

    def __init__(self, obj: FlyinParser) -> None:
        """ init and resolve the input """
        self.base: FlyinParser = obj
        self.states: list[FlyinParser] = [copy.deepcopy(obj)]
       # self.next: FlyinParser = copy.deepcopy(self.base)

        start = self.states[0].get_one(FP.START_HUB)
        start[FP.DRONES] = self.states[0].nb_drones
        start[FP.DIST] = 1

        self.resolve(start)
        print("TOTAL TURNS", len(self.states))

    def create_futur(self) -> None:
        next_nod: FlyinParser = copy.deepcopy(self.base)
        self.states[len(self.states) - 1].linking_futur(next_nod.all_data)
        self.states[len(self.states) - 1].futur.common = 1
        self.states.append(next_nod)
        

    def get_map(self) -> list[Any]:
        """return the 3d graph"""
        return self.base.all_data

    def resolve(self, entry: list[Any]) -> None:

        tree: list[Any] = [entry]

        while tree:
            active = tree.pop(0)
            value = active[FP.DIST]

            for nod in active[FP.LINK]:
                cost = nod[FP.COST]

                if nod[FP.DRONES] == nod[FP.MAX].common:
                    if nod[FP.FUTUR].common == 0 and nod[FP.FTYPE] != FP.START_HUB:
                        self.create_futur()
                        tree.append(nod)
                else: 
                    if nod[FP.DIST] > value + cost or nod[FP.DIST] == 0:
                        nod[FP.DIST] = value + cost
                        tree.append(nod)

        i: int = len(self.states) - 1
        shorter: None | list[Any] = self.states[i].end
        while i >= 0:
            end = self.states[i].end
            if end[FP.DIST] < shorter[FP.DIST]:
                shorter = end
            i -= 1

        active = shorter
        path: list[Any] = [active]
        value:float = 0
        while 1:
            if active == None:
                raise Exception("error during path retrieving")
            print(value)

            value = active[FP.DIST]
            shorter = None
            
            for nod in active[FP.LINK]:
                if nod[FP.TWIN]:
                    if nod[FP.TWIN][FP.DIST] < value:
                        shorter = nod
                else:
                    if nod[FP.DIST] < value:
                        shorter = nod
            if value == 1:
                break
            active = shorter
            path.append(shorter)
        for elem in path:
            if elem[FP.COST] == 1:
                elem[FP.DRONES] += 1
            else:
                elem[FP.MAX].common -= 1

            
         
