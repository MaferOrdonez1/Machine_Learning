import pyodbc
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from collections import Counter

# Configuración de colores y estilos
BACKGROUND_COLOR = "#2C3E50"
FRAME_COLOR = "#34495E"
TEXT_COLOR = "#000000"  # Negro
BUTTON_COLOR = "#2980B9"
ENTRY_COLOR = "#FFFFFF"  # Fondo blanco para los campos de entrada
TITLE_FONT = ("Helvetica", 14, "bold")
LABEL_FONT = ("Helvetica", 12)
ENTRY_FONT = ("Helvetica", 12)

# Clase Regla
class Regla:
    def __init__(self, genero: str, condiciones: set, categorias: str, conclusion: str):
        self.genero = genero
        self.condiciones = condiciones
        self.categorias = categorias
        self.conclusion = conclusion

# Conectar a la base de datos
def conectar_base_datos():
    return pyodbc.connect(
        r'DRIVER=SQL Server;'
        r'SERVER=DESKTOP-J9H4PGR\MSSQLSERVER01;'
        r'DATABASE=SistemasExpertosDB;'
        r'UID=sa;'
        r'PWD=Everise$2024.;'
    )

# Obtener reglas de la base de datos
def obtener_reglas():
    with conectar_base_datos() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT genero, condiciones, categorias, conclusion FROM Reglas")
        
        reglas = []
        generos_disponibles = set()
        
        for row in cursor.fetchall():
            genero = row.genero.strip().lower()
            generos_disponibles.add(genero)
            condiciones = set(row.condiciones.split(', '))
            categorias = row.categorias.strip().lower()
            conclusion = row.conclusion
            reglas.append(Regla(genero, condiciones, categorias, conclusion))
    
    return reglas, generos_disponibles

# Agregar nueva regla
def agregar_regla(genero, condiciones, categorias, conclusion):
    with conectar_base_datos() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Reglas (genero, condiciones, categorias, conclusion) VALUES (?, ?, ?, ?)",
            genero, condiciones, categorias, conclusion)
        conn.commit()
    cargar_generos()

# Encadenamiento hacia adelante
def encadenamiento_hacia_adelante(hechos: set, reglas: list, genero_seleccionado: str) -> set:
    conclusiones = set()
    nuevo_hecho_agregado = True

    while nuevo_hecho_agregado:
        nuevo_hecho_agregado = False
        for regla in reglas:
            if regla.genero == genero_seleccionado and regla.condiciones.issubset(hechos):
                if regla.conclusion not in hechos:
                    hechos.add(regla.conclusion)
                    conclusiones.add(regla.conclusion)
                    nuevo_hecho_agregado = True

    return conclusiones

# Mostrar recomendaciones
def mostrar_recomendaciones():
    genero = listbox_generos.get(listbox_generos.curselection()).strip().lower() 
    duracion = duracion_var.get().strip().lower()
    categoria = categoria_var.get().strip().lower()

    hechos = {genero, duracion, categoria}
    reglas, _ = obtener_reglas()
    recomendaciones = encadenamiento_hacia_adelante(hechos.copy(), reglas, genero)

    text_area.delete("1.0", tk.END) 
    if recomendaciones:
        resultado = "\n".join(recomendaciones)
        text_area.insert(tk.END, f"Te recomendamos ver las siguientes películas:\n{resultado}")
    else:
        text_area.insert(tk.END, "No se encontraron recomendaciones basadas en tus preferencias.")

# Generar histograma de categorías
def generar_histograma_categorias():
    reglas, _ = obtener_reglas()
    categorias_recomendadas = Counter([regla.categorias for regla in reglas])
    
    if not categorias_recomendadas:
        messagebox.showinfo("Información", "No hay datos suficientes para generar el histograma.")
        return
    
    labels = list(categorias_recomendadas.keys())
    values = list(categorias_recomendadas.values())
    
    plt.bar(labels, values, color=['#2980B9', '#2ECC71', '#9B59B6', '#F1C40F'])
    plt.xlabel('Categoría')
    plt.ylabel('Cantidad de Películas')
    plt.title('Distribución de Películas por Categoría')
    plt.show()

# Generar histograma de géneros
def generar_histograma_generos():
    reglas, _ = obtener_reglas()
    generos_recomendados = Counter([regla.genero for regla in reglas])
    
    if not generos_recomendados:
        messagebox.showinfo("Información", "No hay datos suficientes para generar el histograma.")
        return
    
    labels = list(generos_recomendados.keys())
    values = list(generos_recomendados.values())
    
    plt.bar(labels, values, color='#9B59B6')
    plt.xlabel('Género')
    plt.ylabel('Cantidad de Recomendaciones')
    plt.title('Recomendaciones por Género')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Agregar nueva regla
def agregar_nueva_regla():
    genero = genero_nuevo.get().strip().lower()
    condiciones = condiciones_nuevas.get().strip().lower()
    categorias = categoria_nueva.get().strip().lower()
    conclusion = conclusion_nueva.get().strip().lower()
    
    if genero and condiciones and categorias and conclusion:
        agregar_regla(genero, condiciones, categorias, conclusion)
        messagebox.showinfo("Éxito", "Regla añadida exitosamente.")
    else:
        messagebox.showwarning("Advertencia", "Por favor, completa todos los campos.")

