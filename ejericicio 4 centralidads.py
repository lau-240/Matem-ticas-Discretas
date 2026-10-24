"""
Taller MAT 4021 Ejercicio 4:dir

"""

import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque
from fractions import Fraction

RED = "AB AC BC BD CD DE FG FH GH GI HJ IJ KL KM LM LN MN CH DL EF JK"


# ---------------------------------------------------------------- algoritmos
def leer_aristas(texto):
    aristas = []
    for a in texto.replace(",", " ").split():
        a = a.strip().upper()
        if len(a) != 2 or a[0] == a[1]:
            raise ValueError(f"Arista invalida: '{a}' (use dos letras distintas, ej. AB)")
        aristas.append((a[0], a[1]))
    if not aristas:
        raise ValueError("Escriba al menos una arista.")
    return aristas


def construir(aristas):
    adj = {}
    for u, v in aristas:
        adj.setdefault(u, set()).add(v)
        adj.setdefault(v, set()).add(u)
    return {v: sorted(adj[v]) for v in sorted(adj)}


def bfs(adj, s):
    dist, sigma = {s: 0}, {s: 1}
    cola = deque([s])
    while cola:
        v = cola.popleft()
        for w in adj[v]:
            if w not in dist:
                dist[w] = dist[v] + 1
                sigma[w] = 0
                cola.append(w)
            if dist[w] == dist[v] + 1:
                sigma[w] += sigma[v]
    return dist, sigma


def centralidades(adj):
    V = list(adj)
    n = len(V)
    if n < 3:
        raise ValueError("El grafo necesita al menos 3 vertices.")
    D, S = {}, {}
    for s in V:
        D[s], S[s] = bfs(adj, s)
    if len(D[V[0]]) != n:
        raise ValueError("El grafo debe ser conexo.")

    CD, CC, suma = {}, {}, {}
    for v in V:
        CD[v] = Fraction(len(adj[v]), n - 1)
        suma[v] = sum(D[v][u] for u in V if u != v)
        CC[v] = Fraction(n - 1, suma[v])

    CB = {v: Fraction(0) for v in V}
    for i, s in enumerate(V):
        for t in V[i + 1:]:
            for v in V:
                if v == s or v == t:
                    continue
                if D[s][v] + D[v][t] == D[s][t]:
                    CB[v] += Fraction(S[s][v] * S[v][t], S[s][t])
    norm = Fraction((n - 1) * (n - 2), 2)
    CBn = {v: CB[v] / norm for v in V}
    return D, suma, CD, CC, CB, CBn


def ranking(medida, k=3):
    """Top k con empates: devuelve (lista ordenada, hay_empate_en_el_corte)."""
    orden = sorted(medida.items(), key=lambda kv: (-kv[1], kv[0]))
    corte = orden[k - 1][1]
    empatados = [v for v, x in orden if x == corte]
    hay_empate = any(x == corte for _, x in orden[k:])
    return orden, empatados, hay_empate


