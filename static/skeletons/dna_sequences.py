import sys

def evaluate(sequences):
    #TODO
    pass


def main():
    """Read DNA sequences from standard in, one per line.

    Write to standard out the longest subsequence that any two
    sequences have in common.

    """
    sequences = [line.strip() for line in sys.stdin.readlines()]
    print(evaluate(sequences))


if __name__=='__main__':
    main()
