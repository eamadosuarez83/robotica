"""Simula un brazo con offset de calibracion desconocido y ruido de
medicion, y verifica un procedimiento de calibracion que lo recupera
(Bloque 22, Temas 22.3 y 22.4).

Correr con:
    python codigo/bloque_22/calibracion.py
"""

import numpy as np

# "Verdad de fondo" que el procedimiento de calibración debe descubrir,
# sin conocerla de antemano (Bloque 22, Tema 22.3).
OFFSET_REAL = np.radians([7.0, -3.0, 1.5])   # el problema que abre el bloque
SIGNO_REAL = np.array([1, 1, 1])


def medir_articulacion(idx, q_comandado, sigma_ruido=0.0, rng=None):
    """Simula la lectura del sensor de la articulación `idx` cuando se
    comanda `q_comandado` (rad), con el offset/signo reales y ruido
    gaussiano opcional (Tema 22.4)."""
    verdadero = SIGNO_REAL[idx] * q_comandado + OFFSET_REAL[idx]
    ruido = 0.0 if sigma_ruido == 0.0 else rng.normal(0, sigma_ruido)
    return verdadero + ruido


def calibrar_offset(idx, n_lecturas=1, sigma_ruido=0.0, rng=None):
    """Comanda la articulación a 0 y promedia `n_lecturas` para
    estimar el offset (Tema 22.3, y Tema 22.4 para el promediado)."""
    lecturas = [medir_articulacion(idx, 0.0, sigma_ruido, rng) for _ in range(n_lecturas)]
    return float(np.mean(lecturas))


def calibrar_signo(idx, delta=np.radians(10), sigma_ruido=0.0, rng=None):
    """Comanda un cambio pequeño conocido y compara el sentido del
    movimiento real contra el esperado (Tema 22.3)."""
    offset = calibrar_offset(idx, n_lecturas=5, sigma_ruido=sigma_ruido, rng=rng)
    medida = medir_articulacion(idx, delta, sigma_ruido, rng)
    movimiento_real = medida - offset
    return 1 if movimiento_real > 0 else -1


def main() -> None:
    rng = np.random.default_rng(0)

    print("=== Calibración de offset (sin ruido) ===")
    for i in range(3):
        offset_calibrado = calibrar_offset(i)
        error = np.degrees(abs(offset_calibrado - OFFSET_REAL[i]))
        print(f"  articulación {i}: offset real={np.degrees(OFFSET_REAL[i]):+.2f}°, "
              f"calibrado={np.degrees(offset_calibrado):+.2f}°, error={error:.2e}°")
        assert error < 1e-6

    print("\n=== Calibración de signo ===")
    for i in range(3):
        signo = calibrar_signo(i)
        print(f"  articulación {i}: signo real={SIGNO_REAL[i]}, detectado={signo}")
        assert signo == SIGNO_REAL[i]

    print("\n=== Efecto del ruido de medición (Tema 22.4) ===")
    sigma = np.radians(0.5)
    for n in (1, 5, 20, 100):
        offsets = [calibrar_offset(0, n_lecturas=n, sigma_ruido=sigma, rng=rng) for _ in range(50)]
        dispersión = np.degrees(np.std(offsets))
        print(f"  n_lecturas={n:3d}: desviación estándar del offset calibrado = {dispersión:.4f}°")

    print("\nA más lecturas promediadas, menor la dispersión (∝ 1/√n, Ejercicio A1).")


if __name__ == "__main__":
    main()
