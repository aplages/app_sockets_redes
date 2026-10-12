import threading
import time


def t_write(n):
    file_name = str(n)
    for t in range(10):
        with open(f'threading_tests/file{file_name}.txt', 'a') as file:
            file.write(f'{n*t}\n')
            time.sleep(0.5)

def t_read(n):
    file_name = str(n)
    with open(f'threading_tests/file{file_name}.txt', 'r') as file:
        file.readline()
        for i in file.readlines():
            print(i)

def teste():
    for n in range(1, 4):
        thread = threading.Thread(target=t_write, args=(n,))
        thread.start()
    print(True)
    return      
    # Mesmo ao retornar a função que iniciou uma thread de outra função, a thread criada ainda funciona

def read_teste():
    for n in range(1, 4):
        thread = threading.Thread(target=t_read, args=(n,))
        thread.start()
    print(True)
    return      # Threads conseguem ler o mesmo arquivo. Ao mesmo tempo(?)


#teste()
read_teste()





