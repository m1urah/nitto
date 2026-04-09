"""Transforms payload bytes into obfuscated lists of IP, MAC, UUID, or email string representations."""

import os
from enum import Enum
import sys
from typing import Callable, Literal, TypeAlias, cast, get_args

from utils.customLogger import LOGGER
from transformations.common import pad_buffer


# =======  Definitions  ===================================================== #

class ElementSize(Enum): # In bytes
    IPV4  = 4
    IPV6  = 16
    UUID  = 16
    EMAIL = 6
    MAC   = 6

IPMode : TypeAlias = Literal["ipv4", "ipv6"]
IP_MODES = list(get_args(IPMode))

MACMode : TypeAlias = Literal["unix", "win", "net", "raw"]
MAC_MODES = list(get_args(MACMode))

UUIDMode : TypeAlias = Literal["std", "win"]
UUID_MODES = list(get_args(UUIDMode))

EmailMode : TypeAlias = Literal["std"]
EMAIL_MODES = list(get_args(EmailMode))

FIRST_NAMES_PATH = f"scripts/helpers/wordLists/firstNames.gperf"
LAST_NAMES_PATH = f"scripts/helpers/wordLists/lastNames.gperf"

# =======  Transformation  ================================================== #

def _transform_common(data: list[str]) -> str:
    out = ""
    line = "    "
    for item in data:
        if len(line) + len(item) > 90:
            out += line + "\n"
            line = "    "
        if line.strip():
            line += " "
        
        line += "\"" + item + "\""
        if item == data[-1]:
            out += line + "\n"
        else:
            line += ","

    return out

def _transform_into_python(data: list[str]) -> str:
    out = "buf = [\n"
    out += _transform_common(data)
    return out + "]\n"

def _transform_into_c(data: list[str]) -> str:
    out = "const unsigned char *buf[] = {\n"
    out += _transform_common(data)
    return out + "};\n"

_TRANSFORMS = {
    "c": _transform_into_c,
    "python": _transform_into_python
}


# =======  Email  =========================================================== #

DOMAINS = [ # 32 options
    "gmail", "yahoo", "outlook", "hotmail", "live", "icloud", "mail",
    "protonmail", "zoho", "yandex", "aol", "msn", "gmx", "web", "qq",
    "mailru",  "naver", "rediffmail", "comcast", "orange", "t-online",
    "btinternet",  "verizon", "att", "rogers", "sky", "virginmedia",
    "charter",  "cox", "freenet", "rambler", "libero"
]
TLDS = [    # 32 options
    "com", "net", "org", "edu", "xyz", "info", "io", "me", "co", 
    "biz", "es", "de", "uk", "fr", "ca", "au", "jp", "cn", "br",
    "it", "nl", "ru", "in", "mx", "pl", "be", "se", "at", "eu",
    "ai", "cloud", "online"
]
MIDDLE = [  # 32 options
    "a","b","c","d","e","f","g","h","i","j","k","l","m",
    "n","o","p","q","r","s","t","u","v","w","x","y","z",
    "cb", "es", "rc", "zz", "gg", "ad"
]

def _cleanup_names_list(names: list[str]) -> list[str]:
    start = 0 if "%%" not in names else names.index("%%") + 1

    out: list[str] = []
    for line in names[start:]:
        out.append(line.split(",")[0].strip())

    return out

def _get_resource_path(relative_path) -> str:
    """Get the absolute path to a resource when running on exe or not."""
    try:
        # PyInstaller creates a temp folder and stores its path in sys._MEIPASS
        base_path = sys._MEIPASS # type: ignore
    except AttributeError:
        # Find the dir where the word lists exists
        current = os.path.dirname(__file__)
        while current != os.path.dirname(current): # Stop at root
            test_path = os.path.join(current, relative_path)
            if os.path.exists(test_path):
                return test_path
            current = os.path.dirname(current)

        base_path = os.getcwd()

    return os.path.join(base_path, relative_path)

def obfuscate_email(mode: EmailMode, buf: bytes) -> list[str]:
    if mode not in EMAIL_MODES:
        raise ValueError(f"Incorrect mode provided, must be one of {", ".join(EMAIL_MODES)}: {mode}")

    with open(_get_resource_path(FIRST_NAMES_PATH), "r") as f:
        first_names = f.read().splitlines()
    with open(_get_resource_path(LAST_NAMES_PATH), "r") as f:
        last_names = f.read().splitlines()

    FIRST_NAMES = _cleanup_names_list(first_names)
    LAST_NAMES = _cleanup_names_list(last_names)

    out_list: list[str] = []
    for i in range(0, len(buf), ElementSize.EMAIL.value):
        element = int.from_bytes(buf[i:i+ElementSize.EMAIL.value])

        tld_idx     = element & 0x1F           # Last 5 bits
        domain_idx  = (element >> 5) & 0x1F    # Next 5 bits
        number      = (element >> 10) & 0x1FF  # Next 9 bits
        last_idx    = (element >> 19) & 0xFFF  # Next 12 bits
        middle_idx  = (element >> 31) & 0x1F   # Next 5 bits
        first_idx   = (element >> 36) & 0xFFF  # First 12 bits

        out_str = ""
        
        out_str += FIRST_NAMES[first_idx]
        out_str += "." + MIDDLE[middle_idx]
        out_str += "." + LAST_NAMES[last_idx]
        out_str += str(number)
        out_str += "@" + DOMAINS[domain_idx]
        out_str += "." + TLDS[tld_idx]

        out_list.append(out_str)

    return out_list

