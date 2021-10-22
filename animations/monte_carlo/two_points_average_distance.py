from matplotlib import animation

import math
import matplotlib.pyplot as plt
import numpy as np


def distance(point1: tuple, point2: tuple) -> bool:
	return math.sqrt(sum((x - y) ** 2 for x, y in zip(point1, point2)))

class TwoPointsAverageDistanceEstimation:
	def __init__(self, display: "Display"):
		self.display = display

	@staticmethod
	def expected_value(bottom_left_corner, top_right_corner):
		width, height = top_right_corner[ 0 ] - bottom_left_corner[ 0 ], top_right_corner[ 1 ] - bottom_left_corner[ 1 ]
		# the rectangle will have sides equal to 1 and h and solution will be scaled
		h = height / width
		d = math.sqrt(1 + h * h) # diameter of the rectangle
		return round(width * (2 + 2 * h ** 5 - 2 * d + 6 * h * h * d - 2 * h ** 4 * d + 5 * h * math.log(h + d) + 5 * h ** 4 * math.log((1 + d) / h)) / (30 * h * h), 4)

	@property
	def average_distance(self):
		return self.distance_sum / self.cnt_points

	def init(self):
		self.distance_sum = 0
		self.cnt_points = 0

	def step(self):
		return np.random.uniform(self.display.bottom_left_corner, self.display.top_right_corner, (self.display.pairs_per_iteration, 2, 2))

	def display_step(self, i: int):
		pair_of_points = self.step()
		self.distance_sum += sum(distance(point1, point2) for point1, point2 in pair_of_points)
		self.cnt_points += len(pair_of_points)
		self.display.display_step(self, i, pair_of_points)

	def estimate(self):
		self.init()
		self.display.estimate(self.display_step)

class Display:
	def __init__(self, iterations: int, pairs_per_iteration: int, bottom_left_corner: tuple, top_right_corner: tuple):
		self.iterations = iterations
		self.pairs_per_iteration = pairs_per_iteration
		self.bottom_left_corner = bottom_left_corner
		self.top_right_corner = top_right_corner

class GraphicDisplay(Display):
	def __init__(self, iterations: int, pairs_per_iteration: int, bottom_left_corner: tuple, top_right_corner: tuple):
		super(GraphicDisplay, self).__init__(iterations, pairs_per_iteration, bottom_left_corner, top_right_corner)

	def init(self):
		self.fig, (self.monte_carlo_graph, self.average_distance_estimation_graph) = plt.subplots(1, 2)
		self.fig.canvas.manager.set_window_title("Two Points Average Distance Estimation")

		self.clear()
		self.monte_carlo_graph.set_xlabel(f"I = {self.iterations} ; N = {self.pairs_per_iteration}")

		self.average_distance_estimation_graph.set_xlim(1, self.iterations)
		self.average_distance_estimation_graph.set_ylim(0, distance(self.bottom_left_corner, self.top_right_corner))
		self.average_distance_estimation_graph.set_title("Average Distance Estimation")
		self.average_distance_estimation_graph.set_xlabel(f"Iteration")
		expected_value = TwoPointsAverageDistanceEstimation.expected_value(self.bottom_left_corner, self.top_right_corner)
		self.average_distance_estimation_graph.set_ylabel(f"Average Distance Estimation\n(E = {expected_value})")
		self.average_distance_estimation_graph.axhline(y = expected_value, color = "red", linestyle = "--")

		self.fig.tight_layout()
		self.estimations = [ [], [] ]

	def clear(self):
		self.monte_carlo_graph.cla()
		self.monte_carlo_graph.set_xlim(self.bottom_left_corner[ 0 ], self.top_right_corner[ 0 ])
		self.monte_carlo_graph.set_ylim(self.bottom_left_corner[ 1 ], self.top_right_corner[ 1 ])
		self.monte_carlo_graph.set_aspect("equal")

	def display_step(self, obj: TwoPointsAverageDistanceEstimation, i: int, pair_of_points: list):
		self.clear()
		self.monte_carlo_graph.set_title(f"Iteration {i + 1}\nAverage distance estimation: {obj.average_distance:.4f}")
		for point1, point2 in pair_of_points:
			self.monte_carlo_graph.plot(*list(zip(point1, point2)), color = "blue", linestyle = '-', pickradius = 1, marker = '.')

		self.estimations[ 0 ].append(i + 1)
		self.estimations[ 1 ].append(obj.average_distance)
		self.average_distance_estimation_graph.plot(*self.estimations, color = "blue", linestyle = "solid", marker = '')

	def estimate(self, func: "Function"):
		self.init()
		anim = animation.FuncAnimation(self.fig, func, frames = self.iterations, init_func = lambda: None, repeat = False)
		# anim.save("demo.gif")
		plt.show()

class ConsoleDisplay(Display):
	def __init__(self, iterations: int, pairs_per_iteration: int, bottom_left_corner: tuple, top_right_corner: tuple, *, log: bool = True):
		super(ConsoleDisplay, self).__init__(iterations, pairs_per_iteration, bottom_left_corner, top_right_corner)
		self.log = log

	def display_step(self, obj: TwoPointsAverageDistanceEstimation, i: int, pair_of_points: list):
		if self.log:
			print(f"Iteration {i + 1} - Average distance estimation: {obj.average_distance:.4f}")

	def estimate(self, func: "Function"):
		for i in range(self.iterations):
			func(i)


if __name__ == "__main__":
	graph = TwoPointsAverageDistanceEstimation(
		display = GraphicDisplay(
			iterations = 100,
			pairs_per_iteration = 1000,
			bottom_left_corner = (0, 0),
			top_right_corner = (1, 1)
		)
	)
	graph.estimate()

	# average_distance_estimation = TwoPointsAverageDistanceEstimation(
	# 	display = ConsoleDisplay(
	# 		iterations = 1000,
	# 		pairs_per_iteration = 1000,
	# 		bottom_left_corner = (0, 0),
	# 		top_right_corner = (1, 1),
	# 		log = False
	# 	)
	# )
	# average_distance_sum, trials = 0, 1
	# for i in range(trials):
	# 	average_distance_estimation.estimate()
	# 	print(f"Iteration {i + 1} - Average distance estimation: {average_distance_estimation.average_distance:.4f}")
	# 	average_distance_sum += average_distance_estimation.average_distance
	# print(f"After {trials} iterations, by the Law of Large Numbers the average distance between two points in the rectangle" \
	# 	  f" [{average_distance_estimation.display.bottom_left_corner[ 0 ]},{average_distance_estimation.display.top_right_corner[ 0 ]}]" \
	# 	  f"x[{average_distance_estimation.display.bottom_left_corner[ 1 ]},{average_distance_estimation.display.top_right_corner[ 1 ]}]" \
	# 	  f" estimates to: {average_distance_sum / trials:.4f}")