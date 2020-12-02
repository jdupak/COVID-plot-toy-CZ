class Coord:
    def __init__(self, a: int, b: int):
        self.a = a
        self.b = b

    def __add__(self, other):
        c = self.a + other.a
        d = self.b + other.b
        return Coord(c, d)

    def __mul__(self, other: int):
        c = self.a * other
        d = self.b * other
        return Coord(c, d)


def line_size(r: int, c: int, data: list) -> int:
    value = data[r][c]
    count = 1
    count += count_in_direction(value, Coord(r, c), Coord(0, 1), data)
    count += count_in_direction(value, Coord(r, c), Coord(0, -1), data)
    count += count_in_direction(value, Coord(r, c), Coord(1, 0), data)
    count += count_in_direction(value, Coord(r, c), Coord(-1, 0), data)
    return count

def count_in_direction(value: int, start: Coord, direction: Coord, data: list) -> int:
    counter = 0
    current = start + direction
    while True:
        if current.a < 0 or current.a >= len(data) or current.b < 0 or current.b >= len(data[0]):
            break
        if value != data[current.a][current.b]:
            break
        counter += 1
        current += direction
    return counter


if __name__ == '__main__':
    r = 5
    c = 5
    data = [
        [0, 1, 1, 1, 1, 0, 0, 0],
        [1, 1, 0, 1, 0, 1, 1, 1],
        [0, 1, 1, 0, 0, 1, 0, 1],
        [1, 1, 1, 0, 1, 1, 0, 1],
        [0, 1, 0, 0, 0, 0, 1, 1],
        [1, 0, 1, 1, 0, 0, 0, 0],
        [0, 1, 1, 1, 0, 1, 1, 1],
        [1, 1, 0, 1, 0, 1, 1, 1]]
    reg_size = line_size(r, c, data)
    print(reg_size)
