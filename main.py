
from parser import FlyinParser, ParserError
import sys
import traceback

def main() -> None:
    """ main program exec process """

    try:
        if len(sys.argv) < 2:
            raise ParserError("Use as first argument a configuration file")

        obj = FlyinParser("config.txt")
    except Exception as e:
        print(f"An error occured :\n{e}", file=sys.stderr)
        if len(sys.argv) > 2 and sys.argv[2] == "traceback":
            traceback.print_exc()


if __name__ == "__main__":
    main()
