import socket
import threading
import json

host = '0.0.0.0'
# 0.0.0.0
host = '0.0.0.0'
port = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      # Inicia um servidor, configurado para (IPv4, TCP)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)    # LIBERA A PORTA DO SERVIDOR PRA SER REUTILIZADA NA MESMA HORA
server.bind((host, port))                                       # Aloca o servidor no IP-host e na PORTA-port
server.listen()                                                 # Começa a aceitar conexões

sockets = {}

grupos_dict = {} #Nome do grupo + um array com os participantes do grupo 

grupos = [] # lista dos grupos ativos [{user: socket, user: socket, user: socket}, {user: socket, user: socket}]


def printa_grupos():
    global grupos
    for g in grupos:
        print(g.keys())

    return

def broadcast(message):
    """
    Envia uma mensagem a todos os clientes ativos.
    """
    print('entrou na funcao broadcast')

    cliente_origem = message['origem']
    message = json.dumps(message)
    #print(message, type(message))
    for c in sockets.values():
        #print('entrou no loop de broadcast')
        if c != sockets[cliente_origem]:
            c.sendall(message.encode())

"""
def create_groupANTIGO(jinfo: dict):
    user = jinfo["origem"]
    client = sockets[user]

    grupo = {user:client}
    

    grupos.append(grupo)

    return
"""

def leave_group(jinfo):
    username = jinfo["origem"]

    grupo: dict | None = find_group(username)
    if grupo:
        grupo.pop(username)
        if len(grupo) == 0:
                grupos.remove(grupo)
        print(grupo.keys())
    else:
        print('grupo nao existe')
        pass # envia um erro?
    return # User nao está em um grupo

def create_group(username):
    client = sockets[username]
    grupo = {username: client}

    grupos.append(grupo)

    return grupo


def is_active(user):
    if user in sockets.keys():
        return True
    
    return False

def find_group(user):
    for g in grupos:
        if user in g.keys():
            return g

    return None

def invite(jinfo: dict):
    username_convidante = jinfo["convidante"]
    username_convidado = jinfo["convidado"]

    if find_group(username_convidado):
        return # Erro, alvo já está em um grupo (O alvo não pode estar em mais de um grupo?)

    group = find_group(username_convidante)
    if not group:
        create_group(username_convidante)
        group = find_group(username_convidante)
    if sockets[username_convidado]: #verifica se o user a ser convidado existe no dict de sockets
        client_convidado: socket.socket = sockets[username_convidado]
    else:
        pass #Vai retornar um erro
    #print(client_convidado)
    #print(jinfo)
    client_convidado.sendall(json.dumps(jinfo).encode())
    return


def broadcast_group(jinfo:dict):
    user_origem = jinfo['origem']
    grupo = find_group(user_origem)
    if not grupo:
        print(f'Usuário não está em nenhum grupo')
        return


    message = json.dumps(jinfo).encode()

    for c in jinfo['grupo']:
        if c != grupos_dict[user_origem]:
            grupos_dict[c].sendall(message)
    pass

def accept_inv(jinfo: dict):
    convidante = jinfo["convidante"]
    convidado = jinfo["convidado"]

    grupo: dict | None = find_group(convidante)

    if grupo:
        grupo[convidado] = sockets[convidado]
    else:
        pass    # erro, grupo nao encontrado.


def direct_message(jinfo: dict):
    
    user_origem = jinfo["origem"]
    client_orig: socket.socket = sockets[user_origem]


    user_dest = jinfo["destino"]

    if user_dest in sockets.keys():
        client_dest: socket.socket = sockets[user_dest]
        #print(user_dest)
        #print(client_dest)

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


    sockets[username] = client

    client.send("OK".encode())

    print(f'Conexão estabelecida com {client}-{username}. Usuários ativos atualmente:\n{sockets}')
    while True: # Inicia recebimento de JSONs
        try:
            message = json.loads(client.recv(1024).decode()) #lages doente FAZ DECODE DAS MENSAGENS PELO AMOR DE DEUS 
            print(f'-=-\n{message}\n-=-')

            acao = message["acao"]
            
            if acao == "DIRECT":
                dm = threading.Thread(target=direct_message, args=(message,))
                dm.start()
            
            elif acao == 'BROADCAST':
                bd = threading.Thread(target=broadcast, args = (message,))
                bd.start()
            
            elif acao == "INVITE":
                inv_thread = threading.Thread(target=invite, args=(message,))
                inv_thread.start()
            
            elif acao == "ACCEPT":
                acc_thread = threading.Thread(target=accept_inv, args=(message,))
                acc_thread.start()
            
            elif acao == "GROUP_MSG":   # deve chamar a funcao de broad cast de grupos
                pr = threading.Thread(target=broadcast_group, args=(message,))    # essa funcao só printa os grupos (testagem)
                pr.start()
            
            elif acao == "LEAVE_GROUP":  # deve chamar a funcao de sair do grupo
                lp = threading.Thread(target=leave_group, args=(message,))
                lp.start()

        except:
            break


    grupo: dict | None = find_group(username)
    if grupo:
        grupo.pop(username)
    
    sockets.pop(username)
    
    client.close() # Fecha conexão com cliente


    print(f'cliente {username} removido.')
    print(sockets)


receive()