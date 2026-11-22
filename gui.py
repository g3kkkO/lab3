import tkinter as tk
from tkinter import messagebox
from board import Board

class Game(tk.Tk):
    """Графический интерфейс для класса Board."""

    COLORS = [
        "black", "blue", "green", "red",
        "purple", "brown", "teal", "black", "gray"
    ]

    def __init__(self):
        super().__init__()

        self.title("Сапёр")
        self.geometry("450x450")
        self.minsize(270, 270)

        self.board = Board()
        self.restart_id = None
        self.cell_width = 1
        self.cell_height = 1

        self.create_menu()


        self.canvas = tk.Canvas(
            self,
            background="white",
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)


        self.canvas.bind("<Configure>", self.draw)

        self.canvas.bind("<Button-1>", self.left_click)
        self.canvas.bind("<Button-3>", self.right_click)
        self.canvas.bind("<Control-Button-1>", self.right_click)

        self.bind("<F2>", self.new_game)

        self.draw()

    def create_menu(self):
        menu = tk.Menu(self)

        game_menu = tk.Menu(menu, tearoff=False)
        game_menu.add_command(
            label="Новая игра",
            accelerator="F2",
            command=self.new_game
        )
        game_menu.add_separator()
        game_menu.add_command(label="Выход", command=self.destroy)

        menu.add_cascade(label="Игра", menu=game_menu)

        settings_menu = tk.Menu(menu, tearoff=False)
        settings_menu.add_command(
            label="Размер окна",
            command=self.window_settings
        )
        menu.add_cascade(label="Настройки", menu=settings_menu)

        self.config(menu=menu)

    def new_game(self, event=None):
        if self.restart_id is not None:
            self.after_cancel(self.restart_id)
            self.restart_id = None
        self.board = Board()
        self.draw()

    def get_cell(self, event):
        """Переводит координаты мыши в строку и столбец."""
        row = int(event.y // self.cell_height)
        col = int(event.x // self.cell_width)

        if (
            0 <= row < self.board.rows
            and 0 <= col < self.board.cols
        ):
            return row, col

        return None

    def left_click(self, event):
        cell = self.get_cell(event)

        if cell is not None:
            self.board.reveal(*cell)
            self.draw()
            if self.board.state == "lost" and self.restart_id is None:
                self.restart_id = self.after(2000, self.new_game)

        return "break"

    def right_click(self, event):
        cell = self.get_cell(event)

        if cell is not None:
            self.board.toggle_flag(*cell)
            self.draw()

        return "break"

    def draw(self, event=None):
        """Рисует поле на основании данных Board."""
        self.canvas.delete("all")

        width = max(1, self.canvas.winfo_width())
        height = max(1, self.canvas.winfo_height())

        self.cell_width = width / self.board.cols
        self.cell_height = height / self.board.rows

        font_size = max(
            8,
            int(min(self.cell_width, self.cell_height) * 0.45)
        )

        for row in range(self.board.rows):
            for col in range(self.board.cols):
                cell = (row, col)

                x1 = col * self.cell_width
                y1 = row * self.cell_height
                x2 = x1 + self.cell_width
                y2 = y1 + self.cell_height

                background = "#aebed0"
                text = ""
                text_color = "black"

                if (
                    self.board.state == "lost"
                    and cell in self.board.mines
                ):
                    background = "#ef7777"
                    text = "*"

                elif cell in self.board.flags:
                    text = "⚑"
                    text_color = "red"

                    if (
                        self.board.state == "lost"
                        and cell not in self.board.mines
                    ):
                        text = "×"

                elif cell in self.board.opened:
                    background = "#eeeeee"
                    number = self.board.number(row, col)

                    if number > 0:
                        text = str(number)
                        text_color = self.COLORS[number]

                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=background,
                    outline="#78899a"
                )

                self.canvas.create_text(
                    (x1 + x2) / 2,
                    (y1 + y2) / 2,
                    text=text,
                    fill=text_color,
                    font=("Arial", font_size, "bold")
                )

        if self.board.state == "won":
            self.title("Сапёр — победа! F2: новая игра")
        elif self.board.state == "lost":
            self.title("Сапёр — поражение. Новая игра через 2 секунды")
        else:
            remaining = self.board.mine_count - len(self.board.flags)
            self.title(f"Сапёр — осталось флагов: {remaining}")

    def window_settings(self):
        """Открывает диалог настройки ширины и высоты окна."""
        dialog = tk.Toplevel(self)
        dialog.title("Размер окна")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(dialog, text="Ширина:").grid(
            row=0, column=0, padx=10, pady=10
        )
        width_entry = tk.Entry(dialog, width=12)
        width_entry.grid(row=0, column=1, padx=10, pady=10)
        width_entry.insert(0, str(self.winfo_width()))

        tk.Label(dialog, text="Высота:").grid(
            row=1, column=0, padx=10, pady=10
        )
        height_entry = tk.Entry(dialog, width=12)
        height_entry.grid(row=1, column=1, padx=10, pady=10)
        height_entry.insert(0, str(self.winfo_height()))

        def apply_size():
            try:
                width = int(width_entry.get())
                height = int(height_entry.get())

                if not (
                    270 <= width <= self.winfo_screenwidth()
                    and 270 <= height <= self.winfo_screenheight()
                ):
                    raise ValueError(
                        "Размеры должны быть не меньше 270 "
                        "и не больше размеров экрана."
                    )

                self.geometry(f"{width}x{height}")

            except (ValueError, tk.TclError) as error:
                messagebox.showerror(
                    "Ошибка",
                    f"Введите допустимые целые размеры.\n{error}",
                    parent=dialog
                )
                return

            dialog.destroy()

        tk.Button(
            dialog,
            text="Применить",
            command=apply_size
        ).grid(row=2, column=0, padx=10, pady=10)

        tk.Button(
            dialog,
            text="Отмена",
            command=dialog.destroy
        ).grid(row=2, column=1, padx=10, pady=10)

        width_entry.focus_set()
        dialog.bind("<Return>", lambda event: apply_size())
        dialog.bind("<Escape>", lambda event: dialog.destroy())

    def report_callback_exception(self, exc, value, traceback):
        """Обрабатывает ошибки в обработчиках событий Tkinter."""
        messagebox.showerror(
            "Ошибка",
            f"Не удалось выполнить действие:\n{value}\n\n"
            "Можно продолжить работу или нажать F2.",
            parent=self
        )


