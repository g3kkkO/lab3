import random


class Board:
    """Хранит игровое поле и реализует правила Сапёра."""

    def __init__(self, rows=9, cols=9, mines=10):
      
        self.rows = rows
        self.cols = cols
        self.mine_count = mines

        self.rng = random.Random(42)

        self.mines = set()
        self.opened = set()
        self.flags = set()

        self.started = False
        self.state = "playing"

    def neighbors(self, r, c):
        """Выдаёт координаты соседей клетки в пределах поля."""
        for nr in range(max(0, r - 1), min(self.rows, r + 2)):
            for nc in range(max(0, c - 1), min(self.cols, c + 2)):
                if (nr, nc) != (r, c):
                    yield nr, nc

    def number(self, r, c):
        """Возвращает количество мин вокруг клетки."""
        return sum(
            neighbor in self.mines
            for neighbor in self.neighbors(r, c)
        )

    def toggle_flag(self, r, c):
        """Ставит или снимает флаг."""
        if self.state != "playing" or (r, c) in self.opened:
            return

        if (r, c) in self.flags:
            self.flags.remove((r, c))
        elif len(self.flags) < self.mine_count:
            self.flags.add((r, c))


    def reveal(self, r, c):
        """Открывает клетку и проверяет результат игры."""
        if (
            self.state != "playing"
            or (r, c) in self.flags
            or (r, c) in self.opened
        ):
            return


        if not self.started:
            safe = {(r, c)}
            safe.update(self.neighbors(r, c))

            candidates = []

            for row in range(self.rows):
                for col in range(self.cols):
                    if (row, col) not in safe:
                        candidates.append((row, col))

            self.mines = set(
                self.rng.sample(candidates, self.mine_count)
            )
            self.started = True

  
        if (r, c) in self.mines:
            self.opened.add((r, c))
            self.state = "lost"
            return

        stack = [(r, c)]

        while stack:
            cell = stack.pop()

            if cell in self.opened or cell in self.flags:
                continue

            self.opened.add(cell)

            if self.number(*cell) == 0:
                for neighbor in self.neighbors(*cell):
                    if neighbor not in self.opened:
                        stack.append(neighbor)
                        
                        
                        
        safe_cells_count = self.rows * self.cols - self.mine_count

        if len(self.opened) == safe_cells_count:
            self.state = "won"