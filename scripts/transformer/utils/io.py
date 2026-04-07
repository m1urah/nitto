"""Input/Output helper functions."""

import sys
from pathlib import Path

from utils.customLogger import LOGGER


# =======  Helpers  ========================================================= #

def _write_file(path: Path, data: bytes) -> None:
    if path.exists() and path.is_dir():
        raise ValueError("Output file is a directory.")
    
    with open(path, "wb") as f:
        f.write(data)

def _read_file(path: Path) -> bytes:
    if not path.exists():
        raise FileNotFoundError(f"The specified file doesn't exist: {path}. Please create the file and try again.")

    with open(path, "rb") as f:
        read_bytes = f.read()
        if len(read_bytes) == 0:
            raise ValueError(f"The file {path} is empty. Please provide a file with valid content.")
        return read_bytes


# =======  Entrypoint  ====================================================== #

def write_data(data: bytes, path: Path | None = None) -> None:
    """Writes data to path, or stdin (if no path)."""
    if not data:
        raise ValueError("Won't write empty data")

    if path:
        _write_file(path, data)
        LOGGER.info("Transformed payload saved as: %s", path.name)
    else:
        LOGGER.info("Transformed payload: ")
        print(data.decode())

def read_data(path: Path | None = None) -> bytes:
    data = b""
    if not path:
        LOGGER.info("Using stdin as input data.")
        for line in sys.stdin:
            data += line.encode()

        if not data:
             raise IOError("No data provided via stdin, and no valid file path specified. Please provide a valid file path.")
        data = data.rstrip(b'\n')

    else:
        try:
            data = _read_file(path)
        except (FileNotFoundError, ValueError) as e:
            raise

    return data
