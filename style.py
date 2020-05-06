# language

def style():
    def fn_gen() -> object:
        # function generator; -> is a type hint
        for i in range(20):
            yield i

    def f_usegen(*args):
        # local function
        print(args)
        
    matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    filtered = [[x for x in row if x % 3 == 0]
                for row in matrix]
    print(filtered)

    # generator
    try:
        vg = (x % 2 for x in range(1000) if x % 99 == 1)
        # print(vg)
        while True:
            v = next(vg)
            if v is not None:
                print(v)
            else:
                break
    except StopIteration:
        print('\n')

    # zip
    g1 = (x for x in range(100))
    g2 = (y for y in range(200, 300))
    for j, k in zip(g1, g2):
        print(j / k)

    f = fn_gen()

    # f_usegen(*f) # needed to parse the arguments as variable number of arguments
    # if both this and the next run, it is exhausted

    for g in f:
        print(g)

    lcom = list(range(10, 100, 15))
    zcom = [x*x for x in lcom if x > 50]
    print(zcom)


def cortn():
    """Co routine"""
    #can process when called by send
    
    while True:
        received = yield
        print(received)


def usecrtn() -> object:
    #consumer

    it = cortn()
    next(it)
    it.send(1)
    it.send(2)


usecrtn()
# style()
