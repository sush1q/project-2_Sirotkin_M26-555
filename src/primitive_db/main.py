#!/usr/bin/env python3
from . import engine


def main():
    print("Первая попытка запустить проект!\n***")
    while True:
        engine.welcome()

if __name__ == "__main__":
    main()
