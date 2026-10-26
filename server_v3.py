import socket
import threading
import json

host = '0.0.0.0'
# 0.0.0.0
host = '127.0.0.1'
port = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      # Inicia um servidor, configurado para (IPv4, TCP)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)    # LIBERA A PORTA DO SERVIDOR PRA SER REUTILIZADA NA MESMA HORA
server.bind((host, port))                                       # Aloca o servidor no IP-host e na PORTA-port
server.listen()                                                 # Começa a aceitar conexões

clients = []                                                    # Lista dos clientes
users = [] #Vai virar um dicionario fdp

apendice = {}


grupos_dict = {} #Nome do grupo + um array com os participantes do grupo 

grupos = [] # lista dos grupos ativos [{user: socket, user: socket, user: socket}, {user: socket, user: socket}]

def broadcast(message):
    """
    Envia uma mensagem a todos os clientes ativos.
    """
    print('entrou na funcao broadcast')
    cliente_origem = message['origem']
    message = json.dumps(message)
    print(message, type(message))
    for c in apendice.values():
        print('entrou no loop de broadcast')
        c.sendall(message.encode())

def create_group(jinfo: dict):
    user = jinfo["origem"]
    client = apendice[user]

    grupo = {user:client}

    grupos.append(grupo)

    return

def create_group2(username):
    client = apendice[username]
    grupo = {username: client}

    grupos.append(grupo)

    return grupo


def is_active(user):
    if user in apendice.keys():
        return True
    
    return False

def find_group(user):
    for g in grupos:
        if user in g.keys():
            return g

    return None

def invite(jinfo: dict):
    user = jinfo["origem"]
    destino = jinfo["destino"]

    if find_group(destino):
        return # Erro, alvo já está em um grupo (O alvo não pode estar em mais de um grupo?)

    group = find_group(user)
    if not group:
        create_group2(user)
        group = find_group(user)
    else:
        client_destino = apendice[destino]
        pass # envia o convite ao cliente

    
    


def direct_message(jinfo: dict):
    
    user_origem = jinfo["origem"]
    client_orig: socket.socket = apendice[user_origem]


    user_dest = jinfo["destino"]

    if user_dest in apendice.keys():
        client_dest: socket.socket = apendice[user_dest]
        print(user_dest)
        print(client_dest)

        client_dest.sendall(json.dumps(jinfo).encode())
    else:
        print('Cliente nao existe')
        try:
            erro = {
                'acao': 'ERRO',
                'mensagem': 'Usuário não encontrado.'
            }
            client_orig.sendall(json.dumps(erro).encode())
        except:
            pass

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
    client.send('USER'.encode())
    username = client.recv(1024).decode()

    # clients.append(client)
    # users.append(username)

    apendice[username] = client

    client.send("OK".encode())

    print(f'Conexão estabelecida com {client}-{username}. Usuários ativos atualmente:\n{apendice}')
    while True: # Inicia recebimento de JSONs
        try:
            message = json.loads(client.recv(1024).decode()) #lages doente FAZ DECODE DAS MENSAGENS PELO AMOR DE DEUS 
            print(f'-=-\n{message}\n-=-')


            if message["acao"] == "DIRECT":
                dm = threading.Thread(target=direct_message, args=(message,))
                dm.start()

            elif message["acao"] == 'BROADCAST':
                bd = threading.Thread(target=broadcast, args = (message,))
                bd.start()
            elif message['acao'] == 'INVITE':
                iv = threading.Thread(target=invite, args=(message,))
                iv.start()
            elif message["acao"] == "GROUP_MSG":
                pass

            elif message["acao"] == "CREATE_GROUP":
                pass
            #elif message["acao"] == criar grupo
        except:
            break


    apendice.pop(username)
    
    client.close() # Fecha conexão com cliente

    # clients.remove(client)  # remove cliente da lista de clientes
    # users.remove(username)  # remove cliente da lista de users

    print(f'cliente {username} removido.')
    #print(clients)
    #print(users)
    print(apendice)


receive()