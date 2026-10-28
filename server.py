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
    #print('entrou na funcao broadcast')

    #cliente_origem = message['origem']
    message = f'{json.dumps(message)}\n'
    #print(message, type(message))
    copia = sockets.copy()
    for c in copia.values():
        #print('entrou no loop de broadcast')
        #if c != copia[cliente_origem]:
        try:
            c.sendall(message.encode())
        except:
            print(f'User/Cliente {c} não recebeu os dados.')

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
                grupos.remove(grupo)   # remove o grupo
        else:
            server_msg(f"[GRUPO]: {username} saiu do grupo", list(grupo.keys()))
        print(grupo.keys())
    else:
        print('Grupo nao existe')
        mensagem = 'ERRO: Você não está em nenhum grupo.'
        server_msg(mensagem,[username])
        return # User nao está em um grupo
    return

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


    if not username_convidado in sockets: #verifica se o user a ser convidado existe no dict de sockets
        mensagem = 'ERRO: O usuário que está sendo convidado não existe ou não está online.'
        #print(mensagem)
        server_msg(mensagem, [username_convidante])
        return
    
    client_convidado: socket.socket = sockets[username_convidado]
    if find_group(username_convidado):
        mensagem = 'ERRO: O usuário convidado já está em um grupo.'
        server_msg(mensagem, [username_convidante])
        return # Erro, alvo já está em um grupo (O alvo não pode estar em mais de um grupo?)

    group = find_group(username_convidante)
    if not group:
        create_group(username_convidante)
        group = find_group(username_convidante)
    
    #print(client_convidado)
    #print(jinfo)
    client_convidado.sendall(f'{json.dumps(jinfo)}\n'.encode())
    server_msg("Convite enviado", [username_convidante])
    return


def broadcast_group(jinfo:dict):
    user_origem = jinfo['origem']
    grupo = find_group(user_origem)
    
    if not grupo:
        print(f'Usuário não está em nenhum grupo')
        mensagem = 'ERRO: Você não está em um grupo.'
        server_msg(mensagem, [user_origem])
        return
    
    message = f'{json.dumps(jinfo)}\n'.encode()
    for c in list(grupo.keys()):  #uma cópia para evitar o erro de caso o dicionario de membros mudar (um convite aceitou ou um membro saiu) e mudar o tamanho do grupo enquanto uma mensagem é enviada.
        #if c != user_origem:
        socket_membro = grupo[c]
        try:
            socket_membro.sendall(message)
        except:
            print(f"ERRO: Cliente {c} não recebeu a mensagem. Socket: {grupo[c]}")
    return

def accept_inv(jinfo: dict):
    convidante = jinfo["convidante"]
    convidado = jinfo["convidado"]

    grupo: dict | None = find_group(convidante)

    if grupo:
        #print('grupo(convidante) = True')
        grupo[convidado] = sockets[convidado]
        #print(grupo)
        mensagem = f'[GRUPO]: {convidado} se juntou ao grupo.'
        #print(grupo.keys())
        server_msg(mensagem, grupo.keys())
    else:
        #print('gr(convidante) = false')
        mensagem = 'ERRO: Grupo não encontrado'
        print(mensagem)
        server_msg(mensagem,[convidado])

    return


def server_msg(msg: str, users_list: list):
    
    data = f'{json.dumps(
        {
        "acao": "SERVER",
        "mensagem": msg
    }
    )}\n'
    
    if not users_list:
        pass

    for u in users_list:
        try:
            sockets[u].sendall(data.encode())
        except:
            pass
    

def direct_message(jinfo: dict):
    
    user_origem = jinfo["origem"]
    client_orig: socket.socket = sockets[user_origem]


    user_dest = jinfo["destino"]

    if user_dest in sockets.keys():
        client_dest: socket.socket = sockets[user_dest]
        #print(user_dest)
        #print(client_dest)
        try:
            client_dest.sendall(f'{json.dumps(jinfo)}\n'.encode())
            client_orig.sendall(f'{json.dumps(jinfo)}\n'.encode())
        except:
            print("Cliente não recebeu a mensagem")
    else:
        print('Cliente nao existe')
        mensagem = 'ERRO: O cliente que você está tentando enviar mensagem não existe.'
        server_msg(mensagem,[user_origem])
        return

    return


