import numpy as np

class SystemCalculator:
    def __init__(self):
        self.K_global = None
        self.force_vector = None
        self.displacements = None
        self.stresses = None
        self.forces = None
        self.n_nodes = 0
        self.fixed_nodes = []

    def calculate_system(self, system_data, main_window, n_points_per_bar=100):
        """
        Выполнить расчёт системы и сформировать массив точек для графиков.
        """
        try:
            left_fixed = main_window.viewer.checkbox.left_checkbox.isChecked()
            right_fixed = main_window.viewer.checkbox.right_checkbox.isChecked()

            self.assemble_global_matrix(system_data)
            self.assemble_force_vector_correct(system_data)
            K_reduced, F_reduced = self.apply_boundary_conditions(left_fixed, right_fixed)
            self.solve_system(K_reduced, F_reduced, left_fixed, right_fixed)
            self.calculate_stresses_forces_displacements(system_data, n_points_per_bar)
            return True
        except Exception as e:
            print(f"Ошибка расчёта: {e}")
            import traceback
            traceback.print_exc()
            return False

    def assemble_global_matrix(self, system_data):
        bars_data = system_data["Стержни"]
        self.n_nodes = len(bars_data) + 1
        self.K_global = np.zeros((self.n_nodes, self.n_nodes))

        for p, bar in enumerate(bars_data):
            L, A, E = bar[:3]
            k_p = (E * A) / L
            K_local = np.array([[k_p, -k_p], [-k_p, k_p]])
            i, j = p, p+1
            self.K_global[i, i] += K_local[0, 0]
            self.K_global[i, j] += K_local[0, 1]
            self.K_global[j, i] += K_local[1, 0]
            self.K_global[j, j] += K_local[1, 1]

    def assemble_force_vector_correct(self, system_data):
        bars_data = system_data["Стержни"]
        distributed_loads = system_data["Распределенные нагрузки"]
        concentrated_loads = system_data["Сосредоточенные нагрузки"]
        self.force_vector = np.zeros(self.n_nodes)

        for load in distributed_loads:
            p, q = load[0]-1, load[1]
            if 0 <= p < len(bars_data):
                L = bars_data[p][0]
                Q_star = q * L / 2
                self.force_vector[p] += Q_star
                self.force_vector[p+1] += Q_star

        for load in concentrated_loads:
            node, F = load[0]-1, load[1]
            if 0 <= node < self.n_nodes:
                self.force_vector[node] += F

    def apply_boundary_conditions(self, left_fixed, right_fixed):
        self.fixed_nodes = []
        if left_fixed: self.fixed_nodes.append(0)
        if right_fixed: self.fixed_nodes.append(self.n_nodes-1)
        free_nodes = [i for i in range(self.n_nodes) if i not in self.fixed_nodes]
        K_reduced = self.K_global[np.ix_(free_nodes, free_nodes)]
        F_reduced = self.force_vector[free_nodes]
        return K_reduced, F_reduced

    def solve_system(self, K_reduced, F_reduced, left_fixed, right_fixed):
        displacements_reduced = np.linalg.solve(K_reduced, F_reduced)
        self.displacements = np.zeros(self.n_nodes)
        free_nodes = [i for i in range(self.n_nodes) if i not in self.fixed_nodes]
        for idx, node in enumerate(free_nodes):
            self.displacements[node] = displacements_reduced[idx]

    def calculate_stresses_forces_displacements(self, system_data, n_points=100):
        """
        Формирует функции и массивы точек для каждого стержня.
        """
        bars_data = system_data["Стержни"]
        distributed_loads = system_data["Распределенные нагрузки"]

        self.forces = []
        self.stresses = []

        self.bar_forces_points = []
        self.bar_stresses_points = []
        self.bar_displacements_points = []

        self.graph_table = []

        total_x = 0.0  # глобальная координата

        for p, bar in enumerate(bars_data):
            L, A, E = bar[:3]
            i, j = p, p+1
            U0, UL = self.displacements[i], self.displacements[j]

            # распределённая нагрузка
            q = 0
            for load in distributed_loads:
                if load[0]-1 == p:
                    q = load[1]
                    break

            # функции N(x), σ(x), u(x)
            def N_func(x, E=E, A=A, L=L, U0=U0, UL=UL, q=q):
                return (E*A/L)*(UL-U0) + q*(L/2 - x)

            def sigma_func(x, E=E, A=A, L=L, U0=U0, UL=UL, q=q):
                N = (E*A/L)*(UL-U0) + q*(L/2 - x)
                return N/A if A != 0 else 0

            def u_func(x, U0=U0, UL=UL, L=L, q=q, E=E, A=A):
                # точное решение перемещений для стержня с равномерной нагрузкой
                return U0 + (UL-U0)*(x/L) + (q/(2*E*A))*(x*L - x**2)

            self.forces.append(N_func)
            self.stresses.append(sigma_func)

            xs = np.linspace(0, L, n_points)
            N_points = [N_func(x) for x in xs]
            sigma_points = [sigma_func(x) for x in xs]
            u_points = [u_func(x) for x in xs]

            self.bar_forces_points.append(list(zip(xs, N_points)))
            self.bar_stresses_points.append(list(zip(xs, sigma_points)))
            self.bar_displacements_points.append(list(zip(xs, u_points)))

            # Формируем graph_table для постпроцессора
            for xi, ui, Ni, si in zip(xs, u_points, N_points, sigma_points):
                self.graph_table.append({
                    "bar": p+1,
                    "x": total_x + xi,  # глобальная координата
                    "u": ui,
                    "N": Ni,
                    "sigma": si
                })

            total_x += L

    # В SystemCalculator
    @staticmethod
    def check_strength(results, sigma_allow_list):
        strength_status = []
        max_sigmas = []

        for i, bar_points in enumerate(results['bar_stresses_points']):
            _, ys = zip(*bar_points)
            max_sigma = max(map(abs, ys))  # максимальное по модулю напряжение
            max_sigmas.append(max_sigma)

            sigma_allow = sigma_allow_list[i]
            if max_sigma <= sigma_allow:
                strength_status.append("Прочность обеспечена")
            else:
                strength_status.append("Прочность не обеспечена")

        return max_sigmas, strength_status

    def get_results(self):
        return {
            'global_stiffness_matrix': self.K_global,
            'force_vector': self.force_vector,
            'displacements': self.displacements,
            'bar_forces': self.forces,
            'bar_stresses': self.stresses,
            'n_nodes': self.n_nodes,
            'fixed_nodes': self.fixed_nodes,
            'bar_forces_points': self.bar_forces_points,
            'bar_stresses_points': self.bar_stresses_points,
            'bar_displacements_points': self.bar_displacements_points,
            'graph_table': self.graph_table
        }
