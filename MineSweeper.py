import numpy as np
import random
import math

class MineSweeper():
	def __init__(self, difficulty):
		self.width = [9, 16, 30][difficulty]
		self.height = [9, 16, 16][difficulty]
		self.B = [10, 40, 100][difficulty]
		self.field = [[0 for w in range(self.width)] for h in range(self.height)]
		self.cell = [[-1 for w in range(self.width)] for h in range(self.height)]
		self.zero = [[False for w in range(self.width)] for h in range(self.height)]
		self.over = False
		self.clear = False

	def start(self, x, y):
		ard = self.around(x, y)
		place_bomb = np.array([random.random() for i in range(self.width * self.height)])
		order = np.argsort(place_bomb)
		bomb_place = []

		b = 0
		t = 0
		while b < self.B:
			bomb_candidate = self.num_to_position(order[t])
			if not bomb_candidate in ard and bomb_candidate != [x, y]:
				self.field[bomb_candidate[1]][bomb_candidate[0]] = -2
				b += 1
				bomb_place.append(bomb_candidate)
			t += 1

		for h in range(self.height):
			for w in range(self.width):
				position = [w, h]
				if position in bomb_place:
					continue
				p = self.around(w, h)
				count = 0
				for pi in p:
					if self.field[pi[1]][pi[0]] == -2:
						count += 1
				self.field[h][w] = count

		self.open(x, y)

	def count(self, array, value):
		count = 0
		for h in range(self.height):
			for w in range(self.width):
				if array[h][w] == value:
					count += 1
		return count

	def num_to_position(self, num):
		h = math.floor(num / self.width)
		w = num - (self.width * h) 
		return [w, h]

	def out_of_field(self, x, y):
		if x < 0 or x >= self.width or y < 0 or y >= self.height:
			return True
		else:
			return False

	def around(self, x, y):
		ard = [[-1,-1],[-1,0],[-1,1],[0,-1],[0,1],[1,-1],[1,0],[1,1]]
		p = [[x + a[0], y + a[1]] for a in ard]
		for i in range(len(p) - 1, -1, -1):
			if self.out_of_field(p[i][0], p[i][1]):
				del p[i]
		return p

	def open(self, x, y):
		self.cell[y][x] = self.field[y][x]
		if self.cell[y][x] == -2:
			self.over = True	
		while self.count(self.zero,True) != self.count(self.cell,0):
			self.open_around_zero()

		count = 0

		for h in range(self.height):
			for w in range(self.width):
				if self.cell[h][w] == -1:
					count += 1

		if count == self.B and not self.over:
			self.clear = True

		self.PlotField()

	def SearchAround(self, x, y):
		around = self.around(x, y)
		for p in around:
			if self.field[p[1]][p[0]] == 0:
				self.cell[p[1]][p[0]] = 0
	
	def open_around_zero(self):
		for h in range(self.height):
			for w in range(self.width):
				if self.cell[h][w] == 0:
					self.zero[h][w] = True
					around = self.around(w, h)
					for a in around:
						self.cell[a[1]][a[0]] = self.field[a[1]][a[0]]

	def GetCellInfo(self, x, y):
		return self.cell[y][x]

	def PlotField(self):
		self.print_judge()

		for h in range(self.height):
			for w in range(self.width):
				#"""
				if self.cell[h][w] == -1:
					print("x ", end = "")
				elif self.field[h][w] >= 0 and self.cell[h][w] >= 0:
					print("{} ".format(self.cell[h][w]), end = "")
				else:
					print("@ ", end = "")
				
			print("")
		print("")

	def print_judge(self):
		if self.over:
			print("*******************")
			print("***  game over  ***")
			print("*******************")
			print("")
		elif self.clear:
			print("*******************")
			print("*** game clear! ***")
			print("*******************")
			print("")