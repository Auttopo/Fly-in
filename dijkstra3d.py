
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
        start[FP.DRONES].common = self.states[0].nb_drones
        self.resolve(start)
        print("TOTAL STATES", len(self.states))
        print("DONES ARRIVED", len(self.all_path))

    def create_futur(self, operator: list[Any]) -> list[Any]:
        new_operator: list[Any]

        next_nod: FlyinParser = copy.deepcopy(self.base)
        new_operator = self.states[len(self.states) - 1].linking_futur(next_nod.all_data, operator)
        self.states[len(self.states) - 1].futur.common = len(self.states)
        self.states.append(next_nod)

        return new_operator
        
    def max_check(self, nod: list[Any]) -> bool:
        if nod[FP.DRONES].common == nod[FP.MAX].common or nod[FP.MAX].common == 0:
            return False
        return True

    def prepare_futur(self, nod: list[Any], tree: list[Any]) -> None:

        if nod[FP.FUTUR].common == 0:
            unblocked = self.create_futur(nod)
            unblocked[FP.DIST] = nod[FP.DIST] + unblocked[FP.COST]
            tree.append(unblocked)
        else:
            futur_nod = next(new for new in nod[FP.LINK] if new[FP.FUTUR].common != nod[FP.FUTUR].common)
            if self.max_check(futur_nod):
                if futur_nod[FP.DIST] > nod[FP.DIST] + futur_nod[FP.COST] or futur_nod[FP.DIST] == 0:
                    futur_nod[FP.DIST] = nod[FP.DIST] + futur_nod[FP.COST]
                    tree.append(futur_nod)

    def resolve(self, entry: list[Any]) -> None:

        tree: list[Any] = [entry]
        self.all_path: list[list[Any]] = []
        drones = entry[FP.DRONES].common
        
        blocked: list[Any]

        while drones:

            tree = [entry]
            entry[FP.DIST] = 1
            while tree:
                active = tree.pop(0)
                if active[FP.DIST] == 0:
                    raise Exception("traitor among us")
                value = active[FP.DIST]
                for nod in list(active[FP.LINK]):
                    cost = nod[FP.COST]
                    if self.max_check(nod):
                        if nod[FP.DIST] > value + cost or nod[FP.DIST] == 0:
                            nod[FP.DIST] = value + cost
                            tree.append(nod)
                    else: 
                        if active[FP.TWIN]:
                            self.prepare_futur(active[FP.TWIN][FP.LINK][0], tree)
                        else:
                            self.prepare_futur(active, tree)

            i: int = len(self.states) - 1
            shorter: list[Any] = self.states[i].end
            while i >= 0:
                end = self.states[i].end
                if end[FP.DIST] != 0 and end[FP.DIST] < shorter[FP.DIST]:
                    shorter = end
                i -= 1

            active = shorter
            path: list[Any] = [active]

            while 1:
                if active[FP.TWIN]:
                    shorter = active[FP.TWIN][FP.LINK][0]
                else:
                    shorter = active[FP.LINK][0]

                for nod in active[FP.LINK]:
                    if self.max_check(nod):
                        if nod[FP.TWIN]:
                            nod = nod[FP.TWIN]
                        if nod[FP.DIST] != 0 and \
                            nod[FP.FUTUR].common == active[FP.FUTUR].common:
                            if nod[FP.DIST] < shorter[FP.DIST]:
                                shorter = nod

                if active[FP.PAST] and \
                    self.max_check(active[FP.PAST]) and \
                    active[FP.PAST][FP.DIST] != 0 and \
                        active[FP.PAST][FP.DIST] < shorter[FP.DIST]:
                    shorter = active[FP.PAST]
                if shorter[FP.FTYPE] == FP.START_HUB:
                    break

                active = shorter
                path.append(shorter)
            while shorter[FP.PAST]:
                path.append(shorter)
                shorter = shorter[FP.PAST]

            turns: int = 0
            futur: int = path[0][FP.FUTUR]
            for elem in path:
                if elem[FP.FUTUR] == futur and elem[FP.FTYPE] != FP.END_HUB:
                    elem[FP.MAX].common -= 1
                    futur = elem[FP.FUTUR]
                if elem[FP.MAX].common == -1:
                    raise Exception(f"impossible path occured {drones}")

                if elem[FP.COST] == 1:
                    elem[FP.DRONES].common += 1
                    turns += 1

            print(turns, "path finded")

            self.all_path.append(path[::-1])
            drones -= 1
            if drones == 0:
                return
            for timeline in self.states:
                for elem in timeline.all_data:
                    elem[FP.DIST] = 0
                for elem in timeline.all_bridge:
                    elem[FP.DIST] = 0
        
         
