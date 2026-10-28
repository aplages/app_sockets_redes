import socket
import threading
import json

user = str(input("Nome de usuário:\t"))

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      # define o cliente como (IPv4, TCP)
try:
    client.connect(("localhost", 55555))                            # conecta o cliente ao servidor
except:
    print('ERRO: Não foi possível conectar ao servidor.\nVerifique se o servidor está em execução e se o uso do endereço e das portas foi feito de maneira correta.')
    exit(1)

lista_local = []
em_grupo = False
convite = None

def trata_msg(lista):

    for jinfo in lista:
        jinfo = json.loads(jinfo)
        acao = jinfo["acao"]

        if acao == "GROUP_MSG":
            print(f'[GRUPO] - {jinfo["origem"]}: {jinfo["mensagem"]}')

        elif acao == "DIRECT":
            origem = jinfo["origem"]
            if origem != user:
                print(f'W - De <{origem}>: {jinfo["mensagem"]}')
            else:
                print(f'W - Para <{jinfo["destino"]}>: {jinfo["mensagem"]}')

        elif acao == "BROADCAST":
            print(f'Geral - {jinfo["origem"]}: {jinfo["mensagem"]}')

        elif acao == "INVITE":
            global convite
            convite = jinfo["convidante"]   # define o remetente do convite recebido, para ser usado na função de aceite
            print(f'Você recebeu um convite para grupo de {convite}. Use /accept para aceitar')

        elif acao == "SERVER":
            print(f'{jinfo["mensagem"]}')
            if "se juntou ao grupo." in jinfo["mensagem"]:  # gambiarra extrema
                global em_grupo
                em_grupo = True

        elif acao == 'USERS_LIST':
            global lista_local
            lista_local = jinfo['users']

        else:
            print("Erro, nenhuma acao encontrada em trata_msg")

    return