def receive():
    """
    Lida com as conexões dos diferentes clientes e cria uma thread pra cada
    """
    print("Servidor iniciado.")
    while True:
        client, address = server.accept()                       # Recebe o socket e o IP do cleinte (a função retorna uma tupla)
        print(f'Conexão estabelecida com {address}\n')

        client.sendall("Conexão estabelecida com o servidor\n".encode())


        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

def broadcast_user():
    lista = list(sockets.keys())

    mensagem = f'{json.dumps(
        {'acao': 'USERS_LIST',
        'users': lista}
                )}\n'
    for s in list(sockets.values()):
        try:
            s.sendall(mensagem.encode())
        except:
            print(f'Cliene {s} não recebeu a lista de usuários.')


def handle_client(client: socket.socket):
    """
    Vai lidar com o recebimento de mensagens de diferentes clientes e suas threads
    """
    client.send('USER\n'.encode())
    username = client.recv(1024).decode().strip().split('\n')[0]
    
    if username in sockets.keys():
        client.close() #Trata caso o username já exista.
        return

    sockets[username] = client
    client.send("OK\n".encode())
    #print('enviado OK')
    #broadcast_user()


    print(f'Conexão estabelecida com {client}-{username}.\n\nUsuários ativos atualmente:\n{sockets}\n')


    conectado = True
    while conectado: # Inicia recebimento de JSONs
        try:
            data = client.recv(1024).decode().strip().split('\n')    # recebe msg do cliente

            for message in data:
                try:
                    message = json.loads(message) # tenta carregar json
                except json.JSONDecodeError:
                    server_msg('ERRO: Formato inválido ou pacotes foram corrompidos', [username])
                    # não eh um json
                    conectado = False
                    break
                print(f'-=-\n{message}\n-=-')

                acao = message["acao"]
                
                if acao == "DIRECT":
                    #dm = threading.Thread(target=direct_message, args=(message,))
                    #dm.start()

                    direct_message(message)
                
                elif acao == 'BROADCAST':
                    broadcast(message)

                    #bd = threading.Thread(target=broadcast, args = (message,))
                    #bd.start()
                
                elif acao == "INVITE":
                    invite(message)

                    #inv_thread = threading.Thread(target=invite, args=(message,))
                    #inv_thread.start()
                
                elif acao == "ACCEPT":
                    accept_inv(message)

                    #acc_thread = threading.Thread(target=accept_inv, args=(message,))
                    #acc_thread.start()
                
                elif acao == "GROUP_MSG":   # deve chamar a funcao de broad cast de grupos
                    broadcast_group(message)

                    #pr = threading.Thread(target=broadcast_group, args=(message,))    # essa funcao só printa os grupos (testagem)
                    #pr.start()
                
                elif acao == "LEAVE_GROUP":  # deve chamar a funcao de sair do grupo
                    leave_group(message)
                    
                    #lp = threading.Thread(target=leave_group, args=(message,))
                    #lp.start()

                elif acao == "USER_LIST": # deve enviar a lista de usuarios
                    broadcast_user()

                    #ul = threading.Thread(target=broadcast_user, args=())
                    #ul.start()

                elif acao == "LEAVE_SERVER":
                    conectado = False

        except :
            conectado = False


    grupo: dict | None = find_group(username)
    if grupo:
        grupo.pop(username)
        if len(grupo) == 0:
            grupos.remove(grupo)
        else:
            server_msg(f"[GRUPO]: {username} saiu do grupo", list(grupo.keys()))
    
    sockets.pop(username)
    broadcast_user()
    client.close() # Fecha conexão com cliente


    print(f'cliente {username} removido.')
    print(sockets)


receive()