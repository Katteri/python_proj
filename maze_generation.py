from random import choice

# функция, возвращающая массив со стенами и промежутками
def get_map_cell(columns, rows):
    # класс ячейки, тут храним координаты ячейки, стены и инфу о посещении ячейки
    class Cell:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
            self.visited = False

        # функция для получения индекса ячейки по координатам
        def check_cell(self, x, y):
            # проверяем существование
            if x < 0 or x > columns - 1 or y < 0 or y > rows - 1:
                return False
            return grid_cell[x + y * columns]

        # функция, возвращающая случайного непосещенного соседа
        def check_neighbours(self):
            neighbours = []

            top = self.check_cell(self.x, self.y - 1)
            right = self.check_cell(self.x + 1, self.y)
            bottom = self.check_cell(self.x, self.y + 1)
            left = self.check_cell(self.x - 1, self.y)

            if top and not top.visited:
                neighbours.append(top)
            if right and not right.visited:
                neighbours.append(right)
            if bottom and not bottom.visited:
                neighbours.append(bottom)
            if left and not left.visited:
                neighbours.append(left)

            return choice(neighbours) if neighbours else False

    # функция, удаляющая стены между текущей и следующей ячейками
    def remove_walls(current_cell, next_cell):
        # находим разницу координат
        dx = current_cell.x - next_cell.x
        dy = current_cell.y - next_cell.y

        # определяем какие стены нужно удалить
        if dx == 1:
            current_cell.walls['left'] = False
            next_cell.walls['right'] = False
        if dx == -1:
            current_cell.walls['right'] = False
            next_cell.walls['left'] = False
        if dy == 1:
            current_cell.walls['top'] = False
            next_cell.walls['bottom'] = False
        if dy == -1:
            current_cell.walls['bottom'] = False
            next_cell.walls['top'] = False

    # функция, проверяющая есть ли на данном месте стена
    def check_wall(grid_cell, x, y):
        # ячейки, координаты которых четные, не являются стенами
        if x % 2 == 0 and y % 2 == 0:
            return False
        # нечетные координаты = стены
        if x % 2 == 1 and y % 2 == 1:
            return True

        # если x четный, а y - нет, то смотрим на клетку выше
        if x % 2 == 0:
            grid_x = x // 2
            grid_y = (y - 1) // 2
            return grid_cell[grid_x + grid_y * columns].walls['bottom']
        # иначе смотрим на клетку левее
        else:
            grid_x = (x - 1) // 2
            grid_y = y // 2
            return grid_cell[grid_x + grid_y * columns].walls['right']

    # создадим сетку
    grid_cell = [Cell(x, y) for y in range(rows) for x in range(columns)]
    # текущая ячейка
    current_cell = grid_cell[0]
    current_cell.visited = True
    # когда дойдем до тупика, нужно вернуться
    stack = []

    while True:
        next_cell = current_cell.check_neighbours()
        if next_cell:
            next_cell.visited = True
            remove_walls(current_cell, next_cell)
            current_cell = next_cell
            stack.append(current_cell)
        elif stack:
            current_cell = stack.pop()
        else:
            break

    return [check_wall(grid_cell, x, y) for y in range(rows * 2 - 1) for x in range(columns * 2 - 1)]