from collections import deque
from random import randint


def count_neighboring_mines(x0, y0, width, height, mines):
    count = 0
    for x in range(max(x0 - 1, 0), min(x0 + 2, width)):
        for y in range(max(y0 - 1, 0), min(y0 + 2, height)):
            if mines[y][x]:
                count += 1
    return count


def display_grid(width, height, grid, overlay, overlay_char='🚩'):
    print('  \\ x' + ''.join(f'{x + 1:>2}' for x in range(width)))
    print(' y \\╭' + '─' * (width * 2 + 1) + '╮')
    for y, (c_line, o_line) in enumerate(zip(grid, overlay)):
        print(
                f'{y + 1:>3}' +
            ' │ '
            + ''.join(
                overlay_char if f else ('. ' if c is None else f'{c} ')
                for c, f in zip(c_line, o_line)
            )
            + '│'
        )
    print('    ╰' + '─' * (width * 2 + 1) + '╯')


def minesweeper(width, height, mines_count):
    # generated mines
    mines = [[False] * width for y in range(height)]
    # user flags
    flags = [[False] * width for y in range(height)]
    # numbers grid: None for uncovered, neighboring mine count otherwise
    grid = [[None] * width for y in range(height)]

    # there could be less mines than mines_count if the randomness picks the
    # same position twice, but at least it doesn't IndexError or timeout if
    # there are not enough available tiles
    # also the mines generation is incorrect since you shouldn't spawn on a mine
    for i in range(mines_count):
        mines[randint(0, height - 1)][randint(0, width - 1)] = True

    # initial display of the grid
    display_grid(width, height, grid, flags)

    # either 'running', 'lose' or 'win'
    state = 'running'
    while state == 'running':
        action = input('Enter action: f for flag, other for uncover: ')
        input_pos = input('Enter position as "x y", starts at 1: ')

        # no input verification because I am lazy
        is_flag = action.strip().lower() == 'f'
        x0, y0 = input_pos.split(' ')
        x0, y0 = int(x0) - 1, int(y0) - 1

        # flag
        if is_flag:
            flags[y0][x0] = not flags[y0][x0]
        # placement
        else:
            # lose condition
            if mines[y0][x0]:
                state = 'lose'
                break

            # floodfill
            q = deque()
            q.append((x0, y0))
            while q:
                x0, y0 = q.popleft()
                if grid[y0][x0] is not None:
                    continue

                count = count_neighboring_mines(x0, y0, width, height, mines)
                grid[y0][x0] = count
                if count:
                    continue

                for x in range(max(x0 - 1, 0), min(x0 + 2, width)):
                    for y in range(max(y0 - 1, 0), min(y0 + 2, height)):
                        q.append((x, y))

        # win condition
        uncovered_count = 0
        for line in grid:
            for elt in line:
                if elt is None:
                    uncovered_count += 1

        if uncovered_count <= mines_count:
            state = 'win'
            break

        # display the grid
        display_grid(width, height, grid, flags)

    print('Game Over! You', state)

    display_grid(width, height, grid, mines, '💣')
