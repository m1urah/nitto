"""Generate gperf lookup tables for email-based obfuscation"""

import os
import re
import shutil
import subprocess
import sys
import textwrap
import time
import unicodedata
from typing import Literal

from faker import Faker


# =======  Constants  ======================================================= #

FIRST_NAMES_COUNT = 4096
LAST_NAMES_COUNT = 4096
MAX_ELEMENT_SIZE = 21
LOCALES = [
    # English
    "en",
    "en_US",
    "en_GB",
    "en_CA",
    "en_AU",

    # Spanish
    "es",
    "es_ES",
    "es_MX",
    "es_AR",
    "es_CO",

    # Portuguese
    "pt",
    "pt_PT",
    "pt_BR",

    # German
    "de",
    "de_DE",
    "de_AT",
    "de_CH",

    # Other
    "fr_FR",
    "it_IT"
]
FAKE = Faker(LOCALES)

ASCII_FOLDS = {
    "ß": "ss",
    "æ": "ae",
    "Æ": "ae",
    "œ": "oe",
    "Œ": "oe",
    "ø": "o",
    "Ø": "o",
    "ł": "l",
    "Ł": "l",
}


# =======  Others  ========================================================== #

DOMAINS = [ # 32 options
    "gmail", "yahoo", "outlook", "hotmail", "live", "icloud", "mail",
    "protonmail", "zoho", "yandex", "aol", "msn", "gmx", "web", "qq",
    "mailru",  "naver", "rediffmail", "comcast", "orange", "t-online",
    "btinternet",  "verizon", "att", "rogers", "sky", "virginmedia",
    "charter",  "cox", "freenet", "rambler", "libero"
]
TLDS = [    # 32 options
    "com", "net", "org", "edu", "xyz", "in fo", "io", "me", "co", 
    "biz", "es", "de", "uk", "fr", "ca", "au", "jp", "cn", "br",
    "it", "nl", "ru", "in", "mx", "pl", "be", "se", "at", "eu",
    "ai", "cloud", "online"
]
MIDDLE = [  # 32 options
    "a","b","c","d","e","f","g","h","i","j","k","l","m",
    "n","o","p","q","r","s","t","u","v","w","x","y","z",
    "cb", "cc", "rc", "zz", "gg", "ad"
]


# =======  Funcs  =========================================================== #

def to_ascii(text: str) -> str:
    for src, dst in ASCII_FOLDS.items():
        text = text.replace(src, dst)

    normalized = unicodedata.normalize("NFKD", text)
    stripped = "".join(
        c for c in normalized
        if not unicodedata.combining(c) and not c.isspace() # remove any space in compound names
    )

    return stripped.encode("ascii", "ignore").decode("ascii")

def generate_hash_table(
        what: Literal["first", "last", "other"],
        suffix: str,
        file_name: str
):
    if not shutil.which("gperf"):
        print("[!] gperf is not installed. Install it to automate hash table generation.")

    print("[*] Creating header file...")
    try:
        func_name = "Get" + what.capitalize() + suffix.capitalize()[:-1]  # Remove final s
        hash_name = "Hash" + what.capitalize() + suffix.capitalize()[:-1]
        gperf_file = file_name
        header_file = file_name.split(".")[0] + ".h"

        out = subprocess.run(
            ["gperf", "-t", "-K", "key", "-N", func_name, "-H", hash_name, "-C", gperf_file],
            check=True, capture_output=True, text=True
        )

        out_str = re.sub(r"^#line.*\n?", "", out.stdout, flags=re.MULTILINE)

        index = out_str.find("#if") - 1
        out_str = out_str[:index] + textwrap.dedent(f"""
            #pragma once
            #ifndef {what.upper()}_{suffix.upper()}_H
            #define {what.upper()}_{suffix.upper()}_H

            #include <string.h>
        """) + "\n" + out_str[index+1:]

        with open(header_file, "w", encoding="utf-8") as f:
            # Remove all #line directives
            f.write(out_str)
            f.write(f"\n#endif // {what.upper()}_{suffix.upper()}_H")
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[-] Program is not installed or failed to run")

