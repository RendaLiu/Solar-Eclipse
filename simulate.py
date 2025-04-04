import numpy as np
from copy import deepcopy
from big_planet_orb import get_jupiter_orb_fn
from constants import G, YEAR


class ThreeBodySimulator:
    def __init__(self, bodies, dt=1, aux_list=None):
        """
        :param bodies: list of CelestialBody objects
        :param dt: 时间步长 (小时)
        :param aux_list: 辅助天体列表，例如木星等
        """
        self.bodies = bodies
        self.dt = dt
        self.aux_list = aux_list if aux_list is not None else []
        self.orb_fns = [get_jupiter_orb_fn(aux_body) for aux_body in self.aux_list]

    def compute_pairwise_force(self, body1, body2):
        """
        计算两个天体之间的引力
        """
        r = body2.pos - body1.pos
        r_mag = np.linalg.norm(r)
        if r_mag == 0:
            return np.zeros(3)  # 避免除以0
        return G * body1.mass * body2.mass / (r_mag ** 3) * r

    def compute_forces(self, bodies=None):
        """
        计算所有天体间的引力
        """
        if bodies is None:
            bodies = self.bodies

        forces = {body: np.zeros(3) for body in bodies}
        velocities = {body: body.velocity.copy() for body in bodies}

        # 主天体间引力
        for i, body1 in enumerate(bodies):
            for body2 in bodies[i + 1:]:
                F = self.compute_pairwise_force(body1, body2)
                forces[body1] += F
                forces[body2] -= F

        # 计算主天体受到辅助天体的引力
        for body in bodies:
            for aux_body in self.aux_list:
                F = self.compute_pairwise_force(body, aux_body)
                forces[body] += F

        return velocities, forces

    def rk4(self):
        saved_positions = {b: b.pos.copy() for b in self.bodies}
        saved_velocities = {b: b.velocity.copy() for b in self.bodies}

        def update_all(velocities, forces, dt):
            for b in self.bodies:
                b.pos = saved_positions[b] + velocities[b] * dt
                b.velocity = saved_velocities[b] + (forces[b] / b.mass) * dt

        # K1
        v1, f1 = self.compute_forces()

        # K2
        update_all(v1, f1, self.dt / 2)
        v2, f2 = self.compute_forces()

        # K3
        update_all(v2, f2, self.dt / 2)
        v3, f3 = self.compute_forces()

        # K4
        update_all(v3, f3, self.dt)
        v4, f4 = self.compute_forces()

        # 最终更新
        for b in self.bodies:
            b.pos = saved_positions[b] + self.dt * (v1[b] + 2 * v2[b] + 2 * v3[b] + v4[b]) / 6
            b.velocity = saved_velocities[b] + self.dt * (f1[b] + 2 * f2[b] + 2 * f3[b] + f4[b]) / (6 * b.mass)

    def simulate_rk4(self, years=50):
        steps = int(years * YEAR / self.dt)
        trajectories = {b.name: np.zeros((steps, 3)) for b in self.bodies}
        t_range = np.arange(steps) * self.dt

        for step in range(steps):
            # 更新辅助天体轨道
            for aux_body, orb_fn in zip(self.aux_list, self.orb_fns):
                aux_body.pos = orb_fn(step * self.dt)

            for body in self.bodies:
                trajectories[body.name][step] = body.pos.copy()

            self.rk4()

        return trajectories, t_range
