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


def selecionar_saida():
    caminho = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel", "*.xlsx")]
    )
    if caminho:
        entry_saida.delete(0, tk.END)
        entry_saida.insert(0, caminho)


def executar():
    entrada = entry_entrada.get()
    saida = entry_saida.get()

    if not entrada:
        messagebox.showerror("Erro", "Selecione um arquivo de entrada.")
        return

    # desabilita botão
    btn_run.config(state="disabled", bg="gray")

    # mostra barra de progresso
    progress_bar.grid()
    progress_bar["value"] = 0

    status_label.config(text="Iniciando...", fg="orange")

    # thread para não travar UI
    thread = threading.Thread(target=processar_thread, args=(entrada, saida))
    thread.start()


def atualizar_progresso(atual, total):
    percentual = (atual / total) * 100

    progress_bar["value"] = percentual
    status_label.config(text=f"Processando {atual} / {total}")


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
    btn_run.config(state="normal", bg="#4CAF50")

    status_label.config(text="Concluído ✔", fg="green")
    messagebox.showinfo("Sucesso", f"Arquivo gerado:\n{caminho_saida}")


def finalizar_erro(erro):
    btn_run.config(state="normal", bg="#4CAF50")

    status_label.config(text="Erro ❌", fg="red")
    messagebox.showerror("Erro", erro)


# =========================
# UI
# =========================
root = tk.Tk()
root.title("Identificador de Comarca CNJ")
root.geometry("520x320")
root.resizable(False, False)

frame = tk.Frame(root)
frame.pack(padx=20, pady=20)

# Entrada
tk.Label(frame, text="Arquivo de Entrada", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w")

entry_entrada = tk.Entry(frame, width=55)
entry_entrada.grid(row=1, column=0, pady=5)

btn_entrada = tk.Button(frame, text="Selecionar", width=12, command=selecionar_entrada)
btn_entrada.grid(row=1, column=1, padx=5)

# Saída
tk.Label(frame, text="Arquivo de Saída", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=(10, 0))

entry_saida = tk.Entry(frame, width=55)
entry_saida.grid(row=3, column=0, pady=5)

btn_saida = tk.Button(frame, text="Selecionar", width=12, command=selecionar_saida)
btn_saida.grid(row=3, column=1, padx=5)

# Botão principal
btn_run = tk.Button(
    frame,
    text="Processar",
    width=30,
    height=2,
    bg="#4CAF50",
    fg="white",
    command=executar
)
btn_run.grid(row=4, column=0, columnspan=2, pady=15)

# Barra de progresso (inicialmente escondida)
progress_bar = ttk.Progressbar(
    frame,
    orient="horizontal",
    length=350,
    mode="determinate"
)
progress_bar.grid(row=5, column=0, columnspan=2, pady=5)
progress_bar.grid_remove()

# Status
status_label = tk.Label(frame, text="Aguardando...", font=("Arial", 9))
status_label.grid(row=6, column=0, columnspan=2)

root.mainloop()