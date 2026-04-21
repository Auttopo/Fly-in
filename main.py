
from typing import Any
from parser import FlyinParser, ParserError
from dijkstra3d import FlyinAlgorithm
import sys
import traceback
import multiprocessing as mp
from io import StringIO


def create_window(queue: Any, resolved: FlyinAlgorithm, i: list[int]) -> None:

    save_stderr = sys.stderr
    sys.stderr = StringIO()
    i_vale: int = i[0]
    import display 
    try:
        disp = display.FlyinDisplay(resolved.states, i)
        disp.show()
    except Exception as e:
        if i[0] == i_vale:
            i[1] = "stop"
            queue.put(i)
            raise
    finally:
        sys.stderr = save_stderr
        if i[0] == i_vale:
            i[1] = "stop"
           # raise Exception("something get wrong during display")
        queue.put(i)

def main() -> None:
    """ main program exec process """

    try:
        if len(sys.argv) < 2:
            raise ParserError("Use as first argument a configuration file")
        obj: FlyinParser = FlyinParser(sys.argv[1])
        resolved: FlyinAlgorithm = FlyinAlgorithm(obj)
        i: int = [0, ""]

        while i[1] != "stop":
            q = mp.Queue()
            process= mp.Process(target=create_window, args=(q, resolved, i,))
            process.start()
            process.join()
            i = q.get()

    except Exception as e:
        print(f"An error occured :\n{e}", file=sys.stderr)
        if len(sys.argv) > 2 and sys.argv[2] == "traceback":
            traceback.print_exc()

if __name__ == "__main__":
    main()
