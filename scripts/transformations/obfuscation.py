
from enum import Enum
from typing import Callable, Final, Literal, TypeAlias, cast, get_args

from utils.customLogger import LOGGER
from transformations.common import pad_buffer


# =======  Definitions  ===================================================== #

class ElementSize(Enum): # In bytes
    IPV4 = 4
    IPV6 = 16
    UUID = 16
    EMAIL = 0
    MAC = 6

IPMode : TypeAlias = Literal["ipv4", "ipv6"]
IP_MODES = list(get_args(IPMode))

MACMode : TypeAlias = Literal["unix", "win", "net", "none"]
MAC_MODES = list(get_args(MACMode))

UUIDMode : TypeAlias = Literal["std", "win"]
UUID_MODES = list(get_args(UUIDMode))

EmailMode : TypeAlias = Literal["temp", "temp2"]
EMAIL_MODES = list(get_args(EmailMode))

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

def obfuscate_email(mode: int, buf: bytes) -> list[str]:
    return []


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


# =======  MAC  ============================================================= #    """Converts a given set of bytes into it's MAC representation"""
    if len(data) != 6:
        raise ValueError(f"Input data must be exactly 6 bytes before conversion: {len(data)}")

    out = ""
    count = 0
    for i in range(0, len(data), groups_size):
        count += groups_size
        if (count < 6):
            out += f"{int.from_bytes(data[i:i+groups_size]):02X}".upper() + separator
        else:
            out += f"{int.from_bytes(data[i:i+groups_size]):02X}".upper()

    return out

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
    elif mode == "none":
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
            
            if (count < ElementSize.MAC.value):
                out_str += separator

        out_list.append(out_str)

    return out_list


# =======  Definitions  ===================================================== #

_OBFUSCATION_OPS = {
    "ip": {
        "function": obfuscate_ip,
        "modes": IP_MODES
    },
    "uuid": {
        "function": obfuscate_uuid,
        "modes": UUID_MODES
 
    },
    "email": {
        "function": obfuscate_email,
        "modes": EMAIL_MODES
    },
    "mac": {
        "function": obfuscate_mac,
        "modes": MAC_MODES
    },
}

MODES = {op: value["modes"] for op, value in _OBFUSCATION_OPS.items()}
OPS = [op for op in _OBFUSCATION_OPS.keys()]


# =======  Entrypoint  ====================================================== #

def entrypoint(data: bytes, transform: str, format: str) -> str:
    mode = _OBFUSCATION_OPS.get(transform.lower())
    if not mode:
        raise ValueError(f"Invalid transform '{transform}' for mode obfuscation")

    chunk_size = mode["chunk_size"].value
    func = mode["function"]
    padded_data = pad_buffer(chunk_size, data)

    obfuscated_data = cast(list[str], func(chunk_size, padded_data))
    try:
        transform_func = cast(Callable[[list[str]], str], _TRANSFORMS[format.lower()])
    except KeyError:
        raise ValueError(f"Invalid output format '{format}' for mode obfuscation")

    transformed_data = transform_func(obfuscated_data)
    LOGGER.info("Payload size: before = %d bytes, after = %d bytes", len(data), len(transformed_data.encode()))
    
    return transformed_data