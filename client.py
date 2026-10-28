import socket
import threading
import json
import sys

lista_local = []
em_grupo = False
convite = None
user = ""
client = None

def print_msg(lista):
    global convite, em_grupo, lista_local
    for jinfo in lista:
        if not jinfo.strip():
            continue
        try:
            jinfo = json.loads(jinfo)
        except json.JSONDecodeError:
            continue
        acao = jinfo.get("acao")

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
            convite = jinfo["convidante"]   # define o remetente do convite recebido, para ser usado na função de aceite
            print(f'Você recebeu um convite para grupo de {convite}. Use /accept para aceitar')

        elif acao == "SERVER":
            print(f'{jinfo["mensagem"]}')
            if "se juntou ao grupo." in jinfo["mensagem"]:  # gambiarra extrema
                em_grupo = True

        elif acao == 'USERS_LIST':
            lista_local = jinfo['users']

        else:
            print("Erro, nenhuma acao encontrada em print_msg")

    return


def send():
    """
    Escreve uma mensagem e envia ao servidor.
    """
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
    
        try:
            entrada = str(input(prefixo)).strip()
        except (EOFError, KeyboardInterrupt):
            break
    
        if not entrada: # Se a entrada for vazia, vai pro inicio do loop
            continue
    
        if entrada[0] == '/':
            partes = entrada.split(' ', 1) # Divide a entrada no primeiro espaço
            comando = partes[0].lower()
    
            if comando in ['/s', '/p']: # Usuario digitou /s ou /p no inicio
                if comando == '/p' and not em_grupo:
                    print('ERRO: Você não está em nenhum grupo.')
                    continue # Caso o usuario tente mandar msg de grupo e nao esteja em nenhum grupo
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
                    else:
                        print('O alvo não está online.')
                else:
                    print('Uso incorreto. Tente /invite <fulano>')
                continue

            elif comando in ['/accept', '/aceitar']:    # aceita o convite pra grupo
                if em_grupo:
                    print("Você já está em um grupo.")
                elif not convite:
                    print("Não há nenhum convite.")
                else:
                    accept_inv()
                continue    # volta o loop

            elif comando in ['/leavep', '/leaveg', '/lp', '/lg']:    # sai do grupo
                leave_group()
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
    
        # Envia de acordo com o canal atual
        if canal_atual == '/s':
            broadcast_message(mensagem)
        elif canal_atual == '/p':
            group_message(mensagem)
        elif canal_atual == '/w':
            direct_message(alvo_atual, mensagem)

    try:
        client.sendall((json.dumps({
            "acao": "LEAVE_SERVER",
            "origem": user
        })+'\n').encode())
    except Exception:
        pass
    client.close()
    print('Saiu da conversa.')

def receive():
    """
    Recebe mensagens do servidor.
    """
    while True:
        try:
            server_com = client.recv(1024).decode()
            if not server_com:
                print('Conexão encerrada pelo servidor.')
                client.close()
                break

            server_com = server_com.strip().split('\n')
            print_msg(server_com)
        except Exception:
            print('Conexão encerrada.')
            client.close()
            break

def verifica_alvo(alvo: str):
    global lista_local, user
    if alvo == user:
        print('ERRO: Você não pode mandar uma DM para si mesmo.')
        return False
    if alvo not in lista_local:
        print(f'ERRO: O usuário mencionado {alvo} não foi encontrado ou está offline')
        return False
    return True

def invite(destino, origem=None):
    if origem is None:
        origem = user
    grupo = {
        "acao": "INVITE",
        "convidante": origem,
        "convidado": destino
    }
    client.sendall(f'{json.dumps(grupo)}\n'.encode())

def leave_group(origem=None):
    global em_grupo
    if origem is None:
        origem = user
    info = {
        "acao": "LEAVE_GROUP",
        "origem": origem
    }
    em_grupo = False
    client.sendall(f'{json.dumps(info)}\n'.encode())

def accept_inv(origem=None):
    global convite
    if origem is None:
        origem = user
    info = {
        "acao": "ACCEPT",
        "convidante": convite,
        "convidado": origem
    }
    client.sendall(f'{json.dumps(info)}\n'.encode())
    convite = None

def direct_message(destino, mensagem, origem=None):
    if origem is None:
        origem = user
    info = {
        "acao": 'DIRECT',
        "origem": origem,
        "destino": destino,
        "mensagem": mensagem
    }
    client.sendall((json.dumps(info)+'\n').encode())

def group_message(mensagem, origem=None):
    if origem is None:
        origem = user
    info = {
        "acao": 'GROUP_MSG',
        "origem": origem,
        "mensagem": mensagem
    }
    client.sendall(f'{json.dumps(info)}\n'.encode())

def broadcast_message(mensagem, origem=None):
    if origem is None:
        origem = user
    info = {
        "acao": "BROADCAST",
        "origem": origem,
        "mensagem": mensagem
    }
    client.sendall(f'{json.dumps(info)}\n'.encode())

def run_cli(host="localhost", port=55555):
    global user, client
    user = str(input("Nome de usuário:\t")).strip()
    if not user:
        print("Nome de usuário não pode ser vazio.")
        sys.exit(1)

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((host, port))
    except Exception:
        print('ERRO: Não foi possível conectar ao servidor.\nVerifique se o servidor está em execução e se o uso do endereço e das portas foi feito de maneira correta.')
        sys.exit(1)

    conecta = False
    while not conecta:
        server_com = client.recv(1024).decode()
        if not server_com:
            print('ERRO: Conexão recusada ou encerrada pelo servidor (provavelmente usuário já está em uso)')
            client.close()
            sys.exit(1)

        server_com = server_com.strip().split('\n')
        for i in server_com:
            i = i.strip()
            if i == 'USER':
                client.sendall((user+'\n').encode())
            elif i == 'OK':
                print("Autenticado com sucesso.\n")
                conecta = True

    receive_thread = threading.Thread(target=receive, daemon=True)
    receive_thread.start()
    send()

if __name__ == "__main__":
    if "--cli" in sys.argv or "--terminal" in sys.argv:
        run_cli()
    else:
        try:
            import tkinter as tk
            from client_gui import ChatClientGUI
            usuario_arg = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-') else None
            root = tk.Tk()
            app = ChatClientGUI(root, user=usuario_arg)
            root.mainloop()
        except Exception as e:
            # Caso não haja ambiente gráfico ou ocorra erro no Tkinter, cai para o modo terminal
            print(f"[Aviso] Interface gráfica não disponível ({e}). Iniciando modo terminal...")
            run_cli()