# =======  UUID  ============================================================ #

def obfuscate_uuid(mode: UUIDMode, buf: bytes) -> list[str]:
    """Converts the buf into a list of UUIDs"""
    if mode not in UUID_MODES:
        raise ValueError(f"Incorrect mode provided, must be one of {", ".join(UUID_MODES)}")

    def format_bytes(b: bytes, s: int, f: Literal['little', 'big']):
        return f"{int.from_bytes(b, f):0{s*2}X}".upper()

    out_list: list[str] = []
    separator = '-'
    for i in range(0, len(buf), ElementSize.UUID.value):
        element = buf[i:i+ElementSize.UUID.value]
        out_str = ""

        first_endianness = "little" if mode == 'win' else "big"
        
        out_str += format_bytes(element[0:4], 4, first_endianness) + separator
        out_str += format_bytes(element[4:6], 2, first_endianness) + separator
        out_str += format_bytes(element[6:8], 2, first_endianness) + separator
        out_str += format_bytes(element[8:10], 2, "big") + separator
        out_str += format_bytes(element[10:16], 6, "big")

        out_list.append(out_str)

    return out_list


# =======  MAC  ============================================================= #

def obfuscate_mac(mode: MACMode, buf: bytes) -> list[str]:
    """Converts the buf into a list of MACs based on mode."""
    if mode not in MAC_MODES:
        raise ValueError(f"Incorrect mode provided, must be one of {", ".join(MAC_MODES)}")
    
    if mode == "unix":
        group_size = 1  # Bytes
        separator = ':'
    elif mode == "win":
        group_size = 1
        separator = '-'
    elif mode == "net":
        group_size = 2
        separator = '.'
    elif mode == "raw":
        group_size = 2
        separator = ''

    out_list: list[str] = []
    for i in range(0, len(buf), ElementSize.MAC.value):
        element = buf[i:i+ElementSize.MAC.value]

        out_str = ""
        count = 0
        for j in range(0, len(element), group_size):
            count += group_size
            out_str += f"{int.from_bytes(element[j:j+group_size]):0{group_size*2}X}".upper()
            if (count < ElementSize.MAC.value):
                out_str += separator

        out_list.append(out_str)

    return out_list


# =======  IP  ============================================================== #

def obfuscate_ip(mode: IPMode, buf: bytes) -> list[str]:
    """Converts the buf into a list of IPs based on the chunk_size (ip mode)"""
    if mode not in IP_MODES:
        raise ValueError(f"Incorrect mode provided, must be one of {", ".join(IP_MODES)}")

    if mode == "ipv4":
        separator = '.'
        group_size = 1  # Bytes
        total_size = ElementSize.IPV4.value
    else:
        separator = ':'
        group_size = 2
        total_size = ElementSize.IPV6.value

    out_list: list[str] = []
    for i in range(0, len(buf), total_size):
        element = buf[i:i+total_size]

        out_str = ""
        count = 0
        for j in range(0, len(element), group_size):
            count += group_size
            if total_size == ElementSize.IPV4.value:
                out_str += f"{int.from_bytes(element[j:j+group_size])}"
            else:
                out_str += f"{int.from_bytes(element[j:j+group_size]):04X}".upper()
            
            if (count < len(element)):
                out_str += separator

        out_list.append(out_str)

    return out_list


# =======  Definitions  ===================================================== #

_OBFUSCATION_OPS = {
    "ip": {
        "function": obfuscate_ip,
        "modes": IP_MODES,
        "element_size": {
            "ipv4": ElementSize.IPV4,
            "ipv6": ElementSize.IPV6,
        }
    },
    "uuid": {
        "function": obfuscate_uuid,
        "modes": UUID_MODES,
        "element_size": ElementSize.UUID
 
    },
    "email": {
        "function": obfuscate_email,
        "modes": EMAIL_MODES,
        "element_size": ElementSize.EMAIL
    },
    "mac": {
        "function": obfuscate_mac,
        "modes": MAC_MODES,
        "element_size": ElementSize.MAC
    },
}

MODES = {op: value["modes"] for op, value in _OBFUSCATION_OPS.items()}
OPS = [op for op in _OBFUSCATION_OPS.keys()]


# =======  Entrypoint  ====================================================== #

def entrypoint(data: bytes, op: str, mode: str, extras: list[str], format: str) -> str:
    op_el = _OBFUSCATION_OPS.get(op)
    if not op_el:
        raise ValueError(f"Invalid op '{op}' for obfuscation")

    element_size = op_el["element_size"]
    if isinstance(element_size, dict):
        element_size = element_size[mode].value
    else:
        element_size = element_size.value
    func = op_el["function"]

    padded_data = pad_buffer(element_size, data)
    obfuscated_data = cast(list[str], func(mode, padded_data))
    try:
        transform_func = cast(Callable[[list[str]], str], _TRANSFORMS[format.lower()])
    except KeyError:
        raise ValueError(f"Invalid output format '{format}' for mode obfuscation")

    transformed_data = transform_func(obfuscated_data)
    LOGGER.info("Payload size: before = %d bytes, after = %d bytes", len(data), len(transformed_data.encode()))
    
    return transformed_data