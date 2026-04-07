"""Encrypts or obfuscates payloads to bypass signature-based detection."""

import argparse
from pathlib import Path
import sys
import textwrap
from typing import Callable, cast

from utils import io
from utils.customLogger import LOGGER
from transformations import encryption, obfuscation

# =======  Definitions  ===================================================== #

class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message.rstrip())
        self.print_help()
        sys.exit(2)

class AlignedMetavarFormatter(argparse.HelpFormatter):
    META_COL = 17  # Where metavar starts inside the option label

    def _format_action_invocation(self, action):
        if not action.option_strings:
            return super()._format_action_invocation(action)

        # Positional args
        if action.nargs == 0:
            return ", ".join(action.option_strings)

        # Optional args with value
        opts = ", ".join(action.option_strings)
        metavar = self._format_args(action, action.dest.upper())

        pad = max(1, self.META_COL - len(opts))
        return f"{opts}{' ' * pad}{metavar}"

MAX_PRINT_WIDTH = 100

TRANSFORMS = {
    "obfuscation": {
        "entrypoint": obfuscation.entrypoint,
        "help": "Obfuscates payload strings into structured data formats",
        "ops": {
            "ip": {
                "help": "Converts bytes to IP address strings",
                "modes": {
                    "ipv4": "(default) Standard 32-bit IPv4 format (x.x.x.x)",
                    "ipv6": "Standard 128-bit IPv6 format (x:x:x:x:x:x:x:x)"
                }
            },
            "mac": {
                "help": "Converts bytes to MAC addresses",
                "modes": {
                    "unix": "(default) Colon-separated hex (xx:xx:xx:xx:xx:xx)",
                    "win": "Dash-separated hex (xx-xx-xx-xx-xx-xx)",
                    "net": "Cusco format (xxxx.xxxx.xxxx)",
                    "raw": "Raw contiguous hex string (xxxxxxxxxxxx)"
                }
            },
            "uuid": {
                "help": "Converts bytes to Universally Unique IDentifiable strings",
                "modes": {
                    "std": "(default) Standard RFC 4122 UUID format",
                    "win": "Windows registry string format"
                }
            },
            "email": {
                "help": "Converts bytes to fake email addresses",
                "modes": {
                    "std": (
                        "(default) 6-byte encoded email addresses (<firstName>."
                        "<middleInitial>.<lastName><Number>@<domain>.<tld>)"
                    ),
                }
            }
        }
    },
    "encryption" : {
        "entrypoint": encryption.entrypoint,
        "help": "Encrypts the payload using various cryptographic standards",
        "ops": {
            "aes": {
                "help": "Advanced Encryption Standard (AES), nonce and key are generated automatically.",
                "modes": {
                    "gcm": "(default) (AEAD) Galois/Counter mode: very fast and parallelizable",
                    "ocb3": "(AEAD) Offset Codebook Mode v3: very fast and parallelizable",
                    "ctr": "(Non-AEAD) Counter Mode: fast and parallelizable; turns AES into a stream cipher"
                },
                "extras": {
                    "key_size": "128, 192, or 256 (default)"
                }
            },
            "rc4": {
                "help": "Rivest Cipher 4 stream cipher",
                "modes": {}
            },
            "xor": {
                "help": "Exclusive-OR byte manipulation",
                "modes": {
                    "256": "(default) Uses a 256-bit key",
                    "192": "Uses a 192-bit key",
                    "128": "Uses a 128-bit key"
                }
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
    "extras",
    "formats",
    "all"
]

# =======  Helpers  ========================================================= #

# For future implementation
def _format_table(cols: list[str], rows = list[str], line_limit = MAX_PRINT_WIDTH):
    pass

def verify_extras(parser: MyParser, args: argparse.Namespace):
    # transform and op are already validated in `parse_args()`
    transform = args.transform
    op = args.op
    extras = args.extra or []

    for arg in extras:
        if "=" not in arg:
            parser.error(f"Invalid extra argument '{arg}'. Use: <extra_name>=<extra_value> (example: key_size=256)")
        
        arg_n = arg.split("=")[0]
        extras_list = list(TRANSFORMS[transform]["ops"][op].get("extras", {}).keys())
        if not extras_list:
            parser.error(f"Provided operation doen't support 'extras', try with a different one: {op}")

        if arg_n not in extras_list:
            parser.error(f"Invalid extra argument. Must be one of: {', '.join(extras_list)}")

def build_list_choices(choice: str) -> None:
    if choice not in LIST_CHOICES:
        raise ValueError(f"Invalid list target '{choice}. Value values: {', '.join(LIST_CHOICES)}")

    sep = "    "
    choices_map = {
        "transforms": {
            "lvl": 1,
            "metavar": "type",
            "section_header":   "Payload Transforms [--transform <type>]",
            "column_header":     f"{sep}{'Name':<17}{'Description'}",
            "column_header_sep": f"{sep}{'----':<17}{'-----------'}",
            "data_rows_padding": [17]
        },
        "ops": {
            "lvl": 2,
            "metavar": "value",
            "section_header":   "Payload Operations [--op <value>]",
            "column_header":     f"{sep}{'Transform':<17}{'Name':<13}{'Description'}",
            "column_header_sep": f"{sep}{'---------':<17}{'----':<13}{'-----------'}",
            "data_rows_padding": [17, 13]
        },
        "modes": {
            "lvl": 3,
            "metavar": "value",
            "section_header":   "Operation Modes [--mode <value>]",
            "column_header":     f"{sep}{'Operation':<17}{'Name':<13}{'Description'}",
            "column_header_sep": f"{sep}{'---------':<17}{'----':<13}{'-----------'}",
            "data_rows_padding": [17, 13]
        },
        "extras": {
            "lvl": 3,
            "metavar": "value",
            "section_header":   "Extras Types [--extra <value>]",
            "column_header":     f"{sep}{'Operation':<17}{'Name':<20}{'Description'}",
            "column_header_sep": f"{sep}{'---------':<17}{'----':<20}{'-----------'}",
            "data_rows_padding": [17, 20]
        },
        "formats": {
            "metavar": "value",
            "section_header":   "Output Formats [--format <value>]",
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
        
        if choice not in ("modes", "extras"):
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
                ops = TRANSFORMS[transform]["ops"]
                if choice == "extras" and not any(op_data.get("extras") for op_data in ops.values()):
                    # No extras, skip this transform "section"
                    continue

                print(f"{sep}=== {transform.upper()} ===")
                print(choices_map[choice]["column_header"])
                print(choices_map[choice]["column_header_sep"])

                pad1 = cast(int, choices_map[choice]["data_rows_padding"][0])
                pad2 = cast(int, choices_map[choice]["data_rows_padding"][1])
                indent_size = pad1 + pad2

                for op, op_data in ops.items():
                    def print_wrapped(data: list[str]):
                        for line in wrapped[1:]:
                            print(f"{sep}{' ' * indent_size}{line}")

                    if choice == "modes":
                        for mode in op_data["modes"]:
                            help = op_data["modes"][mode]
                            wrapped = textwrap.wrap(help, width=MAX_PRINT_WIDTH-indent_size)
                            print(f"{sep}{op:<{pad1}}{mode:<{pad2}}{wrapped[0]}")
                            print_wrapped(wrapped)
                    elif choice == "extras" and op_data.get("extras"):
                        for extra_n, extra_h in op_data["extras"].items():
                            wrapped = textwrap.wrap(extra_h, width=MAX_PRINT_WIDTH-indent_size)
                            print(f"{sep}{op:<{pad1}}{extra_n:<{pad2}}{wrapped[0]}")
                            print_wrapped(wrapped)             

def build_op_choices(parser: MyParser) -> list[str]:
    transform_str = sys.argv[(sys.argv.index("-t") if "-t" in sys.argv else sys.argv.index("--transform")) + 1]

    try:
        ops = list(TRANSFORMS[transform_str]["ops"].keys())
    except KeyError:
        parser.error(f"Invalid transform: '{transform_str}' (use --list transforms to list)")

    return ops

def build_mode_choices(parser: MyParser) -> list[str]:
    transform_str = sys.argv[(sys.argv.index("-t") if "-t" in sys.argv else sys.argv.index("--transform")) + 1]
    op_str = sys.argv[(sys.argv.index("--op")) + 1]

    try:
        modes = list(TRANSFORMS[transform_str]["ops"][op_str]["modes"].keys())
    except KeyError:
        parser.error(f"Invalid op '{op_str}' for '{transform_str}' transform (use --list ops to list)")

    return modes

def build_mode_default(parser: MyParser) -> str:
    transform_str = sys.argv[(sys.argv.index("-t") if "-t" in sys.argv else sys.argv.index("--transform")) + 1]
    op_str = sys.argv[(sys.argv.index("--op")) + 1]

    try:
        mode = list(TRANSFORMS[transform_str]["ops"][op_str]["modes"])[0]
    except KeyError:
        parser.error(f"2 Invalid op '{op_str}' for '{transform_str}' transform (use --list ops to list)")

    return mode


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
        choices=build_op_choices(parser) if any(arg in sys.argv for arg in ["-t", "--transform"]) else [],
        help="Operation to run (use --list ops to list)"
    )
    parser.add_argument(
        "-m", "--mode",
        metavar="<mode>",
        default=build_mode_default(parser) if any(arg in sys.argv for arg in ["--op"]) else None,
        choices=build_mode_choices(parser) if any(arg in sys.argv for arg in ["--op"]) else [],
        help="Mode variant for the selected operation. Depends on --transform and --op (use --list modes to list)"
    )
    parser.add_argument(
        "-x", "--extra",
        metavar="<arg>",
        nargs="*",
        help="Additional arguments for the selected mode, only needed in a few cases (use --list extras to list). Must be in the form: <extra_name>=<extra_value>"
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

    args = parser.parse_args()
    verify_extras(parser, args)

    return args

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
    
    entrypoint = cast(Callable[[bytes, str, str, list[str], str], str], TRANSFORMS[args.transform]["entrypoint"])
    result = entrypoint(data, args.op, args.mode, args.extra, args.format)
    if not result:
        LOGGER.error("Result is empty after aplying %r (%r), something went wrong...", args.mode, args.transform)
        return -1

    io.write_data(result.encode(), args.out)
    return 0

if __name__ == "__main__":
    main()