from modules import *
import flet as ft
import os, sys

def _main():
    ft.app(lambda page: interface.main(page, os.path.abspath(os.path.join(sys.argv[0], '..', 'audio'))))

if __name__ == '__main__': _main()