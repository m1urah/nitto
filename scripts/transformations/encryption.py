# =======  Handlers  ======================================================== #

def encrypt_aes(data: bytes) -> str:
    return ""

def encrypt_rc4(data: bytes) -> str:
    return ""

def encrypt_xor(data: bytes) -> str:
    return ""

_ENCRYPTION_MODES = {
    "aes": encrypt_aes,
    "rc4": encrypt_rc4,
    "xor": encrypt_xor
}

MODES = {}
OPS = [op for op in _ENCRYPTION_MODES.keys()]

# =======  Entrypoint  ====================================================== #

def entrypoint(data: bytes, transform: str, format: str):
    print(f"passed transform {transform}")
    pass