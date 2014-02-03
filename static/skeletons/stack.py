import sys

def evaluate(inp):
    #TODO
    pass

    
def main():
    """Receives input on a single line from standard in. Computes and
    prints the result on a single line to standard out. For example,
    the input
    
    11+2*
    
    should yield the result:
    
    4

    """
    inp = sys.stdin.readline().strip()
    print(evaluate(inp))

    
if __name__=='__main__':
    main()

