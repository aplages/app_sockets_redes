import socket
import threading

nickname = input("Escolhe seu nick (apelido):   ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      # define o cliente como (IPv4, TCP)
client.connect(("127.0.0.1", 55555))                            # conecta o cliente ao servidor

def receive():
    """
    Recebe mensagens do servidor.
    """
    while True:
        try:
            message = client.recv(1024).decode()
            if message == 'NICK':
                client.send(nickname.encode())
            else:
                print(message)

        except:
            print('Erro!!')
            client.close()
            break

def write():
    """
    Escreve uma mensagem e envia ao servidor.
    """
    while True:
        message = f'{nickname}: {input(">>  ")}'
        client.send(message.encode())

receive_thread = threading.Thread(target=receive)

write_thread = threading.Thread(target=write)

receive_thread.start()
write_thread.start()