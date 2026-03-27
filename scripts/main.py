import argparse
from pathlib import Path
import sys
from typing import Any, Callable, cast

from utils import io
from utils.customLogger import LOGGER
from transformations import encryption, obfuscation

# =======  Definitions  ===================================================== #

class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

class AlignedMetavarFormatter(argparse.HelpFormatter):
    META_COL = 17  # column where metavar starts inside the option label

    def _format_action_invocation(self, action):
        if not action.option_strings:
            return super()._format_action_invocation(action)

        # positional args
        if action.nargs == 0:
            return ", ".join(action.option_strings)

        # optional args with value
        opts = ", ".join(action.option_strings)
        metavar = self._format_args(action, action.dest.upper())

        pad = max(1, self.META_COL - len(opts))
        return f"{opts}{' ' * pad}{metavar}"

TRANSFORMS = {
    "obfuscation": {
        "entrypoint": obfuscation.entrypoint,
        "help": "Obfuscates payload strings into structured data formats",
        "ops": {
            "ip": {
                "help": "Converts bytes to IP address strings",
                "modes": {
                    "ipv4": "Standard 32-bit IPv4 format (x.x.x.x)",
                    "ipv6": "Standard 128-bit IPv6 format (x:x:x:x:x:x:x:x)"
                }
            },
            "mac": {
                "help": "Converts bytes to MAC addresses",
                "modes": {
                    "unix": "Colon-separated hex (xx:xx:xx:xx:xx:xx)",
                    "win": "Dash-separated hex (xx-xx-xx-xx-xx-xx)",
                    "net": "Cusco format (xxxx.xxxx.xxxx)",
                    "raw": "Raw contiguous hex string (xxxxxxxxxxxx)"
                }
            },
            "uuid": {
                "help": "Converts bytes to Universally Unique IDentifiable strings",
                "modes": {
                    "std": "Standard RFC 4122 UUID format",
                    "win": "Windows registry string format"
                }
            },
            "email": {
                "help": "Converts bytes to fake email addresses",
                "modes": {
                    "temp": "Standard temporary email format",
                    "temp2": "Alternative temporary email format"
                }
            }
        }
    },
    "encryption" : {
        "entrypoint": encryption.entrypoint,
        "help": "Encrypts the payload using various cryptographic standards",
        "ops": {
            "aes": {
                "help": "Advanced Encryption Standard (AES-256)",
                "modes": {}
            },
            "rc4": {
                "help": "Rivest Cipher 4 stream cipher",
                "modes": {}
            },
            "xor": {
                "help": "Exclusive-OR byte manipulation",
                "modes": {}
            }
        }
    }
}

OUT_FORMATS = [
    "c",
    "python"
]

LIST_CHOICES = [
    "transforms",
    "ops",
    "modes",
    "formats",
    "all"
]

# =======  Helpers  ========================================================= #

def build_mode_choices(parser: MyParser) -> list[str]:
    transform_str = sys.argv[(sys.argv.index("-t") if "-t" in sys.argv else sys.argv.index("--transform")) + 1]
    op_str = sys.argv[(sys.argv.index("--op")) + 1]

    try:
        modes = TRANSFORMS[transform_str]["ops"][op_str]["modes"]
    except KeyError:
        print(f"Invalid op '{op_str}' for '{transform_str}' transform (use --list ops to list)")
        parser.print_help()
        sys.exit()

    return modes

def build_op_choices(parser: MyParser) -> list[str]:
    transform_str = sys.argv[(sys.argv.index("transform")) + 1]

    try:
        ops = TRANSFORMS[transform_str.lower()]["ops"]
    except KeyError:
        print(f"Invalid transform: '{transform_str}' (use --list transforms to list)")
        parser.print_help()
        sys.exit()

    return ops

