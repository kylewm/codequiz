import sys

def evaluate(grid):
    #TODO
    pass


def main():
    """Accepts input from standard input and writes result to standard
    output.

    The first two lines of input will be single numbers that define
    the number of rows and columns. Each subsequent line will
    represent one row of the grid, with the number of pennies at each
    tile separated by spaces.

    For example the input:

    4
    4
    2 2 4 2
    0 3 0 1
    1 2 2 1
    4 1 2 2

    Should print to standard output:

    15

    """
    nrows = int(sys.stdin.readline().strip())
    ncols = int(sys.stdin.readline().strip())

    grid = []
    for nrow in xrange(nrows):
        line = sys.stdin.readline()
        row = [int(cell) for cell in line.strip().split()[:ncols]]
        grid.append(row)

    print(evaluate(grid))


if __name__=='__main__':
    main()
