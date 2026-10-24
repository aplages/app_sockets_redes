import socket
import threading
import json


host = '127.0.0.1'
port = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      # Inicia um servidor, configurado para (IPv4, TCP)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((host, port))                                       # Aloca o servidor no IP-host e na PORTA-port
server.listen()                                                 # Começa a aceitar conexões

clients = []                                                    # Lista dos clientes
users = []

def direct_message(jinfo):
    user_dest = jinfo["destino"]
    if user_dest in users:
        ind = users.index(user_dest)
        
        client_dest: socket.socket = clients[ind]
        print(user_dest)
        print(client_dest)

        client_dest.sendall(json.dumps(jinfo).encode())
    else:
        print('Cliente nao existe')

    return


def receive():
    """
    Lida com as conexões dos diferentes clientes e cria uma thread pra cada
    """
    print("Servidor iniciado.")
    while True:
        client, address = server.accept()                       # Recebe o socket e o IP do cleinte (a função retorna uma tupla)
        print(f'Conexão estabelecida com {address}')

        client.sendall("Conexão estabelecida com o servidor".encode())


        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()


def handle_client(client: socket.socket):
    """
    Vai lidar com o recebimento de mensagens de diferentes clientes e suas threads
    """
    client.sendall('USER'.encode())
    username = client.recv(1024).decode()

    clients.append(client)
    users.append(username)

    client.sendall("OK".encode())

    while True: # Inicia recebimento de JSONs
        try:
            message = json.loads(client.recv(1024).decode()) #lages doente FAZ DECODE DAS MENSAGENS PELO AMOR DE DEUS 
            print(f'-=-\n{message}\n-=-')


            if message["acao"] == "DIRECT":
                dm = threading.Thread(target=direct_message, args=(message,))
                dm.start()

            elif message["acao"] == "GROUP_MSG":
                pass

            #elif message["acao"] == 
        except:
            break


    client.close() # Fecha conexão com cliente

    clients.remove(client)  # remove cliente da lista de clientes
    users.remove(username)  # remove cliente da lista de users

    print(f'cliente {username} removido.')
    print(clients)
    print(users)


receive()