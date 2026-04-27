
from typing import Any, TextIO
from parser import FlyinParser, ParserError
from dijkstra3d import FlyinAlgorithm
import sys
import traceback
import multiprocessing as mp
from io import StringIO
from datetime import datetime


TIMEOUT: float = 300


class TimeMaster:
    """ manage time outs """

    def __init__(self, timeout: float) -> None:
        """ basic init """

        self.timeout: float = timeout
        self.start: datetime = datetime.now()

    def check(self) -> bool:
        """ check if the time out is reached """

        elapsed = (datetime.now() - self.start).total_seconds()
        if elapsed > self.timeout:
            print(f"Time out reached : {self.timeout} secondes")
            return False
        return True


class MainProcess:
    """ main class contain main processes """

    @staticmethod
    def create_window(
                queue: Any, resolved: FlyinAlgorithm,
                i: list[int | str], trace: bool,
                t: TimeMaster) -> None:
        """ process independant ursina launch"""

        save_stderr: TextIO = sys.stderr
        if not trace:
            sys.stderr = StringIO()
        i_vale: int = int(i[0])
        try:
            import display
            display.FlyinDisplay(resolved.states, i, t)
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

    @staticmethod
    def main() -> None:
        """ main program process """

        t: TimeMaster = TimeMaster(TIMEOUT)
        trace: bool = False
        if len(sys.argv) > 2 and sys.argv[2] == "traceback":
            trace = True
        try:
            if len(sys.argv) < 2:
                raise ParserError("Use as first argument a configuration file")
            obj: FlyinParser = FlyinParser(sys.argv[1])
            resolved: FlyinAlgorithm = FlyinAlgorithm(obj, t)
            if not resolved.success:
                return
            i: list[int | str] = [0, ""]

            while i[1] != "stop":
                q: Any = mp.Queue()
                process = mp.Process(
                        target=MainProcess.create_window,
                        args=(q, resolved, i, trace, t))
                process.start()
                process.join()
                i = q.get()

        except Exception as e:
            print(f"An error occured :\n{e}", file=sys.stderr)
            if traceback:
                traceback.print_exc()


if __name__ == "__main__":
    MainProcess.main()
