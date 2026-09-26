"""Carga el URDF de curso_3gdl en PyBullet y compara su cinematica
directa contra robotica.dh.directa (Bloque 11) y
roboticstoolbox.DHRobot (Bloque 21, Tema 21.5) -- triangulo de
verificacion con tres implementaciones independientes.

Correr con:
    python codigo/bloque_21/verificar_pybullet.py
"""

import sys
from pathlib import Path

import numpy as np
import pybullet as p
from roboticstoolbox import DHRobot, RevoluteDH

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from robotica.dh import directa  # noqa: E402
from generar_urdf import DH  # noqa: E402


def posicion_pybullet(cid, robot_id, q):
    n = p.getNumJoints(robot_id, physicsClientId=cid)
    idx_joints = [i for i in range(n)
                  if p.getJointInfo(robot_id, i, physicsClientId=cid)[2] == p.JOINT_REVOLUTE]
    for idx, qi in zip(idx_joints, q):
        p.resetJointState(robot_id, idx, qi, physicsClientId=cid)
    # el ultimo link (tcp) es un joint fijo: su indice es n-1
    estado = p.getLinkState(robot_id, n - 1, physicsClientId=cid)
    return np.array(estado[0])  # posición mundial del origen del link


def main() -> None:
    cid = p.connect(p.DIRECT)   # sin ventana gráfica (headless)
    urdf_path = str(Path(__file__).parent / "curso_3gdl.urdf")
    robot_id = p.loadURDF(urdf_path, physicsClientId=cid, useFixedBase=True)

    robot_rtb = DHRobot([
        RevoluteDH(d=DH[0][1], a=DH[0][2], alpha=DH[0][3]),
        RevoluteDH(d=DH[1][1], a=DH[1][2], alpha=DH[1][3]),
        RevoluteDH(d=DH[2][1], a=DH[2][2], alpha=DH[2][3]),
    ], name="curso_3gdl")

    rng = np.random.default_rng(0)
    print(f"{'postura (°)':>28s} {'|propia-pybullet|':>18s} {'|propia-rtb|':>14s}")
    max_err_pb, max_err_rtb = 0.0, 0.0
    for _ in range(15):
        q = rng.uniform(-np.pi, np.pi, 3)
        p_propia = directa(DH, q)[:3, 3]
        p_pb = posicion_pybullet(cid, robot_id, q)
        p_rtb = robot_rtb.fkine(q).t

        err_pb = np.linalg.norm(p_propia - p_pb)
        err_rtb = np.linalg.norm(p_propia - p_rtb)
        max_err_pb = max(max_err_pb, err_pb)
        max_err_rtb = max(max_err_rtb, err_rtb)
        print(f"{str(np.round(np.degrees(q), 1)):>28s} {err_pb:>18.2e} {err_rtb:>14.2e}")

    print(f"\nError máximo propia vs. PyBullet:          {max_err_pb:.2e} m")
    print(f"Error máximo propia vs. Robotics Toolbox:   {max_err_rtb:.2e} m")
    assert max_err_pb < 1e-6
    assert max_err_rtb < 1e-9
    print("\nOK: las tres implementaciones coinciden.")

    p.disconnect(cid)


if __name__ == "__main__":
    main()
