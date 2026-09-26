"""Tarea de recoger y dejar (pick and place) como maquina de estados,
sobre curso_3gdl, con manejo de errores y registro de eventos
(Bloque 23, Temas 23.3 y 23.4).

Correr con:
    python codigo/bloque_23/tarea_recoger_dejar.py
"""

import sys
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.inversa import inv_3r_geometrica  # noqa: E402
from robotica.trayectorias import linea, resolver_trayectoria  # noqa: E402

L1, L2, L3 = 0.15, 0.12, 0.10


def inversa(px, py, pz):
    return inv_3r_geometrica(px, py, pz, L1, L2, L3)


# Puntos de enseñanza (Bloque 23, Tema 23.2): posiciones cartesianas
# fijas, cada una ya verificada como alcanzable.
PUNTOS = {
    "reposo": np.array([0.10, 0.00, 0.20]),
    "aprox_recoger": np.array([0.18, 0.05, 0.13]),
    "recoger": np.array([0.18, 0.05, 0.09]),
    "aprox_depositar": np.array([0.10, -0.15, 0.13]),
    "depositar": np.array([0.10, -0.15, 0.09]),
}


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
class Tarea:
    prob_objeto_no_encontrado: float = 0.0
    prob_fallo_agarre: float = 0.0
    n_puntos_por_tramo: int = 8
    rng: np.random.Generator = field(default_factory=lambda: np.random.default_rng())

    def __post_init__(self):
        self.estado = Estado.ESPERANDO
        self.eventos: list[Evento] = []
        self._t0 = time.perf_counter()

    def _log(self, mensaje):
        t = time.perf_counter() - self._t0
        self.eventos.append(Evento(t, self.estado.name, mensaje))

    def _mover_a(self, nombre_destino):
        p_actual = PUNTOS[self.punto_actual]
        p_destino = PUNTOS[nombre_destino]
        puntos = linea(p_actual, p_destino, self.n_puntos_por_tramo)
        resultado = resolver_trayectoria(puntos, inversa)
        if not resultado.ok:
            self._log(f"movimiento a '{nombre_destino}' falló: {resultado.estado}")
            return False
        self.punto_actual = nombre_destino
        self._log(f"llegó a '{nombre_destino}' ({resultado.Q.shape[0]} puntos)")
        return True

    def ejecutar_ciclo(self) -> bool:
        """Ejecuta un ciclo completo de recoger-y-dejar. Devuelve True
        si terminó con éxito, False si abortó por un error."""
        self.punto_actual = "reposo"
        self.estado = Estado.ESPERANDO
        self._log("esperando objeto en la banda")

        self.estado = Estado.APROXIMAR_RECOGER
        if not self._mover_a("aprox_recoger"):
            self.estado = Estado.ERROR
            return False

        self.estado = Estado.RECOGER
        if self.rng.random() < self.prob_objeto_no_encontrado:
            self._log("objeto no encontrado en la posición esperada")
            self.estado = Estado.ERROR
            return False
        if not self._mover_a("recoger"):
            self.estado = Estado.ERROR
            return False
        if self.rng.random() < self.prob_fallo_agarre:
            self._log("fallo de agarre: la pinza cerró sin sujetar el huevo")
            self.estado = Estado.ERROR
            return False
        self._log("agarre exitoso")

        self.estado = Estado.LEVANTAR
        if not self._mover_a("aprox_recoger"):
            self.estado = Estado.ERROR
            return False

        self.estado = Estado.TRASLADAR
        if not self._mover_a("aprox_depositar"):
            self.estado = Estado.ERROR
            return False

        self.estado = Estado.DEJAR
        if not self._mover_a("depositar"):
            self.estado = Estado.ERROR
            return False
        self._log("huevo depositado en la cubeta")

        self.estado = Estado.REGRESAR
        if not self._mover_a("reposo"):
            self.estado = Estado.ERROR
            return False

        self.estado = Estado.TERMINADO
        self._log("ciclo completado")
        return True


def main() -> None:
    print("=== Ciclo sin errores ===")
    tarea = Tarea(rng=np.random.default_rng(0))
    exito = tarea.ejecutar_ciclo()
    for e in tarea.eventos:
        print(f"  [{e.t*1000:6.2f} ms] {e.estado:20s} {e.mensaje}")
    print(f"Resultado: {'éxito' if exito else 'FALLO'}, "
          f"tiempo total: {tarea.eventos[-1].t*1000:.2f} ms\n")

    print("=== 200 ciclos con probabilidad de error (Tema 23.4) ===")
    rng = np.random.default_rng(1)
    exitos, fallos_agarre, fallos_objeto = 0, 0, 0
    for _ in range(200):
        tarea = Tarea(prob_objeto_no_encontrado=0.03, prob_fallo_agarre=0.05, rng=rng)
        if tarea.ejecutar_ciclo():
            exitos += 1
        else:
            ultimo = tarea.eventos[-1].mensaje
            if "no encontrado" in ultimo:
                fallos_objeto += 1
            elif "agarre" in ultimo:
                fallos_agarre += 1
    print(f"Éxitos: {exitos}/200, fallos por objeto no encontrado: {fallos_objeto}, "
          f"fallos de agarre: {fallos_agarre}")


if __name__ == "__main__":
    main()