def send():
    """
    Escreve uma mensagem e envia ao servidor.
    """
    #print('send(thread) iniciada.')

    print('-======= Bem-vindo ao Chat =======-')
    print("Comandos: /s (Dizer), /p (Grupo), /w <jogador> (Sussurro), /inv <jogador>, /online (Ver os usuários online)")
    print("Digite '/sair' para encerrar.\n")
    global user, em_grupo

    client.sendall((json.dumps({"acao": "USER_LIST","origem": user})+'\n').encode())
    
    
    canal_atual = '/s'
    alvo_atual = '' 
    
    while True:
        # Recebe input e formata
        if canal_atual == '/w':
            prefixo = f'[{alvo_atual}]: '
        elif canal_atual == '/s':
            prefixo = f'[Geral]: '
        else:
            prefixo = f'[Grupo]: '
    
        entrada = str(input(prefixo)).strip()
    
        if not entrada: # Se a entrada for vazia, vai pro inicio do loop
            continue
    
        if entrada[0] == '/':
            partes = entrada.split(' ', 1) # Divite a entrada no primeiro espaço
    
            comando = partes[0].lower()
    
            if comando in ['/s', '/p']: # Usuario digitou /s ou /p no inicio
                if comando == '/p' and not em_grupo:
                    print('ERRO: Você não está em nenhum grupo.')
                    continue #Caso o usuario tente mandar msg de grupo e nao esteja em nenhum grupo
                canal_atual = comando
                if len(partes) > 1: # Testa se o usuario digitou algo após o comando
                    mensagem = partes[1]
                else:
                    continue    # digitou apenas o comando. Troca o canal e volta pro inicio do loop
    
            elif comando == '/w':
                if len(partes) > 1: # Testa se o usuario digitou um destinatario
                    sussurro_partes = partes[1].split(' ', 1)
                    alvo_atual = sussurro_partes[0] # troca o destinatário do sussurro
                    if verifica_alvo(alvo_atual):
                        canal_atual = '/w'
                    else:
                        continue
                    if len(sussurro_partes) > 1: # testa se o usuario digitou uma mensagem após o comando
                        mensagem = sussurro_partes[1]
                    else:
                        continue    # digitou apenas o comando e um destino. troca o destino do sussurro e inicia o loop
                else:   # Digitou apenas /w sem um destino. Uso incorreto.
                    print('ERRO: Utilize a formatação: /w <destino> [mensagem]')
                    continue
            elif comando in ['/invite', '/convidar', '/inv']: # convidou alguem pra um grupo
                if len(partes) > 1: # testa se o usuario digitou um fulano pra convidar
                    invite_partes = partes[1].split(' ', 1)
                    alvo = invite_partes[0]
                    if verifica_alvo(alvo):
                        if len(invite_partes) > 1: # testa se o user digitou algo alem do alvo
                            print('Uso incorreto. Tente /invite <fulano>')
                        elif alvo == user:
                            print('Uso incorreto, você não pode convidar a si mesmo. Tente /invite <fulano>')
                        else:
                            invite(alvo)
                            #send_i = threading.Thread(target=invite, args=(alvo,))
                            #send_i.start()
                    else:
                        print('O alvo não está online.')
                else:
                    print('Uso incorreto. Tente /invite <fulano>')
                continue

            elif comando in ['/accept', '/aceitar']:    # aceita o convite pra grupo; **ignora qualquer coisa depois(?)
                if em_grupo:
                    print("Você já está em um grupo.")
                elif not convite:
                    print("Não há nenhum convite.")
                else:
                    accept_inv()
                    #send_acc = threading.Thread(target=accept_inv, args=())
                    #send_acc.start()
                continue    # volta o loop

            elif comando in ['/leavep', '/leaveg', '/lp', '/lg', ]:    # sai do grupo; **ignora qualquer coisa depois(?)
                            leave_group()
                            #send_lp = threading.Thread(target=leave_group, args=())
                            #send_lp.start()
                            canal_atual = '/s'
                            continue    # volta o loop

            elif comando == '/sair':
                print('Saindo...')
                break

            elif comando == '/online':
                print(f'Os usuários online no momento são: {lista_local}\n')
                continue

            elif comando == '/help':

                help_msg = '\nComandos disponíveis:\n' \
                '/help - Ajuda - mostra essa página.\n'\
                '/s - Fala no chat geral.\n' \
                '/p - Fala no chat do grupo.\n' \
                '/w <alvo> - Manda uma mensagem direta à um alvo\n' \
                '/invite, /inv, /convidar - Convida um alvo para seu grupo.\n' \
                '/accept, /aceitar - Aceita um convite de grupo pendente.\n' \
                '/leavep, /leaveg, /lp, /lg - Sai do grupo atual.\n' \
                '/sair - Sai do servidor.\n' \
                '/online - Mostra os usuários atualmente online.\n' \
                '=)\n'

                print(help_msg)
                continue
            else:   # Usou / mas nao usou nenhum comando
                print(f'ERRO: Comando desconhecido.')
                continue
    
        else:   # Não é um comando, então é uma mensagem no canal atual
            mensagem = entrada
    
        # Exibe no terminal
        if canal_atual == '/s':
            #print(f'[Geral] {user}: {mensagem}')
            broadcast_message(mensagem)
            #send_t = threading.Thread(target=broadcast_message, args=(mensagem,))
            #send_t.start()

        elif canal_atual == '/p':
            #print(f'[Grupo] {user}: {mensagem}')
            group_message(mensagem)
            #send_t = threading.Thread(target=group_message, args=(mensagem,))
            #send_t.start()

        elif canal_atual == '/w':
            #print(f'Para <{alvo_atual}>: {mensagem}')
            direct_message(alvo_atual, mensagem)
            #send_t = threading.Thread(target=direct_message, args=(alvo_atual, mensagem))
            #send_t.start()


    client.sendall((json.dumps(
        {
            "acao": "LEAVE_SERVER",
            "origem": user
        }
    )+'\n').encode())
    client.close()

    print('Saiu da conversa.')

