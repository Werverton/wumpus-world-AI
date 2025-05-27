import tkinter as tk
from tkinter import messagebox
import random

class MundoWumpus:
    def __init__(self, tamanho=4):
        self.root = tk.Tk()
        self.root.title("Mundo de Wumpus")
        
        self.tamanho = tamanho
        self.criar_mundo()
        self.desenhar_mapa()
        
        # Adicionar controles
        self.frame_controles = tk.Frame(self.root)
        self.frame_controles.pack(pady=10)
        
        tk.Button(self.frame_controles, text="Reiniciar", command=self.reiniciar_jogo).pack(side=tk.LEFT, padx=5)
        tk.Button(self.frame_controles, text="Instruções", command=self.mostrar_instrucoes).pack(side=tk.LEFT, padx=5)
        
        # Adicionar botão para atirar flecha
        self.frame_acao = tk.Frame(self.root)
        self.frame_acao.pack(pady=10)

        self.direcao = tk.StringVar(value="N")  # Direção padrão
        opcoes_direcao = ["N", "S", "L", "O"]
        for direcao_opcao in opcoes_direcao:
            tk.Radiobutton(self.frame_acao, text=direcao_opcao, variable=self.direcao, value=direcao_opcao).pack(side=tk.LEFT)

        tk.Button(self.frame_acao, text="Atirar Flecha", command=self.atirar_flecha).pack(side=tk.LEFT, padx=5)

        self.modo_auto = False
        tk.Button(self.frame_controles, text="Modo Automático", command=self.toggle_modo_auto).pack(side=tk.LEFT, padx=5)

        self.root.mainloop()
    
    def criar_mundo(self):
        # Inicializar o mundo vazio
        self.mundo = [[{'wumpus': False, 'poço': False, 'ouro': False, 'brilho': False, 
                        'brisa': False, 'fedor': False, 'visitado': False} 
                      for _ in range(self.tamanho)] for _ in range(self.tamanho)]

        # Posicionar o Wumpus (1 único)
        while True:
            wumpus_x, wumpus_y = random.randint(0, self.tamanho-1), random.randint(0, self.tamanho-1)
            if (wumpus_x, wumpus_y) != (0, 0):
                self.mundo[wumpus_x][wumpus_y]['wumpus'] = True
                break

        # Posicionar poços (20% das casas, exceto a inicial (0,0))
        for i in range(self.tamanho):
            for j in range(self.tamanho):
                if (i, j) != (0, 0) and random.random() < 0.2:
                    self.mundo[i][j]['poço'] = True

        # Posicionar o ouro (1 único)
        while True:
            ouro_x, ouro_y = random.randint(0, self.tamanho-1), random.randint(0, self.tamanho-1)
            if (ouro_x, ouro_y) != (0, 0) and not self.mundo[ouro_x][ouro_y]['wumpus']:
                self.mundo[ouro_x][ouro_y]['ouro'] = True
                self.mundo[ouro_x][ouro_y]['brilho'] = True
                break

        # Calcular fedor (casas adjacentes ao Wumpus)
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = wumpus_x + dx, wumpus_y + dy
            if 0 <= nx < self.tamanho and 0 <= ny < self.tamanho:
                self.mundo[nx][ny]['fedor'] = True

        # Calcular brisa (casas adjacentes a poços)
        for i in range(self.tamanho):
            for j in range(self.tamanho):
                if self.mundo[i][j]['poço']:
                    for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                        nx, ny = i + dx, j + dy
                        if 0 <= nx < self.tamanho and 0 <= ny < self.tamanho:
                            # Não coloca brisa na casa (0,0)
                            if (nx, ny) != (0, 0):
                                self.mundo[nx][ny]['brisa'] = True

        # Posição inicial do agente
        self.agente_pos = (0, 0)
        self.mundo[self.agente_pos[0]][self.agente_pos[1]]['visitado'] = True
        self.agente_tem_ouro = False
        self.flecha_disponivel = True
        self.anterior = None  # Reinicia a referência da casa anterior
    
    def desenhar_mapa(self):
        # Criar frame para o mapa
        if hasattr(self, 'frame_mapa'):
            self.frame_mapa.destroy()
        
        self.frame_mapa = tk.Frame(self.root)
        self.frame_mapa.pack(padx=10, pady=10)
        
        self.celulas = []
        tamanho_celula = 80
        
        for i in range(self.tamanho):
            linha_celulas = []
            for j in range(self.tamanho):
                frame = tk.Frame(self.frame_mapa, width=tamanho_celula, height=tamanho_celula, 
                                borderwidth=1, relief="solid", bg="white")
                frame.grid(row=i, column=j, padx=2, pady=2)
                frame.bind("<Button-1>", lambda e, x=i, y=j: self.clicar_celula(x, y))
                
                # Adicionar rótulos para os elementos
                label = tk.Label(frame, text="", bg="white")
                label.place(relx=0.5, rely=0.5, anchor="center")
                
                linha_celulas.append((frame, label))
            self.celulas.append(linha_celulas)
        
        self.atualizar_display()
    
    def atualizar_display(self):
        for i in range(self.tamanho):
            for j in range(self.tamanho):
                frame, label = self.celulas[i][j]
                celula = self.mundo[i][j]
                
                # Cor de fundo
                if (i, j) == self.agente_pos:
                    frame.config(bg="lightblue")
                elif celula['visitado']:
                    frame.config(bg="lightgray")
                else:
                    frame.config(bg="white")
                
                # Símbolos
                texto = ""
                if celula['visitado'] or (i, j) == self.agente_pos:
                    if celula['wumpus']:
                        texto += "W"
                    if celula['poço']:
                        texto += "P"
                    if celula['ouro']:
                        texto += "O"
                    if celula['brilho']:
                        texto += "★"
                    if celula['brisa']:
                        texto += "~"
                    if celula['fedor']:
                        texto += "§"
                    if celula.get('grito', False):  # Adiciona o grito
                        texto += "!"

                label.config(text=texto or " ")
    
    def clicar_celula(self, x, y):
        # Verificar se o movimento é válido (adjacente)
        dx = abs(x - self.agente_pos[0])
        dy = abs(y - self.agente_pos[1])
        
        if (dx == 1 and dy == 0) or (dx == 0 and dy == 1):
            self.mover_agente(x, y)
        else:
            messagebox.showinfo("Movimento inválido", "Você só pode mover para casas adjacentes!")
    
    def mover_agente(self, x, y):
        # Verificar perigos
        celula = self.mundo[x][y]
        
        if celula['wumpus']:
            messagebox.showinfo("Fim de jogo", "Você foi devorado pelo Wumpus!")
            self.reiniciar_jogo()
            return
        elif celula['poço']:
            messagebox.showinfo("Fim de jogo", "Você caiu em um poço!")
            self.reiniciar_jogo()
            return
        
        # Atualizar posição do agente
        self.agente_pos = (x, y)
        self.mundo[x][y]['visitado'] = True
        
        # Verificar se pegou o ouro
        if celula['ouro'] and not self.agente_tem_ouro:
            self.agente_tem_ouro = True
            celula['ouro'] = False
            celula['brilho'] = False
            messagebox.showinfo("Ouro", "Você encontrou o ouro!")
        
        # Verificar vitória (voltar ao início com o ouro)
        if self.agente_pos == (0, self.tamanho-1) and self.agente_tem_ouro:
            messagebox.showinfo("Vitória", "Parabéns! Você venceu o jogo!")
            self.reiniciar_jogo()
            return
        
        self.atualizar_display()
    
    def reiniciar_jogo(self):
        self.criar_mundo()
        self.desenhar_mapa()
    
    def mostrar_instrucoes(self):
        instrucoes = """
        === Mundo de Wumpus ===
        
        Objetivo: Encontrar o ouro e voltar à saída.
        
        Perigos:
        W - Wumpus (morte instantânea)
        P - Poço (morte instantânea)
        
        Pistas:
        § - Fedor (Wumpus próximo)
        ~ - Brisa (Poço próximo)
        ★ - Brilho (Ouro nesta casa)
        
        Controles:
        - Clique em casas adjacentes para mover
        - Você começa no canto inferior esquerdo
        """
        messagebox.showinfo("Instruções", instrucoes)
    
    def atirar_flecha(self):
        if not self.flecha_disponivel:
            messagebox.showinfo("Aviso", "Você não tem flechas!")
            return

        direcao = self.direcao.get()
        x, y = self.agente_pos

        # Determinar a próxima célula na direção do tiro
        if direcao == "N":
            alvo_x, alvo_y = x - 1, y
        elif direcao == "S":
            alvo_x, alvo_y = x + 1, y
        elif direcao == "L":
            alvo_x, alvo_y = x, y + 1
        elif direcao == "O":
            alvo_x, alvo_y = x, y - 1
        else:
            messagebox.showinfo("Erro", "Direção inválida!")
            return

        # Verificar se a célula alvo está dentro dos limites do mapa
        if 0 <= alvo_x < self.tamanho and 0 <= alvo_y < self.tamanho:
            # Verificar se o Wumpus está na célula alvo
            if self.mundo[alvo_x][alvo_y]['wumpus']:
                messagebox.showinfo("Resultado", "Você matou o Wumpus!")
                self.mundo[alvo_x][alvo_y]['wumpus'] = False
                self.flecha_disponivel = False

                # Adicionar "Grito" nas células adjacentes
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = alvo_x + dx, alvo_y + dy
                    if 0 <= nx < self.tamanho and 0 <= ny < self.tamanho:
                        self.mundo[nx][ny]['grito'] = True
            else:
                messagebox.showinfo("Resultado", "Você não acertou nada!")
                self.flecha_disponivel = False
        else:
            messagebox.showinfo("Resultado", "A flecha saiu do mapa!")
            self.flecha_disponivel = False

        self.atualizar_display()

    def toggle_modo_auto(self):
        self.modo_auto = not self.modo_auto
        if self.modo_auto:
            self.auto_explorar()

    def auto_explorar(self):
        if not self.modo_auto:
            return

        x, y = self.agente_pos
        celula = self.mundo[x][y]

        # Se encontrou ouro, mostra mensagem para voltar à origem
        if celula['ouro'] and not self.agente_tem_ouro:
            self.agente_tem_ouro = True
            celula['ouro'] = False
            celula['brilho'] = False
            self.atualizar_display()
            messagebox.showinfo("Ouro encontrado", "Você encontrou o ouro! Volte para a casa de origem (0,0) para vencer.")
            self.root.after(500, self.auto_explorar)
            return

        # Se chegou na origem com o ouro, mostra mensagem de vitória
        if self.agente_tem_ouro and self.agente_pos == (0, 0):
            messagebox.showinfo("Vitória", "O agente encontrou o ouro e voltou ao início! Você venceu!")
            self.reiniciar_jogo()
            return

        # Se sentir fedor ou brisa, volta para a casa anterior se possível
        if (celula['fedor'] or celula['brisa']) and hasattr(self, 'anterior'):
            self.agente_pos = self.anterior
            self.mundo[self.agente_pos[0]][self.agente_pos[1]]['visitado'] = True
            self.atualizar_display()
            self.root.after(500, self.auto_explorar)
            return

        # Explora casas adjacentes não visitadas
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.tamanho and 0 <= ny < self.tamanho:
                if not self.mundo[nx][ny]['visitado']:
                    self.anterior = (x, y)
                    self.agente_pos = (nx, ny)
                    self.mundo[nx][ny]['visitado'] = True
                    self.atualizar_display()
                    self.root.after(500, self.auto_explorar)
                    return

        # Se não há mais casas para explorar, para
        messagebox.showinfo("Fim", "O agente não encontrou mais casas seguras para explorar.")
        self.modo_auto = False

# Iniciar o jogo
if __name__ == "__main__":
    MundoWumpus(tamanho=8)