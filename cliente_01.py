import socket
import threading
import json

nickname = input("Escolha seu nick (apelido):   ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      # define o cliente como (IPv4, TCP)
client.connect(("127.0.0.1", 55555))                            # conecta o cliente ao servidor

def direct_message(user_dest, message):
    info = {"dest": str(user_dest),
            "mensagem": str(message)}

    json_info = json.dumps(info)
    pass

def group_message(group, message):
    info = {"dest": str(group),
                "mensagem": str(message)}
    
    json_info = json.dumps(info)
    pass

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

def send():
    """
    Escreve uma mensagem e envia ao servidor.
    """
    while True:
        message = f'{nickname}: {input(">>  ")}'
        client.send(message.encode())

receive_thread = threading.Thread(target=receive)

send_thread = threading.Thread(target=send)

receive_thread.start()
send_thread.start()