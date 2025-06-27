import tkinter as tk
from tkinter import scrolledtext
import threading
import time
import random
import matplotlib.pyplot as plt

# --- Algorytm genetyczny ---

# Funkcja generująca listę przedmiotów z losowymi wagami i wartościami w podanych zakresach
def gen_items(n, min_w, max_w, min_v, max_v):
    return [{'weight': random.randint(min_w, max_w), 'value': random.randint(min_v, max_v)} for _ in range(n)]

# Funkcja generująca osobnika (listę bitów 0 lub 1)
def gen_ind(n):
    return [random.randint(0, 1) for _ in range(n)]

# Funkcja inicjująca populację osobników
def ini_pop(n_items):
    return [gen_ind(n_items) for _ in range(pop_size)]

# Funkcja oceniająca wartość osobnika; jeśli przekracza wagę, zwraca 0
def check_weight(individual, items, max_weight):
    total_weight = total_value = 0
    for i in range(len(individual)):
        if individual[i] == 1:
            total_weight += items[i]['weight']
            total_value += items[i]['value']
    return total_value if total_weight <= max_weight else 0

# Turniej — wybór najlepszego z losowych osobników
def tournament(population, items, max_weight):
    selected = random.sample(population, tournament_size)
    return max(selected, key=lambda ind: check_weight(ind, items, max_weight))

# Krzyżowanie dwóch osobników w jednym punkcie
def crossover(parent1, parent2):
    point = random.randint(1, len(parent1) - 2)
    return parent1[:point] + parent2[point:]


# Mutacja osobnika — zmiana bitu z prawdopodobieństwem mutation_rate
def mutate(individual):
    return [1 - gene if random.random() < mutation_rate else gene for gene in individual]

# Główna funkcja ewolucji populacji przez określoną liczbę pokoleń
def evolution(items, max_weight):
    population = ini_pop(len(items))
    best = population[0]
    best_check_weights = []

    for _ in range(generations):
        new_population = []
        for _ in range(pop_size):
            p1 = tournament(population, items, max_weight)
            p2 = tournament(population, items, max_weight)
            child = mutate(crossover(p1, p2))
            new_population.append(child)
        population = new_population
        current_best = max(population, key=lambda ind: check_weight(ind, items, max_weight))
        if check_weight(current_best, items, max_weight) > check_weight(best, items, max_weight):
            best = current_best
        best_check_weights.append(check_weight(best, items, max_weight))
    return best, best_check_weights

# Rysowanie wykresu postępu
def plot_progress(check_weightes):
    plt.plot(check_weightes)
    plt.xlabel('Pokolenie')
    plt.ylabel('Najlepsza wartość')
    plt.title('Postęp algorytmu')
    plt.grid(True)
    plt.show()

# --- GUI ---
root = tk.Tk()
root.title("Projekt 17 - Adrian Gwiazdowski")
root.geometry("800x750")

frame_inputs = tk.LabelFrame(root, text="Parametry algorytmu", padx=10, pady=10)
frame_inputs.pack(fill="x", padx=10, pady=5)

# Pomocnicza funkcja do dodawania pól wejściowych
def add_entry(label, row, default):
    tk.Label(frame_inputs, text=label).grid(row=row, column=0, sticky='e')
    entry = tk.Entry(frame_inputs)
    entry.insert(0, str(default))
    entry.grid(row=row, column=1, padx=5, pady=2, sticky='w')
    return entry

entry_pop = add_entry("Rozmiar populacji:", 0, 150)
entry_items = add_entry("Liczba przedmiotów:", 1, 100)
entry_weight = add_entry("Maksymalna waga:", 2, 500)
entry_gen = add_entry("Liczba generacji:", 3, 500)
entry_mut = add_entry("Mutacja (0-1):", 4, 0.0125)
entry_tour = add_entry("Rozmiar turnieju:", 5, 5)
entry_min_weight = add_entry("Min waga:", 6, 1)
entry_max_weight = add_entry("Max waga:", 7, 30)
entry_min_value = add_entry("Min wartość:", 8, 10)
entry_max_value = add_entry("Max wartość:", 9, 100)
use_seed_var = tk.IntVar()
tk.Checkbutton(frame_inputs, text="Użyj seed:", variable=use_seed_var).grid(row=10, column=0, sticky='e')

