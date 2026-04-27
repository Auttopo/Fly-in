
from typing import Any, TextIO
from parser import FlyinParser, ParserError
from dijkstra3d import FlyinAlgorithm
import sys
import traceback
import multiprocessing as mp
from io import StringIO


def create_window(
            queue: Any, resolved: FlyinAlgorithm,
            i: list[int | str], trace: bool = False) -> None:

    save_stderr: TextIO = sys.stderr
    if not trace:
        sys.stderr = StringIO()
    i_vale: int = int(i[0])
    try:
        import display
        disp: Any = display.FlyinDisplay(resolved.states, i)
        disp.show()
    except Exception as e:
        if trace:
            print(f"An error occured :\n{e}", file=save_stderr)
    finally:
        sys.stderr = save_stderr
        if i[0] == i_vale:
            if trace and i[1] != "stop":
                print("error occured i.. == ..i", file=sys.stderr)
            i[1] = "stop"
        queue.put(i)


def main() -> None:
    """ main program exec process """

    trace: bool = False
    if len(sys.argv) > 2 and sys.argv[2] == "traceback":
        trace = True
    try:
        if len(sys.argv) < 2:
            raise ParserError("Use as first argument a configuration file")
        obj: FlyinParser = FlyinParser(sys.argv[1])
        resolved: FlyinAlgorithm = FlyinAlgorithm(obj)
        i: list[int | str] = [0, ""]

        while i[1] != "stop":
            q: Any = mp.Queue()
            process = mp.Process(
                    target=create_window, args=(q, resolved, i, trace))
            process.start()
            process.join()
            i = q.get()

    except Exception as e:
        print(f"An error occured :\n{e}", file=sys.stderr)
        if traceback:
            traceback.print_exc()


if __name__ == "__main__":
    main()
