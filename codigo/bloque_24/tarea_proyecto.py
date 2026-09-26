"""Entregables 5 y 7 del proyecto integrador: generador de
trayectorias validado en simulacion (Bloque 19) y la tarea completa
como maquina de estados con registro de eventos (Bloque 23), sobre
prototipo_4gdl.

Los angulos de cada punto de enseñanza se resuelven UNA vez con
inversa_numerica (Bloque 12; este brazo de 4 GDL espacial no tiene
una inversa geometrica cerrada como el 3R plano de los Bloques
12/19/23) y se reutilizan para no recalcular en cada ciclo.

Correr con:
    python codigo/bloque_24/tarea_proyecto.py
"""

import sys
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.dh import directa  # noqa: E402
from robotica.inversa import inversa_numerica  # noqa: E402
from robotica.trayectorias import perfil_trapezoidal  # noqa: E402
from modelo_proyecto import DH  # noqa: E402

PUNTOS_CARTESIANOS = {
    "reposo": [0.15, 0.00, 0.10],
    "aprox_recoger": [0.20, 0.10, 0.00],
    "recoger": [0.20, 0.10, -0.04],
    "aprox_depositar": [0.15, -0.15, 0.05],
    "depositar": [0.15, -0.15, -0.02],
}


def resolver_puntos_de_enseñanza():
    """Entregable 5, primera parte: resuelve la cinemática inversa de
    cada punto de enseñanza UNA vez (Bloque 12)."""
    q_ref = np.zeros(4)
    q_puntos = {}
    for nombre, p in PUNTOS_CARTESIANOS.items():
        q, conv = inversa_numerica(DH, p, q_ref, metodo="amortiguado", max_iter=3000)
        assert conv, f"'{nombre}' no convergió"
        p_check = directa(DH, q)[:3, 3]
        assert np.linalg.norm(np.array(p) - p_check) < 1e-4
        q_puntos[nombre] = q
        q_ref = q
    return q_puntos


Q_PUNTOS = resolver_puntos_de_enseñanza()


def generar_trayectoria(nombre_a, nombre_b, V=np.radians(60), a=np.radians(120), n_puntos=10):
    """Entregable 5: trayectoria articular sincronizada entre dos
    puntos de enseñanza -- cada articulación con su propio perfil
    trapezoidal (Bloque 19), sincronizadas a la más lenta (Bloque 23,
    Tema 23.5). Devuelve (Q, duración), con Q de forma (n_puntos, 4)."""
    qa, qb = Q_PUNTOS[nombre_a], Q_PUNTOS[nombre_b]
    perfiles = [perfil_trapezoidal(q0, q1, V=V, a=a, n_puntos=n_puntos) for q0, q1 in zip(qa, qb)]
    duracion = max(t[-1] for t, _, _, _ in perfiles)
    Q = np.column_stack([q for _, q, _, _ in perfiles])
    return Q, duracion


# --------------------------------------------------------- Entregable 7

class Estado(Enum):
    ESPERANDO = auto()
    APROXIMAR_RECOGER = auto()
    RECOGER = auto()
    LEVANTAR = auto()
    TRASLADAR = auto()
    DEJAR = auto()
    REGRESAR = auto()
    ERROR = auto()
    TERMINADO = auto()


@dataclass
class Evento:
    t: float
    estado: str
    mensaje: str


@dataclass
class TareaProyecto:
    prob_objeto_no_encontrado: float = 0.0
    prob_fallo_agarre: float = 0.0
    rng: np.random.Generator = field(default_factory=lambda: np.random.default_rng())

    def __post_init__(self):
        self.eventos: list[Evento] = []
        self._t0 = time.perf_counter()
        self.punto_actual = "reposo"

    def _log(self, estado, mensaje):
        self.eventos.append(Evento(time.perf_counter() - self._t0, estado.name, mensaje))

    def _mover_a(self, estado, destino):
        Q, duracion = generar_trayectoria(self.punto_actual, destino)
        p_final = directa(DH, Q[-1])[:3, 3]
        objetivo = np.array(PUNTOS_CARTESIANOS[destino])
        if np.linalg.norm(p_final - objetivo) > 1e-3:
            self._log(estado, f"movimiento a '{destino}' no llegó al objetivo")
            return False
        self.punto_actual = destino
        self._log(estado, f"llegó a '{destino}' ({Q.shape[0]} puntos, {duracion:.2f} s nominal)")
        return True

    def ejecutar_ciclo(self) -> bool:
        self._log(Estado.ESPERANDO, "esperando objeto en la banda")

        if not self._mover_a(Estado.APROXIMAR_RECOGER, "aprox_recoger"):
            return False

        if self.rng.random() < self.prob_objeto_no_encontrado:
            self._log(Estado.ERROR, "objeto no encontrado")
            return False
        if not self._mover_a(Estado.RECOGER, "recoger"):
            return False
        if self.rng.random() < self.prob_fallo_agarre:
            self._log(Estado.ERROR, "fallo de agarre")
            return False
        self._log(Estado.RECOGER, "agarre exitoso")

        if not self._mover_a(Estado.LEVANTAR, "aprox_recoger"):
            return False
        if not self._mover_a(Estado.TRASLADAR, "aprox_depositar"):
            return False
        if not self._mover_a(Estado.DEJAR, "depositar"):
            return False
        self._log(Estado.DEJAR, "huevo depositado en la cubeta")
        if not self._mover_a(Estado.REGRESAR, "reposo"):
            return False

        self._log(Estado.TERMINADO, "ciclo completado")
        return True


def main() -> None:
    print("=== Entregable 5: trayectorias entre puntos de enseñanza ===")
    for nombre, q in Q_PUNTOS.items():
        p = directa(DH, q)[:3, 3]
        print(f"  {nombre:16s} q={np.round(np.degrees(q),1)}°  p={np.round(p,4)} m")

    Q, dur = generar_trayectoria("reposo", "aprox_recoger")
    print(f"\nTrayectoria reposo -> aprox_recoger: {Q.shape[0]} puntos, {dur:.3f} s nominal")

    print("\n=== Entregable 7: tarea completa como máquina de estados ===")
    tarea = TareaProyecto(rng=np.random.default_rng(0))
    exito = tarea.ejecutar_ciclo()
    for e in tarea.eventos:
        print(f"  [{e.t*1000:6.2f} ms cómputo] {e.estado:20s} {e.mensaje}")
    print(f"Resultado: {'éxito' if exito else 'FALLO'}")

    print("\n200 ciclos con probabilidad de error:")
    rng = np.random.default_rng(1)
    exitos = sum(TareaProyecto(prob_objeto_no_encontrado=0.03, prob_fallo_agarre=0.05,
                                rng=rng).ejecutar_ciclo() for _ in range(200))
    print(f"  Éxitos: {exitos}/200")


if __name__ == "__main__":
    main()