entry_seed = tk.Entry(frame_inputs)
entry_seed.insert(0, "10")
entry_seed.grid(row=10, column=1, padx=5, pady=2, sticky='w')


frame_output = tk.LabelFrame(root, text="Wyniki", padx=10, pady=10)
frame_output.pack(fill="both", expand=True, padx=10, pady=5)

frame_output.columnconfigure(0, weight=1)
frame_output.columnconfigure(1, weight=1)

tk.Label(frame_output, text="Przedmioty:").grid(row=0, column=0, sticky='w')
item_text = scrolledtext.ScrolledText(frame_output, width=40, height=20)
item_text.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

tk.Label(frame_output, text="Najlepsze rozwiązanie:").grid(row=0, column=1, sticky='w')
result_text = scrolledtext.ScrolledText(frame_output, width=40, height=20)
result_text.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

frame_bottom = tk.Frame(root)
frame_bottom.pack(fill="x", padx=10, pady=10)

status_label = tk.Label(frame_bottom, text="Status: Gotowy", fg="green")
status_label.pack(side="left")

run_button = tk.Button(frame_bottom, text="Uruchom algorytm", width=20)
run_button.pack(side="right")

# Funkcja uruchamiająca algorytm
def run_algorithm():
    try:
        global pop_size, item_count, max_weight, generations, mutation_rate, tournament_size
        pop_size = int(entry_pop.get())
        item_count = int(entry_items.get())
        max_weight = int(entry_weight.get())
        generations = int(entry_gen.get())
        mutation_rate = float(entry_mut.get())
        tournament_size = int(entry_tour.get())
    except ValueError:
        status_label.config(text="Status: Błąd danych wejściowych!", fg="red")
        return

    def target():
        status_label.config(text="Status: Pracuję...", fg="blue")
        start_time = time.time()
        if use_seed_var.get():
            try:
                seed_value = int(entry_seed.get())
                random.seed(seed_value)
            except ValueError:
                status_label.config(text="Status: Błąd w seedzie!", fg="red")
                return
        else:
            random.seed()
        item_text.delete("1.0", tk.END)
        result_text.delete("1.0", tk.END)

        try:
            min_w = int(entry_min_weight.get())
            max_w = int(entry_max_weight.get())
            min_v = int(entry_min_value.get())
            max_v = int(entry_max_value.get())
            if min_w > max_w or min_v > max_v:
                raise ValueError("Błędny zakres wag lub wartości.")
        except ValueError as e:
            status_label.config(text=f"Status: Błąd zakresów - {e}", fg="red")
            return

        items = gen_items(item_count, min_w, max_w, min_v, max_v)

        for i, item in enumerate(items):
            item_text.insert(tk.END, f"{i+1}. Waga: {item['weight']}, Wartość: {item['value']}\n")

        best_solution, progress = evolution(items, max_weight)

        total_weight = 0
        total_value = 0
        selected_items = []

        for i in range(len(best_solution)):
            if best_solution[i] == 1:
                total_weight += items[i]['weight']
                total_value += items[i]['value']
                selected_items.append(i + 1)

        execution_time = time.time() - start_time
        result_text.insert(tk.END, f"Całkowita wartość: {total_value}\n")
        result_text.insert(tk.END, f"Całkowita waga: {total_weight}\n")
        result_text.insert(tk.END, f"Wybrane przedmioty: {selected_items}\n")
        result_text.insert(tk.END, f"Czas wykonania: {execution_time:.2f} s\n")

        status_label.config(text="Status: Gotowy", fg="green")
        root.after(0, lambda: plot_progress(progress))

    threading.Thread(target=target).start()

run_button.config(command=run_algorithm)

root.mainloop()
