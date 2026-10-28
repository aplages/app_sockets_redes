import socket
import threading
import json
import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

class ChatClientGUI:
    def __init__(self, root, host="localhost", port=55555, user=None):
        self.root = root
        self.host = host
        self.port = port
        self.user = user

        self.client_socket = None
        self.conectado = False

        # Variáveis de estado do cliente (as mesmas do client.py)
        self.lista_local = []
        self.em_grupo = False
        self.convite = None
        self.canal_atual = '/s'
        self.alvo_atual = ''

        self.root.title("Chat RPG - Sockets TCP")
        self.root.geometry("800x550")
        self.root.minsize(650, 450)

        # Configurar protocolo de fechamento de janela
        self.root.protocol("WM_DELETE_WINDOW", self.ao_fechar)

        if not self.user:
            self.mostrar_tela_login()
        else:
            self.conectar_ao_servidor()

    # -------------------------------------------------------------
    # TELA DE LOGIN / CONEXÃO
    # -------------------------------------------------------------
    def mostrar_tela_login(self):
        self.login_frame = ttk.Frame(self.root, padding=30)
        self.login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        lbl_titulo = ttk.Label(self.login_frame, text="Chat RPG - Conexão", font=("Helvetica", 16, "bold"))
        lbl_titulo.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        ttk.Label(self.login_frame, text="Nome de usuário:", font=("Helvetica", 10)).grid(row=1, column=0, sticky=tk.W, pady=6)
        self.entry_user = ttk.Entry(self.login_frame, width=28, font=("Helvetica", 10))
        self.entry_user.grid(row=1, column=1, pady=6)
        self.entry_user.focus_set()

        ttk.Label(self.login_frame, text="Servidor (Host):", font=("Helvetica", 10)).grid(row=2, column=0, sticky=tk.W, pady=6)
        self.entry_host = ttk.Entry(self.login_frame, width=28, font=("Helvetica", 10))
        self.entry_host.insert(0, str(self.host))
        self.entry_host.grid(row=2, column=1, pady=6)

        ttk.Label(self.login_frame, text="Porta:", font=("Helvetica", 10)).grid(row=3, column=0, sticky=tk.W, pady=6)
        self.entry_port = ttk.Entry(self.login_frame, width=28, font=("Helvetica", 10))
        self.entry_port.insert(0, str(self.port))
        self.entry_port.grid(row=3, column=1, pady=6)

        self.lbl_status = ttk.Label(self.login_frame, text="", foreground="red", font=("Helvetica", 9))
        self.lbl_status.grid(row=4, column=0, columnspan=2, pady=10)

        btn_conectar = ttk.Button(self.login_frame, text="Entrar no Chat", command=self.acao_conectar)
        btn_conectar.grid(row=5, column=0, columnspan=2, pady=10, ipady=4, sticky=tk.EW)

        self.entry_user.bind("<Return>", lambda event: self.acao_conectar())
        self.entry_host.bind("<Return>", lambda event: self.acao_conectar())
        self.entry_port.bind("<Return>", lambda event: self.acao_conectar())

    def acao_conectar(self):
        usuario = self.entry_user.get().strip()
        host = self.entry_host.get().strip()
        porta_str = self.entry_port.get().strip()

        if not usuario:
            self.lbl_status.config(text="Por favor, digite um nome de usuário.")
            return

        try:
            porta = int(porta_str)
        except ValueError:
            self.lbl_status.config(text="Porta inválida. Digite um número.")
            return

        self.user = usuario
        self.host = host
        self.port = porta

        self.lbl_status.config(text="Conectando...", foreground="blue")
        self.root.update_idletasks()

        sucesso, erro = self.conectar_ao_servidor()
        if sucesso:
            self.login_frame.destroy()
            self.criar_interface_chat()
            self.iniciar_threads()
        else:
            self.lbl_status.config(text=erro, foreground="red")

    # -------------------------------------------------------------
    # CONEXÃO E AUTENTICAÇÃO COM O SERVIDOR
    # -------------------------------------------------------------
    def conectar_ao_servidor(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((self.host, self.port))
        except Exception:
            return False, "ERRO: Não foi possível conectar ao servidor.\nVerifique se o servidor está em execução."

        # Handshake com o servidor
        try:
            autenticado = False
            while not autenticado:
                server_com = self.client_socket.recv(1024).decode('utf-8')
                if not server_com:
                    self.client_socket.close()
                    return False, "ERRO: Conexão recusada ou usuário já em uso."

                linhas = server_com.strip().split('\n')
                for linha in linhas:
                    linha = linha.strip()
                    if linha == 'USER':
                        self.client_socket.sendall((self.user + '\n').encode('utf-8'))
                    elif linha == 'OK':
                        autenticado = True
                        break

            self.conectado = True
            return True, ""
        except Exception as e:
            self.client_socket.close()
            return False, f"Erro na autenticação: {e}"

    # -------------------------------------------------------------
    # CRIAÇÃO DA INTERFACE PRINCIPAL DO CHAT
    # -------------------------------------------------------------
    def criar_interface_chat(self):
        self.root.title(f"Chat RPG - {self.user}")

        # Configurar estilos de tema escuro agradável
        estilo = ttk.Style()
        estilo.theme_use("clam")

        # Container principal
        main_frame = ttk.Frame(self.root, padding=6)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. Barra de Topo / Informações
        top_frame = ttk.Frame(main_frame, padding=(4, 2))
        top_frame.pack(fill=tk.X, side=tk.TOP, pady=(0, 4))

        self.lbl_info_user = ttk.Label(
            top_frame,
            text=f"Usuário: {self.user}",
            font=("Helvetica", 10, "bold")
        )
        self.lbl_info_user.pack(side=tk.LEFT, padx=6)

        self.lbl_info_canal = ttk.Label(
            top_frame,
            text="Canal: [Geral]",
            font=("Helvetica", 10)
        )
        self.lbl_info_canal.pack(side=tk.LEFT, padx=12)

        self.lbl_info_grupo = ttk.Label(
            top_frame,
            text="Grupo: Nenhum",
            font=("Helvetica", 10),
            foreground="#555555"
        )
        self.lbl_info_grupo.pack(side=tk.LEFT, padx=6)

        btn_ajuda = ttk.Button(top_frame, text="Ajuda (/help)", command=lambda: self.processar_entrada("/help"))
        btn_ajuda.pack(side=tk.RIGHT, padx=4)

        btn_sair = ttk.Button(top_frame, text="Sair (/sair)", command=self.ao_fechar)
        btn_sair.pack(side=tk.RIGHT, padx=4)

        # 2. Painel Central: Área de Prints (Mensagens) + Lista de Usuários Online
        center_frame = ttk.Frame(main_frame)
        center_frame.pack(fill=tk.BOTH, expand=True)

        # Área de Prints (ScrolledText)
        self.text_area = scrolledtext.ScrolledText(
            center_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            background="#1e1e1e",
            foreground="#dcdcdc",
            insertbackground="#ffffff",
            selectbackground="#264f78",
            padx=10,
            pady=8,
            state=tk.DISABLED
        )
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Configurar tags de cores para diferentes tipos de mensagens
        self.text_area.tag_config("geral", foreground="#e0e0e0")
        self.text_area.tag_config("grupo", foreground="#4caf50")        # Verde
        self.text_area.tag_config("sussurro", foreground="#ba68c8")     # Roxo/Lilás
        self.text_area.tag_config("sistema", foreground="#ffb74d")      # Laranja claro
        self.text_area.tag_config("servidor", foreground="#64b5f6")     # Azul claro
        self.text_area.tag_config("erro", foreground="#ef5350")         # Vermelho
        self.text_area.tag_config("destaque", foreground="#ffee58", font=("Consolas", 10, "bold"))

        # Painel lateral: Usuários Online
        users_frame = ttk.LabelFrame(center_frame, text=" Online ", padding=4)
        users_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(6, 0))

        self.listbox_users = tk.Listbox(
            users_frame,
            width=16,
            font=("Helvetica", 9),
            background="#252526",
            foreground="#cccccc",
            selectbackground="#094771",
            selectforeground="#ffffff",
            bd=0,
            highlightthickness=0
        )
        self.listbox_users.pack(fill=tk.BOTH, expand=True)
        self.listbox_users.bind("<Double-Button-1>", self.ao_clicar_usuario_online)

        lbl_dica = ttk.Label(users_frame, text="2 cliques = DM", font=("Helvetica", 7), foreground="#888888")
        lbl_dica.pack(side=tk.BOTTOM, pady=2)

        # 3. Painel Inferior: Área de Input do Usuário
        input_frame = ttk.Frame(main_frame, padding=(0, 6))
        input_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.lbl_prefixo = ttk.Label(
            input_frame,
            text="[Geral]: ",
            font=("Consolas", 10, "bold")
        )
        self.lbl_prefixo.pack(side=tk.LEFT, padx=(4, 6))

        self.entry_mensagem = tk.Entry(
            input_frame,
            font=("Consolas", 10),
            background="#2d2d2d",
            foreground="#ffffff",
            insertbackground="#ffffff",
            relief=tk.FLAT,
            bd=4
        )
        self.entry_mensagem.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6), ipady=3)
        self.entry_mensagem.focus_set()

        btn_enviar = ttk.Button(input_frame, text="Enviar", command=self.enviar_mensagem_interface)
        btn_enviar.pack(side=tk.RIGHT, padx=4)

        # Tecla Enter envia a mensagem
        self.entry_mensagem.bind("<Return>", lambda event: self.enviar_mensagem_interface())

    # -------------------------------------------------------------
    # THREADS DE RECEBIMENTO E INICIALIZAÇÃO
    # -------------------------------------------------------------
    def iniciar_threads(self):
        # Mensagens iniciais de boas-vindas
        self.print_ui("-======= Bem-vindo ao Chat ======-", tag="destaque")
        self.print_ui("Comandos: /s (Dizer), /p (Grupo), /w <jogador> (Sussurro), /inv <jogador>, /online (Ver os usuários online)", tag="sistema")
        self.print_ui("Digite '/sair' para encerrar.\n", tag="sistema")

        # Solicita a lista inicial de usuários
        try:
            self.client_socket.sendall((json.dumps({"acao": "USER_LIST", "origem": self.user}) + '\n').encode('utf-8'))
        except Exception as e:
            self.print_ui(f"Erro ao requisitar lista de usuários: {e}", tag="erro")

        # Inicia a thread de recebimento do servidor
        self.thread_recv = threading.Thread(target=self.receive_loop, daemon=True)
        self.thread_recv.start()

    # -------------------------------------------------------------
    # ÁREA DE PRINTS (MENSAGENS NA INTERFACE)
    # -------------------------------------------------------------
    def print_ui(self, texto: str, tag: str = None):
        """Thread-safe print para a área de mensagens da UI."""
        self.root.after(0, self._append_print, texto, tag)

    def _append_print(self, texto: str, tag: str = None):
        self.text_area.config(state=tk.NORMAL)
        if tag:
            self.text_area.insert(tk.END, texto + '\n', tag)
        else:
            self.text_area.insert(tk.END, texto + '\n')
        self.text_area.see(tk.END)
        self.text_area.config(state=tk.DISABLED)

    # -------------------------------------------------------------
    # ÁREA DE INPUT (ENVIO DE MENSAGENS E PROCESSAMENTO DE COMANDOS)
    # -------------------------------------------------------------
    def enviar_mensagem_interface(self):
        entrada = self.entry_mensagem.get().strip()
        if not entrada:
            return

        self.entry_mensagem.delete(0, tk.END)
        self.processar_entrada(entrada)

    def atualizar_prefixo(self):
        if self.canal_atual == '/w':
            prefixo = f'[{self.alvo_atual}]: '
            self.lbl_info_canal.config(text=f"Canal: [Sussurro para {self.alvo_atual}]")
        elif self.canal_atual == '/s':
            prefixo = '[Geral]: '
            self.lbl_info_canal.config(text="Canal: [Geral]")
        else:
            prefixo = '[Grupo]: '
            self.lbl_info_canal.config(text="Canal: [Grupo]")

        self.lbl_prefixo.config(text=prefixo)

    def atualizar_status_grupo(self):
        if self.em_grupo:
            self.lbl_info_grupo.config(text="Grupo: Ativo", foreground="#4caf50")
        else:
            self.lbl_info_grupo.config(text="Grupo: Nenhum", foreground="#888888")

    def processar_entrada(self, entrada: str):
        if entrada[0] == '/':
            partes = entrada.split(' ', 1)
            comando = partes[0].lower()

            if comando in ['/s', '/p']:
                if comando == '/p' and not self.em_grupo:
                    self.print_ui('ERRO: Você não está em nenhum grupo.', tag="erro")
                    return
                self.canal_atual = comando
                self.atualizar_prefixo()
                if len(partes) > 1:
                    mensagem = partes[1]
                else:
                    return

            elif comando == '/w':
                if len(partes) > 1:
                    sussurro_partes = partes[1].split(' ', 1)
                    alvo_atual = sussurro_partes[0]
                    if self.verifica_alvo(alvo_atual):
                        self.canal_atual = '/w'
                        self.alvo_atual = alvo_atual
                        self.atualizar_prefixo()
                    else:
                        return
                    if len(sussurro_partes) > 1:
                        mensagem = sussurro_partes[1]
                    else:
                        return
                else:
                    self.print_ui('ERRO: Utilize a formatação: /w <destino> [mensagem]', tag="erro")
                    return

            elif comando in ['/invite', '/convidar', '/inv']:
                if len(partes) > 1:
                    invite_partes = partes[1].split(' ', 1)
                    alvo = invite_partes[0]
                    if self.verifica_alvo(alvo):
                        if len(invite_partes) > 1:
                            self.print_ui('Uso incorreto. Tente /invite <fulano>', tag="erro")
                        elif alvo == self.user:
                            self.print_ui('Uso incorreto, você não pode convidar a si mesmo. Tente /invite <fulano>', tag="erro")
                        else:
                            self.invite(alvo)
                    else:
                        self.print_ui('O alvo não está online.', tag="erro")
                else:
                    self.print_ui('Uso incorreto. Tente /invite <fulano>', tag="erro")
                return

            elif comando in ['/accept', '/aceitar']:
                if self.em_grupo:
                    self.print_ui("Você já está em um grupo.", tag="erro")
                elif not self.convite:
                    self.print_ui("Não há nenhum convite.", tag="erro")
                else:
                    self.accept_inv()
                return

            elif comando in ['/leavep', '/leaveg', '/lp', '/lg']:
                self.leave_group()
                self.canal_atual = '/s'
                self.atualizar_prefixo()
                return

            elif comando == '/sair':
                self.print_ui('Saindo...', tag="sistema")
                self.ao_fechar()
                return

            elif comando == '/online':
                self.print_ui(f'Os usuários online no momento são: {self.lista_local}\n', tag="sistema")
                return

            elif comando == '/help':
                help_msg = (
                    '\nComandos disponíveis:\n'
                    '/help - Ajuda - mostra essa página.\n'
                    '/s - Fala no chat geral.\n'
                    '/p - Fala no chat do grupo.\n'
                    '/w <alvo> - Manda uma mensagem direta à um alvo\n'
                    '/invite, /inv, /convidar - Convida um alvo para seu grupo.\n'
                    '/accept, /aceitar - Aceita um convite de grupo pendente.\n'
                    '/leavep, /leaveg, /lp, /lg - Sai do grupo atual.\n'
                    '/sair - Sai do servidor.\n'
                    '/online - Mostra os usuários atualmente online.\n'
                    '=)\n'
                )
                self.print_ui(help_msg, tag="sistema")
                return

            else:
                self.print_ui('ERRO: Comando desconhecido.', tag="erro")
                return

        else:
            mensagem = entrada

        # Envia de acordo com o canal atual
        if self.canal_atual == '/s':
            self.broadcast_message(mensagem)
        elif self.canal_atual == '/p':
            self.group_message(mensagem)
        elif self.canal_atual == '/w':
            self.direct_message(self.alvo_atual, mensagem)

    # -------------------------------------------------------------
    # MÉTODOS DE REDE / PROTOCOLO SOCKET
    # -------------------------------------------------------------
    def verifica_alvo(self, alvo: str):
        if alvo == self.user:
            self.print_ui('ERRO: Você não pode mandar uma DM para si mesmo.', tag="erro")
            return False
        if alvo not in self.lista_local:
            self.print_ui(f'ERRO: O usuário mencionado {alvo} não foi encontrado ou está offline', tag="erro")
            return False
        return True

    def invite(self, destino):
        grupo = {
            "acao": "INVITE",
            "convidante": self.user,
            "convidado": destino
        }
        self.enviar_json(grupo)

    def leave_group(self):
        info = {
            "acao": "LEAVE_GROUP",
            "origem": self.user
        }
        self.em_grupo = False
        self.atualizar_status_grupo()
        self.enviar_json(info)

    def accept_inv(self):
        info = {
            "acao": "ACCEPT",
            "convidante": self.convite,
            "convidado": self.user
        }
        self.enviar_json(info)
        self.convite = None

    def direct_message(self, destino, mensagem):
        info = {
            "acao": 'DIRECT',
            "origem": self.user,
            "destino": destino,
            "mensagem": mensagem
        }
        self.enviar_json(info)

    def group_message(self, mensagem):
        info = {
            "acao": 'GROUP_MSG',
            "origem": self.user,
            "mensagem": mensagem
        }
        self.enviar_json(info)

    def broadcast_message(self, mensagem):
        info = {
            "acao": "BROADCAST",
            "origem": self.user,
            "mensagem": mensagem
        }
        self.enviar_json(info)

    def enviar_json(self, dicionario: dict):
        if not self.conectado:
            self.print_ui("ERRO: Cliente desconectado.", tag="erro")
            return
        try:
            dados = json.dumps(dicionario) + '\n'
            self.client_socket.sendall(dados.encode('utf-8'))
        except Exception as e:
            self.print_ui(f"ERRO ao enviar dados: {e}", tag="erro")

    # -------------------------------------------------------------
    # RECEBIMENTO E PROCESSAMENTO DE PACOTES DO SERVIDOR
    # -------------------------------------------------------------
    def receive_loop(self):
        buffer = ""
        while self.conectado:
            try:
                raw_data = self.client_socket.recv(1024).decode('utf-8')
                if not raw_data:
                    self.print_ui('Conexão encerrada pelo servidor.', tag="erro")
                    self.conectado = False
                    break

                buffer += raw_data
                while '\n' in buffer:
                    linha, buffer = buffer.split('\n', 1)
                    linha = linha.strip()
                    if not linha:
                        continue
                    try:
                        jinfo = json.loads(linha)
                        self.tratar_mensagem_recebida(jinfo)
                    except json.JSONDecodeError:
                        # Se não for JSON direto (ex: texto solto de handshake antigo)
                        if linha:
                            self.print_ui(linha, tag="servidor")
            except Exception:
                if self.conectado:
                    self.print_ui('Conexão encerrada.', tag="erro")
                self.conectado = False
                break

    def tratar_mensagem_recebida(self, jinfo: dict):
        acao = jinfo.get("acao")

        if acao == "GROUP_MSG":
            origem = jinfo.get("origem", "")
            msg = jinfo.get("mensagem", "")
            self.print_ui(f'[GRUPO] - {origem}: {msg}', tag="grupo")

        elif acao == "DIRECT":
            origem = jinfo.get("origem", "")
            destino = jinfo.get("destino", "")
            msg = jinfo.get("mensagem", "")
            if origem != self.user:
                self.print_ui(f'W - De <{origem}>: {msg}', tag="sussurro")
            else:
                self.print_ui(f'W - Para <{destino}>: {msg}', tag="sussurro")

        elif acao == "BROADCAST":
            origem = jinfo.get("origem", "")
            msg = jinfo.get("mensagem", "")
            self.print_ui(f'Geral - {origem}: {msg}', tag="geral")

        elif acao == "INVITE":
            self.convite = jinfo.get("convidante")
            self.print_ui(f'Você recebeu um convite para grupo de {self.convite}. Use /accept para aceitar', tag="sistema")

        elif acao == "SERVER":
            msg = jinfo.get("mensagem", "")
            self.print_ui(f'{msg}', tag="servidor")
            if "se juntou ao grupo." in msg:
                self.em_grupo = True
                self.root.after(0, self.atualizar_status_grupo)
            elif "saiu do grupo" in msg and self.user in msg:
                self.em_grupo = False
                self.root.after(0, self.atualizar_status_grupo)

        elif acao == 'USERS_LIST':
            self.lista_local = jinfo.get('users', [])
            self.root.after(0, self.atualizar_lista_usuarios_ui)

        else:
            self.print_ui(f"Mensagem do servidor: {jinfo}", tag="servidor")

    def atualizar_lista_usuarios_ui(self):
        if hasattr(self, 'listbox_users'):
            self.listbox_users.delete(0, tk.END)
            for u in self.lista_local:
                prefixo = "★ " if u == self.user else "• "
                self.listbox_users.insert(tk.END, f"{prefixo}{u}")

    def ao_clicar_usuario_online(self, event):
        selecao = self.listbox_users.curselection()
        if selecao:
            item = self.listbox_users.get(selecao[0])
            nome = item.replace("★ ", "").replace("• ", "").strip()
            if nome != self.user:
                self.entry_mensagem.delete(0, tk.END)
                self.entry_mensagem.insert(0, f"/w {nome} ")
                self.entry_mensagem.focus_set()

    # -------------------------------------------------------------
    # ENCERRAMENTO LIMPO
    # -------------------------------------------------------------
    def ao_fechar(self):
        if self.conectado:
            try:
                leave_msg = json.dumps({"acao": "LEAVE_SERVER", "origem": self.user}) + '\n'
                self.client_socket.sendall(leave_msg.encode('utf-8'))
            except Exception:
                pass
            self.conectado = False
            try:
                self.client_socket.close()
            except Exception:
                pass
        self.root.destroy()
        sys.exit(0)

if __name__ == "__main__":
    usuario_arg = sys.argv[1] if len(sys.argv) > 1 else None
    root = tk.Tk()
    app = ChatClientGUI(root, user=usuario_arg)
    root.mainloop()