def build_list_choices(choice: str) -> None:
    if choice not in LIST_CHOICES:
        raise ValueError(f"Invalid list target '{choice}. Value values: {', '.join(LIST_CHOICES)}")

    sep = "    "
    choices_map = {
        "transforms": {
            "lvl": 1,
            "metavar": "type",
            "section_header": "Payload Transforms [--transform <type>]",
            "column_header":     f"{sep}{'Name':<17}{'Description'}",
            "column_header_sep": f"{sep}{'----':<17}{'-----------'}",
            "data_rows_padding": [17]
        },
        "ops": {
            "lvl": 2,
            "metavar": "value",
            "section_header": "Payload Operations [--op <value>]",
            "column_header":     f"{sep}{'Transform':<17}{'Name':<13}{'Description'}",
            "column_header_sep": f"{sep}{'---------':<17}{'----':<13}{'-----------'}",
            "data_rows_padding": [17, 13]
        },
        "modes": {
            "lvl": 3,
            "metavar": "value",
            "section_header": "Operation Modes [--mode <value>]",
            "column_header":     f"{sep}{'Operation':<17}{'Name':<13}{'Description'}",
            "column_header_sep": f"{sep}{'---------':<17}{'----':<13}{'-----------'}",
            "data_rows_padding": [17, 13]
        },
        "formats": {
            "metavar": "value",
            "section_header": "Output Formats [--format <value>]",
            "column_header":     f"{sep}{'Name'}",
            "column_header_sep": f"{sep}{'----'}",
        }
    }

    first_choice = True
    choices = LIST_CHOICES[:-1] if choice == "all" else [choice]
    for choice in choices:
        if not first_choice:
            print()
            print()
        first_choice = False

        print(choices_map[choice]["section_header"])
        print("=" * len(choices_map[choice]["section_header"]))
        print()
        
        if choice != "modes":
            print(choices_map[choice]["column_header"])
            print(choices_map[choice]["column_header_sep"])

        if choice == "formats":
            for format in OUT_FORMATS:
                print(sep + format)

            continue

        lvl = cast(int, choices_map[choice]["lvl"])
        for transform in TRANSFORMS:
            if lvl == 1:
                pad = cast(int, choices_map[choice]["data_rows_padding"][0])
                print(f"{sep}{transform:<{pad}}{TRANSFORMS[transform]['help']}")
            elif lvl == 2:
                pad1 = cast(int, choices_map[choice]["data_rows_padding"][0])
                pad2 = cast(int, choices_map[choice]["data_rows_padding"][1])
                for op in TRANSFORMS[transform]["ops"]:
                    help = TRANSFORMS[transform]["ops"][op]["help"]
                    print(f"{sep}{transform:<{pad1}}{op:<{pad2}}{help}")
            elif lvl == 3:
                if transform != list(TRANSFORMS.values())[0]:
                    print() # Newline-separate all modes

                print(f"{sep}=== {transform.upper()} ===")
                print(choices_map[choice]["column_header"])
                print(choices_map[choice]["column_header_sep"])

                pad1 = cast(int, choices_map[choice]["data_rows_padding"][0])
                pad2 = cast(int, choices_map[choice]["data_rows_padding"][1])
                for op in TRANSFORMS[transform]["ops"]:
                    for mode in TRANSFORMS[transform]["ops"][op]["modes"]:
                        help = TRANSFORMS[transform]["ops"][op]["modes"][mode]
                        print(f"{sep}{op:<{pad1}}{mode:<{pad2}}{help}")


# =======  Arg Parsing  ===================================================== #

def parse_args() -> argparse.Namespace: 
    parser = MyParser(
        prog="obfuscatePayload",
        description="Transforms payloads depending on the type used. Different modes can be chosen for each transformation.",
        formatter_class=lambda prog: AlignedMetavarFormatter(
            prog, max_help_position=33, width=100
        ),
    )

    parser.add_argument(
        "-l", "--list",
        metavar="<type>",
        choices=LIST_CHOICES,
        help=f"List all modules for [type]. Types are: {', '.join(LIST_CHOICES)}"
    )
    list_provided = any(arg in sys.argv for arg in ["-l", "--list"])

    # --- Transformations --- #
    parser.add_argument(
        "-t", "--transform",
        metavar="<type>",
        required=not list_provided,
        choices=TRANSFORMS.keys(),
        help=f"The transform to apply to the payload (use --list transforms to list)"
    )
    parser.add_argument(
        "--op",
        metavar="<op>",
        required=not list_provided,
        choices=build_op_choices(parser) if any(arg in sys.argv for arg in ["transform"]) else [],
        help="Operation to run (use --list ops to list)"
    )
    parser.add_argument(
        "-m", "--mode",
        metavar="<mode>",
        required=not list_provided,
        choices=build_mode_choices(parser) if any(arg in sys.argv for arg in ["--op"]) else [],
        help="Mode variant for the selected operation. Depends on --transform and --op (use --list modes to list)"
    )


    # --- I/O --- #
    parser.add_argument(
        "-i", "--input",
        type=Path,
        required=sys.stdin.isatty() and not list_provided,
        metavar="<input>",
        help="Path to the bin file containing the payload to be transformed"
    )
    parser.add_argument(
        "-o", "--out",
        type=Path,
        required=not list_provided,
        metavar="<out>",
        help="Save the transformed payload to a file. If not specified, the payload will be printed to the console"
    )
    parser.add_argument(
        "-f", "--format",
        type=str,
        default="c",
        metavar="<format>",
        choices=OUT_FORMATS,
        help=f"Output format (use --list formats to list)"
    )

    return parser.parse_args()

# =======  Entrypoint  ====================================================== #

def main() -> int:
    args = parse_args()
    if args.list:
        build_list_choices(args.list)
        return 0

    try:
        data = io.read_data(args.input)
    except Exception as e:
        LOGGER.error("Error while reading the input file: %s", e)
        return -1
    
    entrypoint = cast(Callable[[bytes, str, str], str], TRANSFORMS[args.mode]["entrypoint"])
    result = entrypoint(data, args.transform, args.format)
    if not result:
        LOGGER.error("Result is empty after aplying %r (%r), something went wrong...", args.mode, args.transform)
        return -1

    io.write_data(result.encode(), args.out)
    return 0

if __name__ == "__main__":
    main()