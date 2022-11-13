import random
from BaseAI import BaseAI
import copy
import math
import time

def merge_score(grid):
	return 0

def edge_score(grid):
	grid = grid.map
	four_max_tiles = []
	for r in range(len(grid)):
		for c in range(len(grid)):
			if len(four_max_tiles)<4:
				four_max_tiles.append((r,c))
				break

			for i, (a,b) in enumerate(four_max_tiles):
				if grid[r][c] > grid[a][b]:
					four_max_tiles[i] = (r,c)
					break
	on_edge = [int(r==0 or r==3 or c==0 or c==3) for r,c in four_max_tiles]
	in_corner = [int(p in [(0,0), (0,3), (3,0),(3,3)]) for p in four_max_tiles]
	return sum(on_edge)+sum(in_corner)

def mono_score(grid):
	return 0
	#count = 0

	#for row in grid:
		#if 

def heuristic(grid):
	score = grid.getMaxTile()
	score = int(math.log(score, 2))
	return score  + 3*len(grid.getAvailableCells()) + mono_score(grid) + edge_score(grid) + merge_score(grid)


class EMMState:
	def __init__(self, grid, d):
		self.move = -1
		self.grid = grid
		self.d = d
		self.h = heuristic(grid)
		self.chance_val = -1

	def max_successors(self):
		result = []
		for i in range(4):
			succ = self.grid.clone()
			if succ.move(i):
				state = EMMState(succ, self.d+1)
				state.move = i
				result.append(state)
		return result

	def min_successors(self):
		result = []
		for tile in self.grid.getAvailableCells():
			ngrid = self.grid.clone()
			ngrid.setCellValue(tile, self.chance_val)
			state = EMMState(ngrid, self.d+1)
			result.append(state)
		return result

	def chance_successor(self, val):
		nstate = copy.deepcopy(self)
		nstate.d += 1
		nstate.chance_val = val
		return nstate


def maximizer(state, alpha, beta, maxd, st):
	

	succs = state.max_successors()
	if len(succs) == 0:
		return state.move, state.h

	succs.sort(key=(lambda s: s.h), reverse=True)

	if (time.process_time() - st) >= 0.2:
		return succs[0].move, succs[0].h

	if state.d >= maxd:
		return succs[0].move, succs[0].h


	max_succ_val = -1.0
	max_succ_mov = -1

	for succ in succs:
		v = chancer(succ, alpha, beta, maxd, st)
		if v > max_succ_val:
			max_succ_val = v
			max_succ_mov = succ.move
		if v >= beta: return succ.move, v
		if v > alpha: alpha = v

	return max_succ_mov, max_succ_val



def minimizer(state, alpha, beta, maxd, st):
	succs = state.min_successors()
	if len(succs) == 0:
		assert 0, "minimizer was passed a state with no tiles to fill"

	succs.sort(key=(lambda s: s.h))

	#if (time.process_time()-st) >= 0.2:
		#return succs[0].h

	min_val = math.inf
	for succ in succs:
		m, v = maximizer(succ, alpha, beta, maxd, st)
		if v < min_val: min_val = v
		if v <= alpha: return v
		if v < beta: beta = v
	return min_val


def chancer(state, alpha, beta, maxd, st):
	two = minimizer(state.chance_successor(2), alpha, beta, maxd, st)
	four = minimizer(state.chance_successor(4), alpha, beta, maxd, st)
	return 0.9 * two + 0.1 * four


class IntelligentAgent(BaseAI):
	def getMove(self, grid):
		start_time = time.process_time()
		state = EMMState(grid, 0)
		move, score = maximizer(state, alpha=-1.0, beta=math.inf, maxd=10, st=start_time)
		return move
		