def generate_list(what: Literal["first", "last", "other"], count: int, count_indiv: int) -> list[str]:
    time_start = time.time()
    
    iter = 0
    items: list[str] = []
    while len(items) < count:
        # Print every 5s
        elapsed = int(time.time() - time_start)
        if elapsed and (elapsed % 5) == 0:
            print(f"[*] Still creating | idx={iter} | elapsed={elapsed}s")

        # Don't use unique with FAKE, takes longer. It's easier to keep it "random"
        item = ""
        if what == "first":
            item = FAKE.first_name().lower()
        elif what == "last":
            item = FAKE.last_name().lower()
        else:
            if iter < 32:
                item = MIDDLE[iter]
            elif iter >= 32 and iter < 64:
                item = DOMAINS[iter % count_indiv]
            else:
                item = TLDS[iter % count_indiv]

        if len(item) > MAX_ELEMENT_SIZE:
            print(f"[!] Found element bigger than {MAX_ELEMENT_SIZE}, skiping it: {item}")
            continue
        
        item_ascii = to_ascii(item)
        if item_ascii in items:
            iter+=1
            continue

        items.append(item_ascii)
        iter+=1

    print(f"[+] List generated after {iter} iterations and {int(time.time() - time_start)} seconds")
    return items

def generate_gperf_header(what: Literal["first", "last", "other"], file_name: str, count: int, count_indiv: int) -> None:
    suffix = "names" if what != "other" else "words"
    print(f"[*] Generating list of {what} {suffix}, this migh take some seconds...")

    # ===  LIST OF NAMES/WORDS  ===
    items_list = generate_list(what, count, count_indiv)
    items_with_idx = [
        f"{item + ',':<{MAX_ELEMENT_SIZE + 1}}{i % count}"
        for i, item in enumerate(items_list)
    ]

    # ===  GPERF FILE  ===
    struct_str = textwrap.dedent(f"""\
    %{{
    typedef struct {what.upper()}_{suffix.upper()[:-1]} {{
        const char *key;
        int idx;
    }} {what.upper()}_{suffix.upper()[:-1]}, *P{what.upper()}_{suffix.upper()[:-1]};
    %}}
    struct {what.upper()}_{suffix.upper()[:-1]};
    %%""")

    with open(file_name, "w", encoding="utf-8") as f:
        f.write(f"{struct_str}\n")
        f.writelines("\n".join(items_with_idx))

    # ===  C HEADER  ===
    generate_hash_table(what, suffix, file_name)
    

if __name__ == "__main__":
    wordlists_dir = os.path.dirname(__file__) + "/wordLists"
    first_file_name = f"{wordlists_dir}/firstNames.gperf"
    last_file_name = f"{wordlists_dir}/lastNames.gperf"
    others_file_name = f"{wordlists_dir}/others.gperf"

    response = ""
    if any([os.path.exists(path) for path in (first_file_name, last_file_name, others_file_name)]):
        response = input(
            "[!] There is already an existing list on the "
            f"'{os.path.basename(wordlists_dir)}' directory, do you want to continue? (Y/N) "
        )
    
        while response.upper() not in ['Y', 'N']:
            response = input(
                "[-] Invalid option, must be Y/N. Do you want to continue? "
            )

        response = response.upper()
    else:
        response = "Y"

    if response == "N":
        print("[*] Exiting...")
        sys.exit(0)

    generate_gperf_header("first", first_file_name, FIRST_NAMES_COUNT, FIRST_NAMES_COUNT)
    generate_gperf_header("last", last_file_name, LAST_NAMES_COUNT, LAST_NAMES_COUNT)
    generate_gperf_header("other", others_file_name, len(MIDDLE) + len(DOMAINS) + len(TLDS), 32)