# ------------------------------------------------------------------ interfaz
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MAT 4021 - Ejercicio 4: Medidas de centralidad")
        self.geometry("900x620")

        top = ttk.Frame(self, padding=8)
        top.pack(fill="x")
        ttk.Label(top, text="Aristas (ej. AB AC BC ...):").pack(anchor="w")
        self.entrada = tk.Text(top, height=3, wrap="word")
        self.entrada.insert("1.0", RED)
        self.entrada.pack(fill="x", pady=4)

        botones = ttk.Frame(top)
        botones.pack(fill="x")
        ttk.Button(botones, text="Calcular", command=self.calcular).pack(side="left")
        ttk.Button(botones, text="Cargar red de investigadores",
                   command=self.cargar_red).pack(side="left", padx=6)

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=8, pady=8)

        # Pestana 1: tabla de resultados
        self.tab_tabla = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_tabla, text="Resultados")
        cols = ("v", "deg", "CD", "sumd", "CC", "CB", "CBn")
        self.tree = ttk.Treeview(self.tab_tabla, columns=cols, show="headings")
        nombres = ["v", "deg", "CD", "Σ d", "CC", "CB", "C'B"]
        for c, nom in zip(cols, nombres):
            self.tree.heading(c, text=nom)
            self.tree.column(c, width=110, anchor="center")
        self.tree.column("v", width=50)
        self.tree.column("deg", width=60)
        self.tree.pack(fill="both", expand=True)

        # Pestana 2: matriz de distancias
        self.tab_matriz = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_matriz, text="Matriz de distancias")
        self.txt_matriz = tk.Text(self.tab_matriz, font=("Courier New", 11))
        self.txt_matriz.pack(fill="both", expand=True)

        # Pestana 3: respuestas
        self.tab_resp = ttk.Frame(self.tabs)
        self.tabs.add(self.tab_resp, text="Respuestas (c, d)")
        self.txt_resp = tk.Text(self.tab_resp, font=("Courier New", 11), wrap="word")
        self.txt_resp.pack(fill="both", expand=True)

        self.calcular()

    def cargar_red(self):
        self.entrada.delete("1.0", "end")
        self.entrada.insert("1.0", RED)
        self.calcular()

    def calcular(self):
        try:
            adj = construir(leer_aristas(self.entrada.get("1.0", "end")))
            D, suma, CD, CC, CB, CBn = centralidades(adj)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return
        V = list(adj)
        n = len(V)

        # Tabla
        self.tree.delete(*self.tree.get_children())
        for v in V:
            self.tree.insert("", "end", values=(
                v, len(adj[v]),
                f"{CD[v]} = {float(CD[v]):.3f}",
                suma[v],
                f"{CC[v]} = {float(CC[v]):.3f}",
                f"{float(CB[v]):.3f}",
                f"{float(CBn[v]):.3f}",
            ))

        # Matriz
        self.txt_matriz.delete("1.0", "end")
        self.txt_matriz.insert("end", "    " + " ".join(f"{v:>2}" for v in V) + "\n")
        for u in V:
            self.txt_matriz.insert(
                "end", f"{u:>2}  " + " ".join(f"{D[u][v]:>2}" for v in V) + "\n")

        # Respuestas
        r = []
        r.append(f"n = {n} vertices.  n-1 = {n-1},  (n-1)(n-2)/2 = {(n-1)*(n-2)//2}")
        r.append(f"Suma de CB = {sum(CB.values())}  (= {float(sum(CB.values())):.3f})\n")
        r.append("TOP 3 POR MEDIDA")
        for nombre, med in (("Grado", CD), ("Cercania", CC), ("Intermediacion", CB)):
            orden, empatados, hay_empate = ranking(med)
            top = ", ".join(f"{v} ({float(x):.3f})" for v, x in orden[:3])
            r.append(f"- {nombre}: {top}")
            if hay_empate:
                r.append(f"  * Hay empate en el corte del top 3: {', '.join(empatados)}")
        r.append("")
        # Empates generales
        r.append("EMPATES")
        for nombre, med in (("Grado", CD), ("Cercania", CC), ("Intermediacion", CB)):
            grupos = {}
            for v, x in med.items():
                grupos.setdefault(x, []).append(v)
            emp = [g for g in grupos.values() if len(g) > 1]
            if emp:
                r.append(f"- {nombre}: " + "; ".join(",".join(g) for g in emp))
            else:
                r.append(f"- {nombre}: sin empates")
        mejor = max(CB, key=lambda v: (CB[v], -ord(v)))
        r.append("")
        r.append(f"Principal intermediario: {mejor}  (CB = {float(CB[mejor]):.3f}, "
                 f"C'B = {float(CBn[mejor]):.3f})")
        self.txt_resp.delete("1.0", "end")
        self.txt_resp.insert("end", "\n".join(r))


if __name__ == "__main__":
    App().mainloop()