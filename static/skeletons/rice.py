import sys

def evaluate(board):
    #TODO
    pass

    
def main():
    """Accepts input from standard input and writes result to standard
    output.

    The first two lines of input will be single numbers that define
    the number of rows and columns. Each subsequent line will
    represent one row of the chessboard, with the number of grains of
    rice in each cell separated by spaces.

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

    board = []
    for nrow in xrange(nrows):
        line = sys.stdin.readline()
        row = [int(cell) for cell in line.strip().split()[:ncols]]
        board.append(row)

    print(evaluate(board))

    
if __name__=='__main__':
    main()

