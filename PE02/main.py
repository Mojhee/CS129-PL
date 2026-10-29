"""Entry point of the IOL compiler program (PE02: Lexical Analysis)."""
from gui import IDE


def main():
    """Open the IOL IDE and run it until the user exits."""
    app = IDE()       # IDE is the Tk root window class in gui.py
    app.mainloop()    # handle user actions until the window is closed


if __name__ == "__main__":
    main()
