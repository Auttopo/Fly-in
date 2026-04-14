
from parser import FlyinParser, ParserError
from dijkstra3d import FlyinAlgorithm
from display import FlyinDisplay
import sys
import traceback


def main() -> None:
    """ main program exec process """

    try:
        if len(sys.argv) < 2:
            raise ParserError("Use as first argument a configuration file")
        obj: FlyinParser = FlyinParser(sys.argv[1])
        resolved: FlyinAlgorithm = FlyinAlgorithm(obj)
        FlyinDisplay(resolved.states)
    except Exception as e:
        print(f"An error occured :\n{e}", file=sys.stderr)
        if len(sys.argv) > 2 and sys.argv[2] == "traceback":
            traceback.print_exc()


if __name__ == "__main__":
    main()
