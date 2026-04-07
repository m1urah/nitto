"""Common stuff used across the script."""

def pad_buffer(pad_size: int, buff: bytes) -> bytes:
    """Simple implementation of PKCS#7 (we always pad, even on dataLength % pad_size = 0)"""
    buf_size = len(buff)
    needed_padding = pad_size - (buf_size % pad_size)

    buff_padded = buff + int.to_bytes(needed_padding) * needed_padding
    return buff_padded
