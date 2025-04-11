import numpy as np
from copy import deepcopy
from big_planet_orb import get_jupiter_orb_fn
from constants import G, YEAR
from check_eclipse import check_sun_eclipse, check_moon_eclipse


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

    def rk4(self, step_t):
        saved_positions = {b: b.pos.copy() for b in self.bodies}
        saved_velocities = {b: b.velocity.copy() for b in self.bodies}

        def update_all(velocities, forces, step_t):
            for b in self.bodies:
                b.pos = saved_positions[b] + velocities[b] * step_t
                b.velocity = saved_velocities[b] + (forces[b] / b.mass) * step_t

        # K1
        v1, f1 = self.compute_forces()

        # K2
        update_all(v1, f1, step_t / 2)
        v2, f2 = self.compute_forces()

        # K3
        update_all(v2, f2, step_t / 2)
        v3, f3 = self.compute_forces()

        # K4
        update_all(v3, f3, step_t)
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

            self.rk4(self.dt)

        return trajectories, t_range

    def simulate_with_eclipse_detection(self, years=8, coarse_dt=1):
        """使用两种时间步长模拟日月食
        Args:
            years: 模拟年数
            coarse_dt: 粗略时间步长（秒）
        """
        fine_dt = 0.1  # 精细时间步长为0.1小时
        total_time = years * YEAR
        trajectories = {b.name: [] for b in self.bodies}
        eclipse_events = {
            'solar': [],  # 存储日食事件
            'lunar': []   # 存储月食事件
        }
        
        current_time = 0
        
        def save_state():
            """保存当前状态，包括位置和速度"""
            positions = {b.name: b.pos.copy() for b in self.bodies}
            velocities = {b.name: b.velocity.copy() for b in self.bodies}
            return positions, velocities
        
        def restore_state(saved_state):
            """恢复到保存的状态"""
            positions, velocities = saved_state
            for b in self.bodies:
                b.pos = positions[b.name].copy()
                b.velocity = velocities[b.name].copy()
        
        def detect_eclipse():
            """检测当前状态是否发生日食或月食"""
            positions = {b.name: b.pos for b in self.bodies}
            sun_pos = positions['Sun']
            earth_pos = positions['Earth']
            moon_pos = positions['Moon']
            
            solar_type = check_sun_eclipse(sun_pos[np.newaxis], 
                                         moon_pos[np.newaxis], 
                                         earth_pos[np.newaxis])
            
            lunar_type = check_moon_eclipse(sun_pos[np.newaxis], 
                                          moon_pos[np.newaxis], 
                                          earth_pos[np.newaxis])
            
            return solar_type[0], lunar_type[0]
        
        # 主循环
        while current_time < total_time:
            # 保存当前状态用于回退
            prev_state = save_state()
            
            # 使用粗时间步长更新
            self.dt = coarse_dt
            self.rk4(coarse_dt)
            current_time += coarse_dt
            
            # 检测是否发生日食或月食
            solar_type, lunar_type = detect_eclipse()
            
            if solar_type is not None or lunar_type is not None:
                # 发现食现象，回退到上一步
                restore_state(prev_state)
                current_time -= coarse_dt
                
                # 记录事件信息
                event_type = 'solar' if solar_type is not None else 'lunar'
                eclipse_type = solar_type if solar_type is not None else lunar_type
                
                # 使用精细时间步长追踪食现象
                self.dt = fine_dt
                eclipse_ongoing = False
                eclipse_duration_time = 0

                while not eclipse_ongoing:
                    self.rk4(fine_dt)
                    current_time += fine_dt
                    
                    # 检测食现象状态
                    solar_type, lunar_type = detect_eclipse()
                    
                    if solar_type is not None or lunar_type is not None:
                        # 食现象开始
                        eclipse_ongoing = True
                        event_start_time = current_time
                
                while eclipse_ongoing:
                    self.rk4(fine_dt)
                    current_time += fine_dt
                    
                    # 检测食现象状态
                    solar_type, lunar_type = detect_eclipse()
                    
                    if solar_type is not None or lunar_type is not None:
                        # 更新食甚时间
                        eclipse_duration_time += fine_dt
                    else:
                        # 食现象结束
                        eclipse_events[event_type].append({
                            'type': eclipse_type,
                            'start_time': event_start_time,
                            'max_time': event_start_time + eclipse_duration_time / 2,
                            'end_time': current_time,
                            'duration': eclipse_duration_time
                        })
                        eclipse_ongoing = False

            # 记录轨道
            for body in self.bodies:
                trajectories[body.name].append(body.pos.copy())
        
        # 将轨迹转换为numpy数组
        for body in trajectories:
            trajectories[body] = np.array(trajectories[body])
        
        return trajectories, eclipse_events
