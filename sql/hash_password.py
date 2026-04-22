#!/usr/bin/env python3
import getpass
import sys

import bcrypt


def main() -> None:
    if len(sys.argv) > 1:
        plaintext = sys.argv[1]
    else:
        plaintext = getpass.getpass("Plaintext password: ")
    print(bcrypt.hashpw(plaintext.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"))


if __name__ == "__main__":
    main()
