# RUN THIS COMMAND BEFORE: > socat -d -d pty,raw,echo=0 pty,raw,echo=0

import serial
import time
import random


mu = 7          # Średnia (mean)
sigma = 0.5       # Odchylenie standardowe (standard deviation)

try:
    ser1 = serial.Serial('/dev/pts/3', 9600)  # Port 1 (wysyłanie)
    ser2 = serial.Serial('/dev/pts/7', 9600)  # Port 2 (odbieranie)

    while True:

        # Generowanie losowej liczby
        random_number = random.gauss(mu, sigma)
        ser1.write(b"PH: " + str(random_number).encode() + b"\n")

        # if ser2.in_waiting > 0:
        #     received_data = ser2.readline()
        #     print(random.randint(0, 100))
        #     print(f"Received data: {received_data.decode()}")
        # if ser1.in_waiting > 0:
        #     received_data = ser1.readline()
        #     print(f"Received data: {received_data.decode()}")
        
        time.sleep(0.001)

except KeyboardInterrupt:
    print("Program interrupted by user.")

finally:
    if ser1.is_open:
        ser1.close()
    if ser2.is_open:
        ser2.close()
    print("Ports closed.")
