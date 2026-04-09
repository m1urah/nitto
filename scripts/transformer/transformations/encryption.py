"""Encrypt a payload with different types of ciphers: AES, ChaCha, RC4, and XOR."""

import os
import struct
from dataclasses import dataclass
from typing import Callable, Literal, TypeAlias, cast, get_args

from cryptography.hazmat.primitives.ciphers.aead import AESGCM, AESOCB3
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from utils.customLogger import LOGGER

# =======  Definitions  ===================================================== #

AESMode: TypeAlias = Literal["gcm", "ocb3", "ctr"]
AES_MODES = list(get_args(AESMode))

AESExtras : TypeAlias = Literal["key_size"]
AES_EXTRAS = {
    "key_size": [128, 192, 256]
}

XORMode: TypeAlias = Literal["128", "192", "256"]
XOR_MODES = list(get_args(XORMode))

@dataclass
class EncResult:
    key: bytes
    nonce_or_iv: bytes | None
    ciphertext: bytes

EncryptHandler: TypeAlias = Callable[[str, list[str], bytes], EncResult]


# =======  Transformation  ================================================== #

def _transform_common(data: bytes, prefix: str = "") -> str:
    out = ""
    line = prefix
    for byte in data:
        item = f"\\x{byte:02x}"
        if len(line) + len(item) > 90:
            out += line + "\"" + "\n"
            line = prefix
        
        line += item
        if item == f"\\x{data[-1]:02x}":
            out += line + "\""
            break

    return out

def _transform_into_python(data: bytes, buf_name: str = "buf") -> str:
    out = f"{buf_name} =  b\"\"\n"
    out += _transform_common(data, prefix=f"{buf_name} += b\"")
    return out

def _transform_into_c(data: bytes, buf_name: str = "buf") -> str:
    out = f"const unsigned char {buf_name}[] =\n"
    out += _transform_common(data, prefix="\"")
    return out + ";"

_TRANSFORMS = {
    "c": _transform_into_c,
    "python": _transform_into_python,
}


# =======  Handlers  ======================================================== #

def _aes_handler(mode: str, extras: list[str], buf: bytes) -> EncResult:
    """Encrypts buf using AES based on 'mode', then returns (key, nonce/iv, ciphertext)"""
    key_val: int = 256

    if mode not in AES_MODES:
        raise ValueError(f"Incorrect mode provided, must be one of {', '.join(AES_MODES)}")
    for extra_n, extra_v in extras:
        if extra_n not in AES_EXTRAS.keys():
            raise ValueError(f"Invalid extra argument. Must be one of: {', '.join(AES_EXTRAS.keys())}")
        
        if extra_v not in AES_EXTRAS["key_size"]:
            raise ValueError(f"Invalid extra value for {extra_n} argument. Must be one of: {', '.join(str(v) for v in AES_EXTRAS["key_size"])}")
        key_val = int(extra_v)
    
    nonce = b""
    iv = b""
    if mode == "gcm":
        nonce = os.urandom(12)
        key = AESGCM.generate_key(bit_length=key_val)
        cipher = AESGCM(key)
        ct = cipher.encrypt(nonce, buf, None)
    elif mode == "ocb3":
        nonce = os.urandom(12)
        key = AESOCB3.generate_key(bit_length=key_val)
        cipher = AESOCB3(key)
        ct = cipher.encrypt(nonce, buf, None)
    else: # ctr
        iv = os.urandom(16)
        key = os.urandom(key_val // 8) # 32, 24 or 16
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        ct = encryptor.update(buf) + encryptor.finalize()

    return EncResult(key=key, nonce_or_iv=nonce or iv, ciphertext=ct)

def _chacha20_handler(mode: str, extras: list[str], buf: bytes) -> EncResult:
    """Encrypts buf using ChaCha20', then returns (key, nonce, ciphertext)"""
    key = os.urandom(32) # 256-bit
    nonce = os.urandom(8)
    counter = 0

    full_nonce = struct.pack("<Q", counter) + nonce
    algorithm = algorithms.ChaCha20(key, full_nonce)
    cipher = Cipher(algorithm, mode=None)
    encryptor = cipher.encryptor()
    ct = encryptor.update(buf)

    return EncResult(key=key, nonce_or_iv=nonce, ciphertext=ct)

def _rc4_handler(mode: str, extras: list[str], buf: bytes) -> EncResult:
    """Encrypts using the deprecated, yet fast RC4 cipher, then returns (key, ciphertext)"""
    key = os.urandom(16)
    algorithm = algorithms.ARC4(key)
    cipher = Cipher(algorithm, mode=None)
    encryptor = cipher.encryptor()
    ct = encryptor.update(buf)

    return EncResult(key=key, nonce_or_iv=None, ciphertext=ct)

def _xor_handler(mode: str, extras: list[str], buf: bytes) -> EncResult:
    """XOR-encrypt buf with a random key, repeating it to match the buffer length, then returns (key, ciphertext)"""
    if mode not in XOR_MODES:
        raise ValueError(f"Incorrect mode provided, must be one of {', '.join(XOR_MODES)}")

    def extend_repeat(data: bytes, target_len: int) -> bytes:
        return (data * ((target_len + len(data) - 1) // len(data)))[:target_len] # ceil

    key_og = os.urandom(int(mode) // 8)
    print(f"key len = {len(key_og)}")
    key = extend_repeat(key_og, len(buf))
    ct = bytes([a ^ b for a, b in zip(buf, key)])

    return EncResult(key=key_og, nonce_or_iv=None, ciphertext=ct)

_ENCRYPTION_OPS = {
    "aes": _aes_handler,
    "chacha20": _chacha20_handler,
    "rc4": _rc4_handler,
    "xor": _xor_handler
}

OPS = [op for op in _ENCRYPTION_OPS.keys()]


# =======  Entrypoint  ====================================================== #

def entrypoint(data: bytes, op: str, mode: str, extras: list[str], format: str) -> str:
    handler = _ENCRYPTION_OPS.get(op)
    if not handler:
        raise ValueError(f"Invalid op '{op}' for encryption")
    
    try:
        transform_func = cast(Callable[[bytes, str], str], _TRANSFORMS[format.lower()])
    except KeyError:
        raise ValueError(f"Invalid output format '{format}' for mode obfuscation")
    
    enc_result = cast(EncResult, handler(mode, extras, data))
    key = "".join(f"\\x{byte:02x}" for byte in enc_result.key)
    nonce_or_iv = "".join(f"\\x{byte:02x}" for byte in enc_result.nonce_or_iv) if enc_result.nonce_or_iv else "none used"
    
    out_data = transform_func(enc_result.ciphertext, "buf")
    out_key = transform_func(enc_result.key, "key")
    out_nonce_or_iv = transform_func(enc_result.nonce_or_iv, "nonce_or_iv") if enc_result.nonce_or_iv else None

    LOGGER.info("Encrypted with: key = %s, nonce/iv = %s", key, nonce_or_iv)
    LOGGER.info("Encrypted with:")
    print(out_key)
    if out_nonce_or_iv: print(out_nonce_or_iv)
    LOGGER.info("Payload size: before = %d bytes, after = %d bytes", len(data), len(out_data.encode()))

    return out_data