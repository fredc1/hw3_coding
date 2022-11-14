import random
from BaseAI import BaseAI
import copy
import math
import time

def merge_score(grid):
	arr = grid.map 
	merges = 0
	for row in arr:
		last = -1
		for i in range(len(row)):
			if row[i] == last:

				merges += 1#math.log(last, 2)
			if row[i] != 0:
				last = row[i]
	for c in range(len(arr)):
		last = -1
		for r in range(len(arr)):
			if arr[r][c] == last:
				merges += 1#math.log(last, 2)
			if arr[r][c] != 0:
				last = arr[r][c]
	return merges

		
def edge_score(grid):
	grid = grid.map
	arr = grid
	'''
	four_max_tiles = []
	for r in range(len(grid)):
		for c in range(len(grid)):
			if len(four_max_tiles) < 2:
				four_max_tiles.append((r,c))
				break

			for i, (a,b) in enumerate(four_max_tiles):
				if grid[r][c] > grid[a][b]:
					four_max_tiles[i] = (r,c)
					break
	on_edge = [int(r==0 or r==3 or c==0 or c==3) for r,c in four_max_tiles]
	#in_corner = [int(p in [(0,0), (0,3), (3,0),(3,3)]) for p in four_max_tiles]
	return sum(on_edge)#+sum(in_corner)
	'''
	max_tile = None
	for r in range(len(grid)):
		for c in range(len(grid)):
			if max_tile is None:
				max_tile = (r,c)
				break
			a,b = max_tile
			if arr[r][c] > arr[a][b]:
				max_tile = (a,b)
	r,c = max_tile
	score = 0
	if r==0 or r==3 or c==0 or c==3:
		score += 2
	if (r,c) in [(0,0), (0,3), (3,0),(3,3)]:
		score += 2 
	return score
# no score 2, 1, 1, 1, 1, 1
# score 1, 1, 
def mono_score(grid):
	arr = grid.map 
	score = 0
	for row in arr:
		trans = []
		
		for i in range(len(row)):
			if i + 1 < 4 and row[i+1] != 0:
				v = row[i+1] - row[i]
				if v==0: trans.append(0)
				else: trans.append(v/v)
		score += int(trans[0]==trans[1]) + int(trans[1]==trans[2])

	for c in range(len(arr)):
		trans = []
		
		for i in range(len(arr)):
			if i + 1 < 4:
				v = arr[i+1][c] - arr[i][c]
				trans.append(v/v)
		score += int(trans[0]==trans[1]) + int(trans[1]==trans[2])
	return score


def next_nonzero_entry(b, p, d):
	(r, c) = p
	if d=='row':
		while c < 3:
			c += 1
			v = b[r][c]
			if v != 0:
				return r, c, v
		return None, None, None

	while r < 3:
		r += 1
		v = b[r][c]
		if v != 0:
			return r,c,v

	return None, None, None


def smooth_score(grid):
	arr = grid.map 
	volatility = 0
	for r in range(len(arr)):
		for c, v in enumerate(arr[r]):
			if v==0:
				continue
			i,j,nv = next_nonzero_entry(arr,(r,c),'row')
			if nv is not None:
				volatility += abs(math.log(nv,2) - math.log(v,2))
	for c in range(len(arr)):
		for r in range(len(arr)):
			v = arr[r][c]
			if v==0:
				continue
			i,j,nv = next_nonzero_entry(arr,(r,c),'col')
			if nv is not None:
				volatility += abs(math.log(nv,2) - math.log(v,2))

	return -1*volatility




def heuristic(grid):
	score = grid.getMaxTile()
	score = int(math.log(score, 2))
	return score + 3*len(grid.getAvailableCells())  + 2*edge_score(grid) + smooth_score(grid)


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
		nstate.chance_val = val
		return nstate


def maximizer(state, alpha, beta, maxd, st):
	if (time.process_time() - st) >= 0.2:
		return 0,0, True

	succs = state.max_successors()
	if len(succs) == 0:
		return state.move, 0, False

	succs.sort(key=(lambda s: s.h), reverse=True)

	

	if state.d >= maxd:
		return succs[0].move, succs[0].h, False


	max_succ_val = -1.0
	max_succ_mov = -1

	for succ in succs:
		v, short = chancer(succ, alpha, beta, maxd, st)
		if short: return 0,0, short
		if v > max_succ_val:
			max_succ_val = v
			max_succ_mov = succ.move
		if v >= beta: return succ.move, v, False
		if v > alpha: alpha = v

	return max_succ_mov, max_succ_val, False



def minimizer(state, alpha, beta, maxd, st):
	if (time.process_time() - st) >= 0.2:
		return 0, True

	succs = state.min_successors()
	if len(succs) == 0:
		assert 0, "minimizer was passed a state with no tiles to fill"

	succs.sort(key=(lambda s: s.h))

	if state.d >= maxd:
		return succs[0].h, False

	min_val = math.inf
	for succ in succs:
		m, v, short = maximizer(succ, alpha, beta, maxd, st)
		if short: return 0, short
		if v < min_val: min_val = v
		if v <= alpha: return v, False
		if v < beta: beta = v
	return min_val, False


def chancer(state, alpha, beta, maxd, st):
	two, short1 = minimizer(state.chance_successor(2), alpha, beta, maxd, st)
	if short1: return 0, short1
	four, short2 = minimizer(state.chance_successor(4), alpha, beta, maxd, st)
	if short2: return 0, short2
	return (0.9 * two + 0.1 * four), False


class IntelligentAgent(BaseAI):
	def getMove(self, grid):
		start_time = time.process_time()
		state = EMMState(grid, 0)
		best_move = -1
		depth = 1
		called_max = 0
		while (time.process_time() - start_time) <= 0.2:
			move, score, short = maximizer(state, alpha=-1.0, beta=math.inf, maxd=depth, st=start_time)
			called_max = 1
			if short:
				break
				print(f"shorted on depth {depth}")
			else:
				best_move = move
				depth += 1
		if best_move == -1:
			s = time.process_time()
			state = EMMState(grid, 0)
			f = time.process_time()
			print(f"TIME TOO LONG FOR H: {f-s > 0.2} called max: {called_max}")
		return best_move
		