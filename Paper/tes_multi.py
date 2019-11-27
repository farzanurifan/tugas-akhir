from multiprocessing import Process

def loop_a():
    i = 10
    while i:
        print("a")
        i -= 1

def loop_b():
    i = 10
    while i:
        print("b")
        i -= 1

if __name__ == '__main__':
    Process(target=loop_a).start()
    Process(target=loop_b).start()