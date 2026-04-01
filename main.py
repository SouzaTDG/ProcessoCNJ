import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import sys
import threading

from core.processor import processar_arquivo


# =========================
# CAMINHO PARA EXE
# =========================
def caminho_recurso(rel_path):
    """Funciona tanto no .py quanto no .exe"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, rel_path)


# =========================
# CLASSE CUSTOM BUTTON COM HOVER
# =========================
class HoverButton(tk.Button):
    def __init__(self, master, bg_normal, bg_hover, **kwargs):
        super().__init__(master, **kwargs)
        self.bg_normal = bg_normal
        self.bg_hover = bg_hover
        self.config(bg=bg_normal, relief="flat", cursor="hand2")
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self.config(bg=self.bg_hover)

    def on_leave(self, event):
        self.config(bg=self.bg_normal)


# =========================
# CLASSE CUSTOM ENTRY COM SOMBRA
# =========================
class ShadowFrame(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Sombra (frame cinza por trás)
        self.shadow = tk.Frame(master, bg="#D0D0D0", highlightthickness=0)
        self.shadow.place(x=kwargs.get('x', 0) + 2, y=kwargs.get('y', 0) + 2)
        
        self.config(bg="white", highlightthickness=0)


# =========================
# FUNÇÕES UI
# =========================
def selecionar_entrada():
    caminho = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx")])
    if caminho:
        entry_entrada.delete(0, tk.END)
        entry_entrada.insert(0, caminho)

        # sugere saída automática
        caminho_padrao = caminho.replace(".xlsx", "_corrigido.xlsx")
        entry_saida.delete(0, tk.END)
        entry_saida.insert(0, caminho_padrao)
        
        # atualiza label visual
        atualizar_label_arquivo()


def selecionar_saida():
    caminho = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel", "*.xlsx")]
    )
    if caminho:
        entry_saida.delete(0, tk.END)
        entry_saida.insert(0, caminho)


def atualizar_label_arquivo():
    """Mostra nome do arquivo em vez do caminho completo"""
    caminho = entry_entrada.get()
    if caminho:
        nome_arquivo = os.path.basename(caminho)
        label_info_entrada.config(text=f"✓ {nome_arquivo}", fg="#4CAF50")
    else:
        label_info_entrada.config(text="Nenhum arquivo selecionado", fg="#999")


def executar():
    entrada = entry_entrada.get()
    saida = entry_saida.get()

    if not entrada:
        messagebox.showerror("Erro", "Selecione um arquivo de entrada.")
        return

    # desabilita botão
    btn_run.config(state="disabled")

    # mostra barra de progresso
    progress_frame.pack()
    progress_bar["value"] = 0

    status_label.config(text="Iniciando processamento...", fg="#FF9800")

    # thread para não travar UI
    thread = threading.Thread(target=processar_thread, args=(entrada, saida))
    thread.daemon = True
    thread.start()


def atualizar_progresso(atual, total):
    percentual = (atual / total) * 100

    progress_bar["value"] = percentual
    status_label.config(text=f"Processando: {atual} de {total} linhas", fg="#FF9800")


def processar_thread(entrada, saida):
    try:
        caminho_comarcas = caminho_recurso("data/comarcas.xlsx")
        caminho_tribunal = caminho_recurso("data/tribunal_uf.json")

        caminho_saida = processar_arquivo(
            entrada,
            caminho_comarcas,
            caminho_tribunal,
            saida if saida else None,
            callback_progresso=lambda atual, total: root.after(0, atualizar_progresso, atual, total)
        )

        root.after(0, lambda: finalizar_sucesso(caminho_saida))

    except Exception as e:
        root.after(0, lambda: finalizar_erro(str(e)))


def finalizar_sucesso(caminho_saida):
    progress_bar["value"] = 100
    btn_run.config(state="normal")

    status_label.config(text="✓ Processamento concluído com sucesso!", fg="#4CAF50")
    messagebox.showinfo("Sucesso", f"Arquivo gerado:\n\n{caminho_saida}")
    
    # reseta após sucesso
    root.after(3000, resetar_ui)


def finalizar_erro(erro):
    btn_run.config(state="normal")

    status_label.config(text="✗ Erro no processamento", fg="#F44336")
    messagebox.showerror("Erro", f"Ocorreu um erro:\n\n{erro}")


def resetar_ui():
    """Reseta estado da UI após processamento"""
    progress_frame.pack_forget()
    status_label.config(text="Pronto para processar", fg="#666")


# =========================
# TEMAS E CORES
# =========================
CORES = {
    "bg_principal": "#F8F9FA",
    "bg_card": "#FFFFFF",
    "accent": "#1976D2",
    "accent_hover": "#1565C0",
    "accent_light": "#E3F2FD",
    "sucesso": "#4CAF50",
    "sucesso_hover": "#45a049",
    "erro": "#F44336",
    "aviso": "#FF9800",
    "texto_primario": "#212121",
    "texto_secundario": "#666666",
    "borda": "#E0E0E0",
    "sombra": "#00000015"
}


# =========================
# UI PRINCIPAL
# =========================
root = tk.Tk()
root.title("Identificador de Comarca CNJ")
root.geometry("650x580")
root.resizable(False, False)
root.configure(bg=CORES["bg_principal"])

# Estilo ttk
style = ttk.Style()
style.theme_use('clam')
style.configure(
    'TProgressbar',
    thickness=10,
    troughcolor=CORES["borda"],
    background=CORES["accent"]
)


# Header - com mais destaque
header = tk.Frame(root, bg=CORES["accent"], height=90)
header.pack(fill="x", side="top")
header.pack_propagate(False)

titulo = tk.Label(
    header,
    text="📋 Identificador de Comarca CNJ",
    font=("Segoe UI", 20, "bold"),
    bg=CORES["accent"],
    fg="white"
)
titulo.pack(pady=12)

subtitulo = tk.Label(
    header,
    text="Processe seus arquivos Excel com facilidade e segurança",
    font=("Segoe UI", 9),
    bg=CORES["accent"],
    fg=CORES["accent_light"]
)
subtitulo.pack()


# Frame principal
main_frame = tk.Frame(root, bg=CORES["bg_principal"])
main_frame.pack(fill="both", expand=True, padx=20, pady=20)


# Card de entrada - com sombra
card_entrada_shadow = tk.Frame(main_frame, bg="#E8E8E8", highlightthickness=0)
card_entrada_shadow.pack(fill="x", pady=12, padx=2)

card_entrada = tk.Frame(card_entrada_shadow, bg=CORES["bg_card"], highlightthickness=0)
card_entrada.pack(fill="x", padx=3, pady=3)

# Borda superior arredondada
borda_entrada = tk.Frame(card_entrada, bg=CORES["accent"], height=4)
borda_entrada.pack(fill="x")
borda_entrada.pack_propagate(False)

# Conteúdo card
frame_entrada = tk.Frame(card_entrada, bg=CORES["bg_card"])
frame_entrada.pack(fill="x", padx=16, pady=14)

label_entrada = tk.Label(
    frame_entrada,
    text="📁 Arquivo de Entrada",
    font=("Segoe UI", 11, "bold"),
    bg=CORES["bg_card"],
    fg=CORES["texto_primario"]
)
label_entrada.pack(anchor="w", pady=(0, 8))

frame_input_entrada = tk.Frame(frame_entrada, bg=CORES["bg_card"])
frame_input_entrada.pack(fill="x", pady=6)

entry_entrada = tk.Entry(
    frame_input_entrada,
    font=("Segoe UI", 9),
    bg="white",
    fg=CORES["texto_primario"],
    relief="solid",
    borderwidth=1,
    width=48
)
entry_entrada.pack(side="left", fill="x", expand=True, ipady=6)

btn_entrada = HoverButton(
    frame_input_entrada,
    text="Selecionar",
    font=("Segoe UI", 9, "bold"),
    bg_normal=CORES["accent"],
    bg_hover=CORES["accent_hover"],
    fg="white",
    padx=18,
    pady=6,
    command=selecionar_entrada,
    activeforeground="white",
    activebackground=CORES["accent_hover"]
)
btn_entrada.pack(side="left", padx=10)

label_info_entrada = tk.Label(
    frame_entrada,
    text="Nenhum arquivo selecionado",
    font=("Segoe UI", 8),
    bg=CORES["bg_card"],
    fg="#999",
    pady=4
)
label_info_entrada.pack(anchor="w", pady=(4, 0))


# Card de saída - com sombra
card_saida_shadow = tk.Frame(main_frame, bg="#E8E8E8", highlightthickness=0)
card_saida_shadow.pack(fill="x", pady=12, padx=2)

card_saida = tk.Frame(card_saida_shadow, bg=CORES["bg_card"], highlightthickness=0)
card_saida.pack(fill="x", padx=3, pady=3)

borda_saida = tk.Frame(card_saida, bg=CORES["accent"], height=4)
borda_saida.pack(fill="x")
borda_saida.pack_propagate(False)

frame_saida = tk.Frame(card_saida, bg=CORES["bg_card"])
frame_saida.pack(fill="x", padx=16, pady=14)

label_saida = tk.Label(
    frame_saida,
    text="💾 Arquivo de Saída",
    font=("Segoe UI", 11, "bold"),
    bg=CORES["bg_card"],
    fg=CORES["texto_primario"]
)
label_saida.pack(anchor="w", pady=(0, 8))

frame_input_saida = tk.Frame(frame_saida, bg=CORES["bg_card"])
frame_input_saida.pack(fill="x", pady=6)

entry_saida = tk.Entry(
    frame_input_saida,
    font=("Segoe UI", 9),
    bg="white",
    fg=CORES["texto_primario"],
    relief="solid",
    borderwidth=1,
    width=48
)
entry_saida.pack(side="left", fill="x", expand=True, ipady=6)

btn_saida = HoverButton(
    frame_input_saida,
    text="Selecionar",
    font=("Segoe UI", 9, "bold"),
    bg_normal=CORES["accent"],
    bg_hover=CORES["accent_hover"],
    fg="white",
    padx=18,
    pady=6,
    command=selecionar_saida,
    activeforeground="white",
    activebackground=CORES["accent_hover"]
)
btn_saida.pack(side="left", padx=10)


# Botão de processamento - com sombra mais elaborada
btn_frame_shadow = tk.Frame(main_frame, bg="#D0D0D0", highlightthickness=0)
btn_frame_shadow.pack(pady=16)

btn_run = HoverButton(
    btn_frame_shadow,
    text="🚀 Processar",
    font=("Segoe UI", 12, "bold"),
    bg_normal=CORES["sucesso"],
    bg_hover=CORES["sucesso_hover"],
    fg="white",
    padx=48,
    pady=13,
    command=executar,
    activeforeground="white"
)
btn_run.pack(padx=3, pady=3)


# Frame de progresso (inicialmente escondido)
progress_frame = tk.Frame(main_frame, bg=CORES["bg_principal"])
progress_bar = ttk.Progressbar(
    progress_frame,
    orient="horizontal",
    mode="determinate"
)
progress_bar.pack(fill="x", padx=0, pady=8)


# Status
status_label = tk.Label(
    main_frame,
    text="Pronto para processar",
    font=("Segoe UI", 9),
    bg=CORES["bg_principal"],
    fg=CORES["texto_secundario"]
)
status_label.pack(pady=12)


# Footer - mais elegante
footer_sep = tk.Frame(root, bg=CORES["borda"], height=1)
footer_sep.pack(fill="x")
footer_sep.pack_propagate(False)

footer = tk.Frame(root, bg=CORES["bg_card"], height=35)
footer.pack(fill="x", side="bottom")
footer.pack_propagate(False)

footer_text = tk.Label(
    footer,
    text="🔒 Fortes & Fortes Advogados • Processador de Comarcas CNJ • Dados Seguros",
    font=("Segoe UI", 8),
    bg=CORES["bg_card"],
    fg=CORES["texto_secundario"]
)
footer_text.pack(pady=8)


root.mainloop()