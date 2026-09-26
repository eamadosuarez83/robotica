"""Romperlo a proposito: calcular la inercia de un eslabon respecto a
su extremo SIN Steiner (usando por error I_cm directamente) y
comparar con el valor correcto (Bloque 06, Tema 6.3).

Correr con:
    python codigo/bloque_06/romper_sin_steiner.py
"""


def main() -> None:
    m = 0.3    # kg
    L = 0.4    # m, varilla uniforme

    I_cm = m * L**2 / 12          # momento de inercia respecto al centro
    d = L / 2                     # distancia del centro al extremo

    I_extremo_correcto = I_cm + m * d**2      # Steiner
    I_extremo_incorrecto = I_cm               # error clásico: olvidar Steiner

    print(f"I_cm                          = {I_cm:.6f} kg·m²")
    print(f"I_extremo (correcto, Steiner) = {I_extremo_correcto:.6f} kg·m²")
    print(f"I_extremo (incorrecto, sin Steiner) = {I_extremo_incorrecto:.6f} kg·m²")
    print(f"Factor de error: {I_extremo_correcto/I_extremo_incorrecto:.2f}x "
          f"(el valor correcto es {I_extremo_correcto/I_extremo_incorrecto:.0f} "
          f"veces el incorrecto para una varilla uniforme)")

    # Consecuencia física: un motor dimensionado con el valor incorrecto
    # aplicaría menos par del que realmente hace falta para la misma
    # aceleración angular deseada.
    alfa_deseada = 5.0  # rad/s²
    tau_incorrecto = I_extremo_incorrecto * alfa_deseada
    tau_correcto = I_extremo_correcto * alfa_deseada
    print(f"\nPar pedido al motor (incorrecto): {tau_incorrecto:.4f} N·m")
    print(f"Par realmente necesario (correcto): {tau_correcto:.4f} N·m")
    print("Con el valor incorrecto, el motor se queda corto y el eslabón "
          "acelera más lento de lo esperado.")


if __name__ == "__main__":
    main()