# Cargar géneros disponibles
def cargar_generos():
    listbox_generos.delete(0, tk.END)
    _, generos_disponibles = obtener_reglas()
    for genero in generos_disponibles:
        listbox_generos.insert(tk.END, genero.capitalize())

# GUI con tkinter
root = tk.Tk()
root.title("Sistema Experto de Recomendación de Películas")
root.geometry("800x600")
root.configure(bg=BACKGROUND_COLOR)

# Configurar estilos
style = ttk.Style()
style.theme_use('clam')
style.configure("Custom.TEntry", background=ENTRY_COLOR, foreground=TEXT_COLOR)

notebook = ttk.Notebook(root)
tab_recomendaciones = ttk.Frame(notebook)
tab_agregar_reglas = ttk.Frame(notebook)
tab_estadisticas = ttk.Frame(notebook)

notebook.add(tab_recomendaciones, text="Recomendaciones")
notebook.add(tab_agregar_reglas, text="Agregar Regla")
notebook.add(tab_estadisticas, text="Estadísticas")
notebook.pack(expand=True, fill="both", padx=10, pady=10)

# Pestaña Recomendaciones
duracion_var = tk.StringVar()
categoria_var = tk.StringVar()

ttk.Label(tab_recomendaciones, text="Géneros disponibles:", foreground="#000000", font=LABEL_FONT).grid(row=0, column=0, pady=10)
listbox_generos = tk.Listbox(tab_recomendaciones, height=5, width=30, font=ENTRY_FONT, bg=ENTRY_COLOR, fg=TEXT_COLOR)
listbox_generos.grid(row=0, column=1, pady=10)

ttk.Label(tab_recomendaciones, text="Duración (corta/larga):", foreground="#000000", font=LABEL_FONT).grid(row=1, column=0, pady=10)
ttk.Entry(tab_recomendaciones, textvariable=duracion_var, style="Custom.TEntry").grid(row=1, column=1, pady=10)

ttk.Label(tab_recomendaciones, text="Categoría:", foreground="#000000", font=LABEL_FONT).grid(row=2, column=0, pady=10)
ttk.Entry(tab_recomendaciones, textvariable=categoria_var, style="Custom.TEntry").grid(row=2, column=1, pady=10)

button_recommend = ttk.Button(tab_recomendaciones, text="Mostrar Recomendaciones", command=mostrar_recomendaciones)
button_recommend.grid(row=3, column=0, columnspan=2, pady=10)

text_area = tk.Text(tab_recomendaciones, height=10, width=50, bg=ENTRY_COLOR, fg=TEXT_COLOR)
text_area.grid(row=4, column=0, columnspan=2, pady=10)

# Pestaña Agregar Reglas
frame_agregar = ttk.LabelFrame(tab_agregar_reglas, text="Agregar Nueva Regla", padding=(10, 10))
frame_agregar.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

ttk.Label(frame_agregar, text="Género:", font=LABEL_FONT).grid(row=0, column=0, pady=5, padx=5, sticky="w")
genero_nuevo = ttk.Entry(frame_agregar, style="Custom.TEntry", width=30)
genero_nuevo.grid(row=0, column=1, pady=5, padx=5)

ttk.Label(frame_agregar, text="Condiciones:", font=LABEL_FONT).grid(row=1, column=0, pady=5, padx=5, sticky="w")
condiciones_nuevas = ttk.Entry(frame_agregar, style="Custom.TEntry", width=30)
condiciones_nuevas.grid(row=1, column=1, pady=5, padx=5)

ttk.Label(frame_agregar, text="Categorías:", font=LABEL_FONT).grid(row=2, column=0, pady=5, padx=5, sticky="w")
categoria_nueva = ttk.Entry(frame_agregar, style="Custom.TEntry", width=30)
categoria_nueva.grid(row=2, column=1, pady=5, padx=5)

ttk.Label(frame_agregar, text="Conclusión:", font=LABEL_FONT).grid(row=3, column=0, pady=5, padx=5, sticky="w")
conclusion_nueva = ttk.Entry(frame_agregar, style="Custom.TEntry", width=30)
conclusion_nueva.grid(row=3, column=1, pady=5, padx=5)

button_add_rule = ttk.Button(frame_agregar, text="Agregar Regla", command=agregar_nueva_regla)
button_add_rule.grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")

# Pestaña Estadísticas
ttk.Label(tab_estadisticas, text="Generar Histogramas:", font=TITLE_FONT).pack(pady=10)
button_histogram_categorias = ttk.Button(tab_estadisticas, text="Histograma de Categorías", command=generar_histograma_categorias)
button_histogram_categorias.pack(pady=10)

button_histogram_generos = ttk.Button(tab_estadisticas, text="Histograma de Géneros", command=generar_histograma_generos)
button_histogram_generos.pack(pady=10)

cargar_generos()
root.mainloop()
