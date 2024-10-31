import numpy as np
import random
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.optimizers import Adam

# Generamos datos para el juego de cartas
num_samples = 1000
x_train = np.random.randint(1, 14, size=(num_samples, 1))  # Cartas del jugador
y_train = (x_train >= 7).astype(int)  # Gana si la carta es 7 o mayor, pierde si es menor a 7

# Definimos el modelo
model = Sequential([
    Input(shape=(1,)),
    Dense(16, activation='relu'),
    Dense(8, activation='relu'),
    Dense(1, activation='sigmoid')
])

# Compilamos el modelo
model.compile(optimizer=Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])

# Entrenamos el modelo
model.fit(x_train, y_train, epochs=10, batch_size=32, verbose=1)

# Bucle interactivo
while True:
    try:
        user_input = int(input("Introduce el valor de tu carta (1-13) o 0 para salir: "))
        if user_input == 0:
            print("¡Gracias por jugar!")
            break
        if user_input < 1 or user_input > 13:
            print("Por favor, introduce un valor entre 1 y 13.")
            continue

        # Predicción del modelo para la carta del usuario
        test_card_user = np.array([[user_input]])
        prediction_user = model.predict(test_card_user)

        # La máquina elige una carta al azar
        machine_card = random.randint(1, 13)
        test_card_machine = np.array([[machine_card]])
        prediction_machine = model.predict(test_card_machine)

        # Resultados
        print(f"\nHas jugado una carta de valor {user_input}.")
        if prediction_user[0][0] >= 0.5:
            print(f"¡Ganaste con tu carta! (Probabilidad: {prediction_user[0][0]:.2f})")
        else:
            print(f"¡Perdiste con tu carta! (Probabilidad: {prediction_user[0][0]:.2f})")

        print(f"La máquina jugó una carta de valor {machine_card}.")
        if prediction_machine[0][0] >= 0.5:
            print(f"La máquina ganó con su carta! (Probabilidad: {prediction_machine[0][0]:.2f})")
        else:
            print(f"La máquina perdió con su carta! (Probabilidad: {prediction_machine[0][0]:.2f})")

    except ValueError:
        print("Entrada no válida. Por favor, introduce un número.")
