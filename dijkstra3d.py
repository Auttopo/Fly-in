
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
        self.resolve(start)
        print("TOTAL TURNS", len(self.states))
        print("DONES ARRIVED", len(self.all_path))

    def create_futur(self, operator: list[Any]) -> list[Any]:
        new_operator: list[Any]

        next_nod: FlyinParser = copy.deepcopy(self.base)
        new_operator = self.states[len(self.states) - 1].linking_futur(next_nod.all_data, operator)
        self.states[len(self.states) - 1].futur.common = len(self.states)
        self.states.append(next_nod)

        return new_operator
        

    def get_map(self) -> list[Any]:
        """return the 3d graph"""
        return self.base.all_data

    def max_check(self, nod: list[Any]) -> bool:
        if nod[FP.DRONES] == nod[FP.MAX].common or nod[FP.MAX].common == 0:
            return False
        return True

    def resolve(self, entry: list[Any]) -> None:

        tree: list[Any] = [entry]
        self.all_path: list[list[Any]] = []
        drones = entry[FP.DRONES]
        
        blocked: list[Any]

        while drones:

            tree = [entry]
            entry[FP.DIST] = 1
            while tree:
                active = tree.pop(0)
                value = active[FP.DIST]
                for nod in list(active[FP.LINK]):
                    cost = nod[FP.COST]
                    if not self.max_check(nod) and not nod[FP.TWIN]:
                        if nod[FP.FUTUR].common == 0:
                            nod = active[FP.TWIN][FP.LINK][0]
                            unblocked = self.create_futur(nod)
                            unblocked[FP.DIST] = nod[FP.DIST] + unblocked[FP.COST]
                            tree.append(unblocked)
                        else:
                            nod = active[FP.TWIN][FP.LINK][0]
                            futur_nod = next(new for new in nod[FP.LINK] if new[FP.FUTUR].common != nod[FP.FUTUR].common)
                            if futur_nod[FP.DIST] > nod[FP.DIST] + unblocked[FP.COST] or futur_nod[FP.DIST] == 0:
                                futur_nod[FP.DIST] = nod[FP.DIST] + unblocked[FP.COST]
                                tree.append(futur_nod)
                    else: 
                        if nod[FP.DIST] > value + cost or nod[FP.DIST] == 0:
                            nod[FP.DIST] = value + cost
                            tree.append(nod)

            i: int = len(self.states) - 1
            shorter: None | list[Any] = self.states[i].end
            while i >= 0:
                end = self.states[i].end
                if end[FP.DIST] != 0 and end[FP.DIST] < shorter[FP.DIST]:
                    shorter = end
                i -= 1

            active = shorter
            path: list[Any] = [active]

            while 1:
                if active == None:
                    raise Exception(f"error during path retrieving {drones}")
                shorter = active[FP.LINK][0]
                pass_check: bool = False
                for nod in active[FP.LINK]:
                    if self.max_check(nod) and nod[FP.DIST] != 0:
                        if nod[FP.FUTUR].common == active[FP.FUTUR].common:
                            if nod[FP.TWIN]:
                                if nod[FP.TWIN][FP.DIST] < shorter[FP.DIST]:
                                    shorter = nod
                            else:
                                if nod[FP.DIST] < shorter[FP.DIST]:
                                    shorter = nod
                    if active[FP.PAST] and \
                        self.max_check(active[FP.PAST]) and \
                        active[FP.PAST][FP.DIST] != 0 and \
                            active[FP.PAST][FP.DIST] < shorter[FP.DIST]:
                        shorter = active[FP.PAST]
                        pass_check = True
                if not pass_check:
                    shorter[FP.MAX].common -= 1
                    if shorter[FP.MAX].common == -1:
                        raise Exception(f"impossible path occured {drones}")
                if shorter[FP.DIST] == 1:
                    break
                active = shorter
                path.append(shorter)

            for elem in path:
                if elem[FP.COST] == 1:
                    elem[FP.DRONES] += 1
            print(len(path), "path finded")
            print(len(self.all_path), "path tot")

            self.all_path.append(path[::-1])
            drones -= 1
            if drones == 0:
                return
            for timeline in self.states:
                for elem in timeline.all_data:
                    elem[FP.DIST] = 0
                for elem in timeline.all_bridge:
                    elem[FP.DIST] = 0
                    
            
         
