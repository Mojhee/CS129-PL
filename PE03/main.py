"""Entry point of the non-recursive predictive parser program (PE03)."""
from gui import ParserApp


def main():
    """Open the parser window and run it until the user closes it."""
    app = ParserApp()   # ParserApp is the Tk root window class in gui.py
    app.mainloop()      # handle user actions until the window is closed


if __name__ == "__main__":
    main()
