import tkinter as tk
from tkinter import messagebox
import serial
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Konfiguracja połączenia z Arduino
ser = serial.Serial('/dev/pts/7', 9600, timeout=1)
time.sleep(1)  # Czas na inicjalizację połączenia

# Zmienne
ph_samples = []
sample_size = 10
target_ph = 7.0
ph_sensor_tolerance = 0.5
pump_active = False
measurement_interval = 0.5
pump_duration = 5
allow_pump_activation = True
running = True

# Funkcja do odczytu danych z Arduino
def read_serial():
    global ph_samples
    while running:
        if ser.in_waiting > 0:
            try:
                line = ser.readline().decode('utf-8').strip()
                # print("Serial: " + line)

                if line.startswith("PH:"):
                    ph_value = float(line.split(":")[1].strip())
                    ph_samples.append(ph_value)
                    if len(ph_samples) > sample_size:
                        ph_samples.pop(0)

                    root.after(0, update_ph_display)
                    root.after(0, update_graph)

            except Exception as e:
                print(f"Błąd odczytu: {e}")
        time.sleep(measurement_interval)

# Aktualizacja wyświetlanego pH
def update_ph_display():
    avg_ph = sum(ph_samples) / len(ph_samples) if ph_samples else 0
    current_ph_label.config(text=f"Aktualne pH: {avg_ph:.2f}")
    if abs(avg_ph - target_ph) > ph_sensor_tolerance and allow_pump_activation:
        activate_pump()

# Funkcja do zmiany docelowego pH
def set_target_ph():
    global target_ph
    try:
        target_ph = float(target_ph_entry.get())
        messagebox.showinfo("Zmiana pH", f"Docelowe pH ustawione na {target_ph}")
    except ValueError:
        messagebox.showerror("Błąd", "Wprowadź poprawną wartość pH")

def update_pump_status():
    if pump_active:
        pump_status_label.config(text="Pompa: Aktywna", bg="green")
    else:
        pump_status_label.config(text="Pompa: Nieaktywna", bg="gray")

# Funkcja obsługująca pompę
def pump_water():
    global pump_active
    pump_active = True
    update_pump_status()
    time.sleep(pump_duration)
    pump_active = False
    update_pump_status()

# Aktywacja pompy
def activate_pump():
    if pump_active:
        return
    print("Aktywuje pompę")
    thread = threading.Thread(target=pump_water, daemon=True)
    thread.start()

# Aktualizacja wykresu
def update_graph():
    avg_ph = sum(ph_samples) / len(ph_samples) if ph_samples else 0
    ph_data.append(avg_ph)
    if len(ph_data) > 100:
        ph_data.pop(0)

    ax.clear()
    ax.axhspan(target_ph - ph_sensor_tolerance, target_ph + ph_sensor_tolerance, color='green', alpha=0.2, label="Bezpieczny zakres")
    ax.plot(ph_data, label="pH", color="blue")
    ax.set_title("Zmienność pH")
    ax.set_xlabel("Czas")
    ax.set_ylabel("pH")
    ax.legend(loc="best")
    canvas.draw()

# Resetowanie ustawień do domyślnych
def reset_settings():
    global target_ph, ph_sensor_tolerance, sample_size
    target_ph = 2.0
    ph_sensor_tolerance = 0.5
    sample_size = 10
    target_ph_entry.delete(0, tk.END)
    target_ph_entry.insert(0, target_ph)
    messagebox.showinfo("Reset", "Ustawienia przywrócone do domyślnych.")

# Kalibracja czujnika pH
def calibrate_sensor():
    ser.write(b'CALIBRATE\n')  # Komenda do Arduino
    messagebox.showinfo("Kalibracja", "Kalibracja czujnika pH została rozpoczęta.")

# Aktualizacja stanu połączenia
def check_connection():
    if ser.is_open:
        connection_status_label.config(text="Połączenie: Aktywne", bg="green")
        connection_lamp.delete("all")
        connection_lamp.create_oval(10, 10, 40, 40, fill="green", outline="")
    else:
        connection_status_label.config(text="Połączenie: Brak", bg="red")
        connection_lamp.delete("all")
        connection_lamp.create_oval(10, 10, 40, 40, fill="red", outline="")
    root.after(100, check_connection)

# Funkcja do zmiany czasu pomiaru
def set_measurement_interval():
    global measurement_interval
    try:
        measurement_interval = float(measurement_interval_entry.get())
        messagebox.showinfo("Zmiana interwału", f"Interwał pomiaru ustawiony na {measurement_interval} sekundy")
    except ValueError:
        messagebox.showerror("Błąd", "Wprowadź poprawną wartość czasu pomiaru")

# Funkcja do zmiany czasu działania pompy
def set_pump_duration():
    global pump_duration
    try:
        pump_duration = float(pump_duration_entry.get())
        messagebox.showinfo("Zmiana czasu pompy", f"Czas działania pompy ustawiony na {pump_duration} sekundy")
    except ValueError:
        messagebox.showerror("Błąd", "Wprowadź poprawną wartość czasu działania pompy")

# Funkcja do zmiany liczby próbek w średniej
def set_sample_size():
    global sample_size
    try:
        sample_size = int(sample_size_entry.get())
        messagebox.showinfo("Zmiana liczby próbek", f"Liczba próbek w średniej ustawiona na {sample_size}")
    except ValueError:
        messagebox.showerror("Błąd", "Wprowadź poprawną wartość liczby próbek")