def receive():
    """
    Recebe mensagens do servidor.
    """
    print('receive() thread iniciada. Recebendo mensagens do servidor...\n.\n.\n.')
    while True:
        try:
            server_com = client.recv(1024).decode()

            server_com = server_com.strip().split('\n')

            for j in server_com:
                j = json.loads(j)
            
            trata_msg(server_com)   # trata a mensagem - NAO APAGA ESSA LINHA
            
            #server_com = json.loads(server_com)     

            #print(f"receive():\t{server_com}")

            #printer_thread = threading.Thread(target=trata_msg, args=(server_com,))
            #printer_thread.start()

            
            
        except:
            print('Conexão encerrada.')
            client.close()
            break

def verifica_alvo(alvo : str):
    global lista_local, user
    if alvo == user:
        print('ERRO: Você não pode mandar uma DM para si mesmo.')
        return False
    if alvo not in lista_local:
        print(f'ERRO: O usuário mencionado {alvo} não foi encontrado ou está offline')
        return False
    return True

def invite(destino, origem=user):
    global em_grupo
    grupo = {
            "acao": "INVITE",
            "convidante": origem,
            "convidado": destino
            }
    client.sendall(f'{json.dumps(grupo)}\n'.encode())

    return

def leave_group(origem=user):
    global em_grupo
    info = {
        "acao": "LEAVE_GROUP",
        "origem": origem
    }
    em_grupo = False

    client.sendall(f'{json.dumps(info)}\n'.encode())

    return


def accept_inv(origem=user):    # REFAZER
    global convite, em_grupo  # str que informa o nome do usuario do ultimo convite recebido

    info = {
        "acao": "ACCEPT",
        "convidante": convite,
        "convidado": origem
    }

    client.sendall(f'{json.dumps(info)}\n'.encode())
    convite = None # limpa os convites
    #em_grupo = True
    return

def direct_message(destino, mensagem, origem=user):
    info = {
        "acao": 'DIRECT',
        "origem": origem,
        "destino": destino,
        "mensagem": mensagem
    }
    
    client.sendall((json.dumps(info)+'\n').encode())

    # CRIAR ERRO PARA USUARIO NAO ENCONTRADO:
    # Print('Erro, usuário não encontrado.')

    return

def group_message(mensagem, origem=user):
    info = {
        "acao": 'GROUP_MSG',
        "origem": origem,
        "mensagem": mensagem
    }
    
    client.sendall(f'{json.dumps(info)}\n'.encode())

    # CRIAR ERRO PARA GRUPO NAO ENCONTRADO:
    # Print('Erro, você não está em um grupo.')

    return

def broadcast_message(mensagem, origem = user):
    info = {"acao": "BROADCAST",
            "origem": origem,
            "mensagem": mensagem}
    client.sendall(f'{json.dumps(info)}\n'.encode())

conecta = False

while not conecta:
    server_com = client.recv(1024).decode()
    
    if not server_com:
        print('ERRO: Conexão recusada ou encerrada pelo servidor (provavelmente usuário já está em uso)')
        client.close()
        exit(1)
    #print(f"START: {server_com}")

    server_com = server_com.strip().split('\n')
    #print(server_com)
    for i in server_com:
        #print('START:'+i)
        if i == 'USER':
            #print('user?')
            client.sendall((user+'\n').encode())   # ENVIA O NOME DE USUARIO
            #print('user enviado')
    
            #server_com = client.recv(1024).decode().strip().split('\n') # recebe resposta do server
            #print('recbv')

        elif i == 'OK':  # servidor respoondeu OK?
            print("Autenticado com sucesso.\n") # ok
            conecta = True  # quebra o loop while

receive_thread = threading.Thread(target=receive)
send_thread = threading.Thread(target=send)

receive_thread.start()  # INICIA O PROGRAMA DE RECEBIMENTO
send_thread.start() # INICIA O PROGRAMA DE ENVIO