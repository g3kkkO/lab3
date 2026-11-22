from gui import Game
import tkinter as tk

if __name__ == "__main__":
    try:
        app = Game()
        app.mainloop()
    except tk.TclError as error:
        print(f"Не удалось запустить графическое окно: {error}")
