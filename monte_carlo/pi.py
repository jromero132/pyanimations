from matplotlib import animation

import math
import matplotlib.pyplot as plt
import numpy as np


def is_in_circle(center: tuple, radius: float, point: tuple) -> bool:
	return math.sqrt(sum((c - p) ** 2 for c, p in zip(center, point))) <= radius

class MonteCarloPiEstimation:
	def __init__(self, display: "Display"):
		self.display = display

	@staticmethod
	def expected_value():
		return 3.1415

	@property
	def pi(self):
		return 4 * self.cnt_in_points / self.cnt_all_points

	def init(self):
		self.cnt_in_points = 0
		self.cnt_all_points = 0

	def step(self):
		in_points, out_points = [ [], [] ], [ [], [] ]
		points = np.random.uniform(self.display.bottom_left_corner, self.display.top_right_corner, (self.display.points_per_iteration, 2))
		for p in points:
			if is_in_circle(self.display.center, self.display.radius, p):
				in_points[ 0 ].append(p[ 0 ])
				in_points[ 1 ].append(p[ 1 ])
			else:
				out_points[ 0 ].append(p[ 0 ])
				out_points[ 1 ].append(p[ 1 ])
		return in_points, out_points

	def display_step(self, i: int):
		in_points, out_points = self.step()
		self.cnt_in_points += len(in_points[ 0 ])
		self.cnt_all_points += len(in_points[ 0 ]) + len(out_points[ 0 ])
		self.display.display_step(self, i, in_points, out_points)

	def estimate(self):
		self.init()
		self.display.estimate(self.display_step)

class Display:
	def __init__(self, iterations: int, points_per_iteration: int, bottom_left_corner: tuple, length: float):
		self.iterations = iterations
		self.points_per_iteration = points_per_iteration
		self.bottom_left_corner = bottom_left_corner
		self.top_right_corner = tuple(x + length for x in bottom_left_corner)
		self.radius = length / 2
		self.center = tuple(x + self.radius for x in self.bottom_left_corner)

class GraphicDisplay(Display):
	def __init__(self, iterations: int, points_per_iteration: int, bottom_left_corner: tuple, length: float):
		super(GraphicDisplay, self).__init__(iterations, points_per_iteration, bottom_left_corner, length)

	def init(self):
		self.fig, (self.monte_carlo_graph, self.pi_estimation_graph) = plt.subplots(1, 2)
		self.fig.canvas.manager.set_window_title("Monte Carlo Pi Estimation")

		self.monte_carlo_graph.set_aspect("equal")
		self.monte_carlo_graph.set_xlim(self.bottom_left_corner[ 0 ], self.top_right_corner[ 0 ])
		self.monte_carlo_graph.set_ylim(self.bottom_left_corner[ 1 ], self.top_right_corner[ 1 ])
		self.monte_carlo_graph.set_xlabel(f"I = {self.iterations} ; N = {self.points_per_iteration}")

		angle = np.linspace(0, 2 * np.pi, 180)
		circle_x = self.center[ 0 ] + self.radius * np.cos(angle)
		circle_y = self.center[ 1 ] + self.radius * np.sin(angle)
		self.monte_carlo_graph.plot(circle_x, circle_y, color = "blue")

		self.pi_estimation_graph.set_xlim(1, self.iterations)
		self.pi_estimation_graph.set_ylim(0, 5)
		self.pi_estimation_graph.set_title("Pi Estimation")
		self.pi_estimation_graph.set_xlabel(f"Iteration")
		expected_value = MonteCarloPiEstimation.expected_value()
		self.pi_estimation_graph.set_ylabel(f"Pi Estimation (E = {expected_value})")
		self.pi_estimation_graph.axhline(y = expected_value, color = "red", linestyle = "--")

		self.fig.tight_layout()
		self.estimations = [ [], [] ]

	def display_step(self, obj: MonteCarloPiEstimation, i: int, in_points: list, out_points: list):
		self.monte_carlo_graph.set_title(f"Iteration {i + 1} - Pi estimation: {obj.pi:.4f}")
		self.monte_carlo_graph.scatter(*in_points, color = "blue", s = 1)
		self.monte_carlo_graph.scatter(*out_points, color = "red", s = 1)

		self.estimations[ 0 ].append(i + 1)
		self.estimations[ 1 ].append(obj.pi)
		self.pi_estimation_graph.plot(*self.estimations, color = "blue", linestyle = "solid", marker = '')

	def estimate(self, func: "Function"):
		self.init()
		anim = animation.FuncAnimation(self.fig, func, frames = self.iterations, init_func = lambda: None, repeat = False)
		# anim.save("demo.gif")
		plt.show()

class ConsoleDisplay(Display):
	def __init__(self, iterations: int, points_per_iteration: int, bottom_left_corner: tuple, length: int, *, log: bool = True):
		super(ConsoleDisplay, self).__init__(iterations, points_per_iteration, bottom_left_corner, length)
		self.log = log

	def display_step(self, obj: MonteCarloPiEstimation, i: int, in_points: list, out_points: list):
		if self.log:
			print(f"Iteration {i + 1} - Pi estimation: {obj.pi:.4f}")

	def estimate(self, func: "Function"):
		for i in range(self.iterations):
			func(i)


if __name__ == "__main__":
	graph = MonteCarloPiEstimation(
		display = GraphicDisplay(
			iterations = 100,
			points_per_iteration = 1000,
			bottom_left_corner = (0, 0),
			length = 1
		)
	)
	graph.estimate()

	# pi_estimation = MonteCarloPiEstimation(
	# 	display = ConsoleDisplay(
	# 		iterations = 1000,
	# 		points_per_iteration = 1000,
	# 		bottom_left_corner = (0, 0),
	# 		length = 1,
	# 		log = False
	# 	)
	# )
	# pi_sum, trials = 0, 100
	# for i in range(trials):
	# 	pi_estimation.estimate()
	# 	print(f"Iteration {i + 1} - Pi estimation: {pi_estimation.pi:.4f}")
	# 	pi_sum += pi_estimation.pi
	# print(f"After {trials} iterations, by the Law of Large Numbers pi estimates to: {pi_sum / trials:.4f}")