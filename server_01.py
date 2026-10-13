import socket
import threading
import json


host = '127.0.0.1'
port = 55555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      # Inicia um servidor, configurado para (IPv4, TCP)
server.bind((host, port))                                       # Aloca o servidor no IP-host e na PORTA-port
server.listen()                                                 # Começa a aceitar conexões

clients = []                                                    # Lista dos clientes

def broadcast(message):
    """
    Envia uma mensagem a todos os clientes.
    """
    for client in clients:
        try:
            client.send(message)                                # Envia tal mensagem ao cliente
        except:
            pass    # Desconectar o cliente*

def authenticator(client):
    """
    Autenticar diferentes clientes com password e usernames e criar caso não existam ainda
    """
    while True:
        client.send('Login or Register'.encode()) #Perguntar modo de autenticação

        modo = client.recv(1024).decode().strip().lower()
        print(modo)

        client.send('Username'.encode())

        username = client.recv(1024).decode().strip()

        client.send('Password'.encode())

        password = client.recv(1024).decode().strip()

        usuarios = {}
        with open('user-teste.txt', 'r') as f:
            for line in f:
                if ':' in line:
                    u, p = line.strip().split(':',1)
                    usuarios[u] = p #coloca os usuarios ja existentes dentro do dicionario 
        if modo == 'register':
            if username in usuarios: #caso o login já exista
                client.send('ERRO: Nome de usuário já existente'.encode()) 
            else:
                with open('user-teste.txt','a') as f:
                    f.write(f'{username}:{password}\n')
                client.send('Sucesso, criou a conta neguin'.encode())
        elif modo == 'login':
            if username in usuarios and usuarios[username] == password:
                client.send('é tu mesmo neguin pode passar'.encode())
                return username
            else:
                client.send('Erro, usuario ou senha tao errado kkkkk'.encode())
        else:
            client.send('Modo de autenticacao nao existente dog'.encode())
def handle_login(client):
    pass

def handle_client(client):
    """
    Vai lidar com o recebimento de mensagens de diferentes clientes e suas threads
    """
    while True:
        try:
            message = client.recv(1024)
            print(message.decode())     # TESTAGEM: mostra a mensagem do cliente no terminal do servidor
        except:
            client.close()
            break


def receive():
    """
    Lida com as conexões dos diferentes clientes e cria uma thread pra cada
    """
    print("Servidor iniciado.")
    while True:
        client, address = server.accept()                       # Recebe o socket e o IP do cleinte (a função retorna uma tupla)
        print(f'Conexão estabelecida com {address}')

        nickname = authenticator(client)

        if not nickname:
            client.close()
            continue 

        #client.send('NICK'.encode()) # recebe o NICK, futuramente receber login?
        #nickname = client.recv(1024).decode()
        clients.append(client)

        with open('users-names.txt', 'a') as file:
            file.write(f'{nickname}\n')
            file.close()
        
        
        print(f'Nick do cliente é: {nickname}')
        broadcast(f'{nickname} se juntou ao chat!'.encode())

        client.send("Conexão estabelecida com o servidor".encode())

        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()


receive()