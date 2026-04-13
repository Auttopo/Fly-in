
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

    def create_futur(self) -> None:
        next_nod: FlyinParser = copy.deepcopy(self.base)
        self.states[len(self.states) - 1].linking_futur(next_nod.all_data)
        self.states[len(self.states) - 1][FP.FUTUR].common = 1
        self.states.append(next_nod)
        

    def get_map(self) -> list[Any]:
        """return the 3d graph"""
        return self.base.all_data

    def resolve(self, entry: list[Any]) -> None:

        tree: list[Any] = [entry]

        while tree:
            active = tree.pop(0)
            new_value = active[FP.DIST]

            for nod in active[FP.LINK]:
                cost = nod[FP.COST]

                if nod[FP.DRONES] == nod[FP.MAX].common and \
                        nod[FP.FUTUR].common == 0:
                    self.create_futur()
                    tree.append(nod)

                if nod[FP.DIST] > new_value + cost or nod[FP.DIST] == 0:
                    nod[FP.DIST] = new_value + cost
                    tree.append(nod)
        