# Funkcja do zmiany tolerancji pH
def set_ph_tolerance():
    global ph_sensor_tolerance
    try:
        ph_sensor_tolerance = float(ph_tolerance_entry.get())
        messagebox.showinfo("Zmiana tolerancji", f"Tolerancja pH ustawiona na {ph_sensor_tolerance}")
    except ValueError:
        messagebox.showerror("Błąd", "Wprowadź poprawną wartość tolerancji")

# Funkcja do włączania/wyłączania pompy
def toggle_pump_activation():
    global allow_pump_activation
    allow_pump_activation = not allow_pump_activation
    pump_activation_button.config(text="Aktywacja pompy: Włączona" if allow_pump_activation else "Aktywacja pompy: Wyłączona")

# Tworzenie GUI
root = tk.Tk()
root.title("Stacja kontrolna pH")
root.geometry("900x750")

# Tworzymy ramki dla dwóch kolumn
frame_left = tk.Frame(root)
frame_left.pack(side="left", padx=20, pady=20)
frame_right = tk.Frame(root)
frame_right.pack(side="right", padx=20, pady=20)


# Etykieta aktualnego pH
current_ph_label = tk.Label(frame_left, text="Aktualne pH: --", font=("Arial", 16))
current_ph_label.pack(pady=10)


# Etykieta i pole do ustawienia docelowego pH
target_ph_frame = tk.Frame(frame_left)
target_ph_frame.pack(pady=10)
tk.Label(target_ph_frame, text="Docelowe pH:").pack(side="left")
target_ph_entry = tk.Entry(target_ph_frame, width=5)
target_ph_entry.insert(0, target_ph)
target_ph_entry.pack(side="left", padx=5)
set_ph_button = tk.Button(target_ph_frame, text="Ustaw", command=set_target_ph)
set_ph_button.pack(side="left")


# Lampka statusu pompy
pump_status_label = tk.Label(frame_left, text="Pompa: Nieaktywna", font=("Arial", 14), bg="gray", width=20)
pump_status_label.pack(pady=10)

pump_activation_button = tk.Button(frame_left, text="Aktywacja pompy: Włączona", command=toggle_pump_activation)
pump_activation_button.pack(pady=10)

# Przycisk do resetu ustawień
reset_button = tk.Button(frame_left, text="Resetuj ustawienia", command=reset_settings)
reset_button.pack(pady=10)

# Przycisk kalibracji czujnika
calibrate_button = tk.Button(frame_left, text="Kalibruj czujnik", command=calibrate_sensor)
calibrate_button.pack(pady=10)

# Status połączenia
connection_status_label = tk.Label(frame_left, text="Połączenie: Brak", font=("Arial", 14), bg="red", width=20)
connection_status_label.pack(pady=10)

# Lampka połączenia
connection_lamp = tk.Canvas(frame_left, width=50, height=50, bg="white", highlightthickness=0)
connection_lamp.pack(pady=10)

# Regulacje
control_frame = tk.Frame(frame_left)
control_frame.pack(pady=20)
tk.Label(control_frame, text="Czas pomiaru:").pack(side="left")
measurement_interval_entry = tk.Entry(control_frame, width=5)
measurement_interval_entry.insert(0, measurement_interval)
measurement_interval_entry.pack(side="left", padx=5)
set_measurement_button = tk.Button(control_frame, text="Ustaw", command=set_measurement_interval)
set_measurement_button.pack(side="left", padx=5)

control_frame_2 = tk.Frame(frame_left)
control_frame_2.pack(pady=20)
tk.Label(control_frame_2, text="Czas pompy:").pack(side="left")
pump_duration_entry = tk.Entry(control_frame_2, width=5)
pump_duration_entry.insert(0, pump_duration)
pump_duration_entry.pack(side="left", padx=5)
set_pump_duration_button = tk.Button(control_frame_2, text="Ustaw", command=set_pump_duration)
set_pump_duration_button.pack(side="left", padx=5)

control_frame_3 = tk.Frame(frame_left)
control_frame_3.pack(pady=20)
tk.Label(control_frame_3, text="Liczba próbek:").pack(side="left")
sample_size_entry = tk.Entry(control_frame_3, width=5)
sample_size_entry.insert(0, sample_size)
sample_size_entry.pack(side="left", padx=5)
set_sample_size_button = tk.Button(control_frame_3, text="Ustaw", command=set_sample_size)
set_sample_size_button.pack(side="left", padx=5)

control_frame_4 = tk.Frame(frame_left)
control_frame_4.pack(pady=20)
tk.Label(control_frame_4, text="Tolerancja pH:").pack(side="left")
ph_tolerance_entry = tk.Entry(control_frame_4, width=5)
ph_tolerance_entry.insert(0, ph_sensor_tolerance)
ph_tolerance_entry.pack(side="left", padx=5)
set_ph_tolerance_button = tk.Button(control_frame_4, text="Ustaw", command=set_ph_tolerance)
set_ph_tolerance_button.pack(side="left", padx=5)

fig, ax = plt.subplots(figsize=(5, 4))
ph_data = []
canvas = FigureCanvasTkAgg(fig, master=frame_right)
canvas.get_tk_widget().pack()

thread = threading.Thread(target=read_serial, daemon=True)
thread.start()

def on_closing():
    global running
    running = False
    ser.close()
    root.quit()

root.protocol("WM_DELETE_WINDOW", on_closing)

# Sprawdzenie stanu połączenia
check_connection()

root.mainloop()
