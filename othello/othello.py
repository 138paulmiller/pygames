#!/usr/bin/env python3
import datetime
import pygame,math,random, time


	# ---------------------------- Board Class ------------------------------------
class Board:
	'''
	Board - Represents the Othello/Reversi board as a 2D grid of cells.
			Each cell is owned by either player one, two, or neither(nil). 
	'''
	# Statics for the board
	PLAYER_NEITHER = -1 # niether player
	PLAYER_BLACK = 0 # player one (black)
	PLAYER_WHITE = 1 # player two (white)
	DIMEN = 10 # dimension of the grid 8x8
	BLACK = [0,0,0]
	WHITE = [255,255,255]

	TILE_COLOR_A = [34,109,34]
	TILE_COLOR_B = [12,155,12]
	
	# Move and states
	TIE = 2 		# TIE
	NO_MOVES = 3	
	GAME_OVER = 4
	WAIT_TIME = 8 # 5 steps
	BUNNY_FILE = 'bunny.png'

	# ---------------------------- Cell Class ------------------------------------
	class Cell:
		'''
		Board - Basic components of the board
				Each cell has an owner that is either one of the players or none. 
				Each cell also contains its indices on the grid [0-DIMEN][0-DIMEN] and its
				position in screen space (x,y).
		'''
		# Statics for the cells
		HIGHLIGHT_PIECE_COLOR= [255,12,0]
		HIGHLIGHT_CELL_COLOR = [250,250,0]
		TEXT_COLOR = [205,5,1]
		BONUS = 2
		FRAMES = 5 # number animation frames 
		# ---------------------------- Cell Definitions ------------------------------------
		def __init__(self, grid_pos, screen_pos, size, owner):
			i,j = grid_pos[0],grid_pos[1]
			x,y = screen_pos[0],screen_pos[1]
			self.grid_pos = grid_pos # indices on grid
			self.screen_pos = screen_pos # coordinates of rect
			self.size = size  # size of cell
			self.owner = owner # player one, two or nil
			self.midpoint = int((x*2+size[0])/2), int((y*2+size[1])/2) # get middle of rect diagonal
			self.radius = int((size[0]+size[1])/5) # create radius slightly smaller than avg of width and height
			self.rect = [self.screen_pos[0],self.screen_pos[1],self.size[0],self.size[1]]
			self.frame = 0
			# color each cell in traditional "grid" pattern
			# if col is even and row is odd  
			if (i%2) == 0 and (j%2) != 0:
					self.cell_color = Board.TILE_COLOR_A
			# if row is even and col is odd 
			elif (j%2) == 0 and (i%2) != 0:
					self.cell_color = Board.TILE_COLOR_A
			else:
				#else color background color
				self.cell_color = Board.TILE_COLOR_B
			self.bunny = None
			self.plus_one_frame = False # if bonus
			self.font = pygame.font.SysFont(None, 54)
			self.plus_one_text = self.font.render('+'+str(self.BONUS), True,  self.TEXT_COLOR)


		def __repr__(self):
			return "(" + str( self.grid_pos[0]) + ", " + str(self.grid_pos[1]) + ")"

		def __eq__(self, other):
			if other:
				return self.grid_pos == other.grid_pos		
			return False

		def __hash__(self):
			return hash(self.grid_pos )


		def copy(self):
			'''
				return deepcopy of cell
			'''
			return Board.Cell(self.grid_pos, self.screen_pos, self.size, self.owner)


		def draw(self, screen):
			pygame.draw.rect(screen, self.cell_color, self.rect, 0)
			# draw the piece if any
			if self.owner != Board.PLAYER_NEITHER:
				color = None
				if self.frame == 0: # not currently animated
					if self.owner == Board.PLAYER_BLACK:
						color = Board.BLACK
					elif self.owner == Board.PLAYER_WHITE:
						color = Board.WHITE
					pygame.draw.circle(screen, color, self.midpoint,self.radius,0)
				else: #animate
					# to simulate the piece being flipped draw an ellipse whose width decrease then increases
					# on the increase change the color to the new owner 
					# flips along
					if self.bunny:
						self.plus_one_frame = 1
					rot = math.sin(self.frame)
					if rot < 0:
						rot *= -1
						# flip color to current owner
						if self.owner == Board.PLAYER_BLACK:
							color = Board.BLACK
						elif self.owner == Board.PLAYER_WHITE:
							color = Board.WHITE
					else:
						# still flipping, draw with previous owner color
						if self.owner == Board.PLAYER_BLACK:
							color = Board.WHITE
						elif self.owner == Board.PLAYER_WHITE:
							color = Board.BLACK
					# draw animated rotating disk effect with ellipse
					w,h = self.radius*2/self.frame*rot, self.radius*2
					x,y = self.midpoint[0]-self.radius/self.frame*rot, self.midpoint[1]-self.radius
					pygame.draw.ellipse(screen, color, [x,y,w,h],0)
					self.frame += 1
					self.frame %= self.FRAMES

			
			if self.bunny != None:
				pos =  int(self.midpoint[0]-self.bunny.get_width()/2),\
				  		int(self.midpoint[1]-self.bunny.get_height()/2)
				screen.blit(self.bunny, pos)
				if self.plus_one_frame > 0:
					x,y = self.rect[0], self.rect[1]
					w,h = self.rect[2]+self.frame*2, self.rect[3]+self.frame*2
					screen.blit(self.plus_one_text, [x,y,w,h])
					if self.plus_one_frame == 0:
						self.plus_one_frame = False
					else:
						self.plus_one_frame += 1
						self.plus_one_frame %= self.FRAMES

		def flip(self):
			self.frame = 1
			# flip owner
			self.owner = Board.toggle_player(self.owner)


		def draw_highlight(self,screen, piece=False):
			if piece:
				pygame.draw.circle(screen, self.HIGHLIGHT_PIECE_COLOR, self.midpoint,self.radius+2,3)
			else:
				pygame.draw.rect(screen, self.HIGHLIGHT_CELL_COLOR, self.rect, 3)


		def does_intersect(self, pos):
			return (pos[0] > self.rect[0] and pos[0] < self.rect[0]+self.rect[2]) \
				and (pos[1] > self.rect[1] and pos[1] < self.rect[1]+self.rect[3])
			
	# ---------------------------- Board Definitions ------------------------------------
	def __init__(self, offset, size):
		self.font = pygame.font.SysFont(None, 48)
		self.offset = offset
		self.size = size 
		cell_size = size[0]//self.DIMEN, size[1]//self.DIMEN
		img_size = int(cell_size[0]*0.6), int(cell_size[1]*0.6)
		self.img = pygame.transform.scale(pygame.image.load(self.BUNNY_FILE), img_size)
		self.player_bonuses = {} 
		self.grid = []
		self.setup_board(offset, cell_size)
		# TODO - random ", draw as bunny 
		# assign "bunnies" double point cells
		random.seed(datetime.datetime.now())
		for i in range(0,5):
			x,y =  random.randint(0,self.DIMEN-1), random.randint(0, self.DIMEN-1) 
			self.grid[x][y].bunny = self.img
		self.winner = self.PLAYER_NEITHER
		# foreach bunny visited add to bonus
		self.wait = 0 #animation waittime, after eah move made wait for animation

	def copy(self):
		'''
			return deepcopy of board
		'''
		copy = Board(self.offset, self.size)
		for i in range(0,self.DIMEN):
			for j in range(0,self.DIMEN):
				copy.grid[i][j] = self.grid[i][j].copy()
		return copy

	def is_waiting(self):
		#waiting to help tell if board is waiting for animations to finish
		return self.wait > 0


	@staticmethod
	def toggle_player(owner):
		return (owner+1)%2


	def setup_board(self, offset, cell_size):
		# bonuses for each player
		self.player_bonuses = {self.PLAYER_BLACK : 0, self.PLAYER_WHITE : 0}
		self.pieces = {}
		# clear if not empty
		if len(self.grid) > 0:	
			for row in self.grid:
				row[:] = []
			self.grid[:] = []
		# populate elements
		for x in range(0, self.DIMEN):
			self.grid.append([])
			for y in range(0, self.DIMEN):
				screen_pos = (offset[0]+x*cell_size[0], offset[1]+y*cell_size[1])
				self.grid[x].append(self.Cell((x,y), screen_pos, cell_size, self.PLAYER_NEITHER) )
		center = (self.DIMEN-1)//2
		# set initial pieces
		a = self.grid[center][center+1]
		b = self.grid[center+1][center]
		c = self.grid[center][center]
		d = self.grid[center+1][center+1]
		self.pieces[self.PLAYER_BLACK] = {a:1, b:1}
		self.pieces[self.PLAYER_WHITE] = {c:1, d:1}
		a.owner = b.owner = self.PLAYER_BLACK
		c.owner = d.owner = self.PLAYER_WHITE

	def get_winner(self):
		return self.winner

	def get_score(self, player):
		score = 0
		for cell in self.pieces[player]:
			score+=1
		return score + self.player_bonuses[player]

	def check_game_over(self):
		'''
			Returns winner if game is over, if game is not over returns PLAYER_NEITHER
		'''
		winner = self.PLAYER_NEITHER
		has_empty = False
		i = 0
		# try to find any empty cell
		while not has_empty and i < self.DIMEN:
			j =0
			while not has_empty and j < self.DIMEN:
				if self.grid[i][j].owner == self.PLAYER_NEITHER:
					has_empty = True
				j+=1
			i+=1

		# if player has no cells then they lose!
		# if black_cell_count <= 0 :
		# 	winner = self.PLAYER_WHITE
		# elif white_cell_count <= 0 :
		# 	winner = self.PLAYER_BLACK
		black_score = self.get_score(self.PLAYER_BLACK)
		white_score = self.get_score(self.PLAYER_WHITE)
		if black_score <= 0 :
			winner = self.PLAYER_WHITE
		elif white_score <= 0 :
			winner = self.PLAYER_BLACK
		# if the board has no empty, pick winner by number of owned cells
		elif not has_empty:
			print("FULL BOARD!")
			if black_score > white_score:
				winner = self.PLAYER_BLACK  
			elif black_score < white_score:
				winner = self.PLAYER_WHITE
			else:
				winner = self.TIE
		# if both players have no moves then TIE
		else: 
			black_moves =  self.get_all_moves(self.PLAYER_BLACK)
			white_moves = self.get_all_moves(self.PLAYER_WHITE)
			if black_moves == False and white_moves == False:
				winner = self.TIE  

		self.winner = winner
		return self.winner != self.PLAYER_NEITHER
		
	def get_all_moves(self, player):
		'''return false if player has no moves else returns list of all moves (cell_from, cell_to)'''
		moves = False
		move = Board.NO_MOVES 
		# for each cell try to find a move to pick
		for cell_from in self.get_owned_cells(player):
			for  cell_to in self.get_moves(cell_from):
				if not moves:
					moves = []
				moves.append((cell_from, cell_to))
		return moves

	def draw(self, screen):
		self.wait-= 1
		if self.wait < 0:
			self.wait = 0
		for row in self.grid:
			for cell in row:
				cell.draw(screen)


	def get_intersecting_cell(self, pos):
		for row in self.grid:
			for cell in row:
				if cell.does_intersect(pos):
					return cell
		return None

	def get_owned_cells(self, player):
		return list(self.pieces[player].keys())		

	def get_moves(self, cell):
		'''
			get_moves
			 	find all lines from the current cell to the nearest empty cell such that all cells in between do not 
				have the same owner as the moving cell
				Do this by searching immediate neighbors then following the lines from neighbor to empty while
				owner is the opponent
	 		cell : current cell
	 		Returns a list of cells that are potential moves
		'''
		moves = []
		if cell.owner == self.PLAYER_NEITHER:
			return moves # empty cell!
		i,j = cell.grid_pos
		# get each index of the neighbor and check if the move is valid
		neighbor = None

		for di in range(-1,2):
			for dj in range(-1,2):
				ni, nj = i+di, j+dj
				if (ni, nj) != (i,j):
					# check the neighbor, if it is opponent try to find move
					if ni >= 0 and ni < self.DIMEN and nj >= 0 and nj < self.DIMEN:
						neighbor = self.grid[ni][nj]
						if neighbor.owner != self.PLAYER_NEITHER and neighbor.owner != cell.owner:  
							# get the next cell in the same direction as neighbor 
							search = True
							while search:
								ni, nj = ni+di, nj+dj
								# if next cell is not beyond board
								if ni < 0 or ni >= self.DIMEN or nj < 0 or nj >= self.DIMEN:
									search = False # reached end of board 
								else:
									next_cell = self.grid[ni][nj]
									 # if found empty cell!
									if next_cell.owner == self.PLAYER_NEITHER:
										# add this cell to moves
										# if next_cell does not result in surrounding opponent then valid
										# for each neighbor of next-cell, count owned cells 		
										moves.append(next_cell)
										search = False
									elif next_cell.owner == cell.owner: # not opponent, cannot jump
										search = False

									#else keep searching
		return moves

	# def is_move(self, move):
	# 	valid = False
	# 	cell_from, cell_to = move
	# 	if cell_to.owner == self.PLAYER_NEITHER:
	# 		i,j = cell_from.grid_pos
	# 		di, dj = self.get_move_delta(move)
	# 		ni, nj = i+di, j+dj
	# 		if (ni, nj) != (i,j):
	# 			valid = True
	# 			next_cell = None
	# 			while valid and \
	# 					ni >= 0 and ni < self.DIMEN and nj >= 0 and nj < self.DIMEN:
	# 				next_cell = self.grid[ni][nj]
	# 				# if cell is owned by opponent 
	# 				if next_cell.owner == cell_from.owner or next_cell.owner == self.PLAYER_NEITHER: 
	# 					valid  = False
	# 				ni, nj = ni+di, nj+dj
	# 			# empty cell broke loop
	# 			if next_cell.owner == self.PLAYER_NEITHER:
	# 				valid = True
	# 			else:
	# 				valid = False
	# 	return valid

	def move_piece(self, move):
		self.wait = self.WAIT_TIME
		# flips all cells in between the line segment created by  to and from 
		# try for each cell from owned cells		
		cell_from, cell_to = move
		i, j =  cell_from.grid_pos
		di, dj = self.get_move_delta(move)
		ni, nj = i+di, j+dj
		next_cell = None
		continue_flipping = True
		while continue_flipping  and \
				ni >= 0 and ni < self.DIMEN and nj >= 0 and nj < self.DIMEN:
			next_cell = self.grid[ni][nj]
			# if cell is owned by opponent 
			if next_cell.owner != cell_from.owner and next_cell.owner != self.PLAYER_NEITHER: 
				# add piece to new owner remove from old
				self.pieces[cell_from.owner][next_cell] = 1
				del self.pieces[next_cell.owner][next_cell]
				next_cell.flip() # flip owner and start animation
				# add bonus
				if next_cell.bunny:
					self.player_bonuses[cell_from.owner]+=cell_from.BONUS
			else:
				continue_flipping  = False
			ni, nj = ni+di, nj+dj
		cell_to.owner = cell_from.owner
		self.pieces[cell_from.owner][cell_to] = 1


	def move(self, player, cell_to):
		'''
		for each player move from any owned cell to destination cell
		'''
		moves = self.get_all_moves(player)
		for move in moves:
			if move[1] == cell_to:
				self.move_piece(move)
				if cell_to.bunny:
					self.player_bonuses[cell_to.owner]+=cell_to.BONUS
					cell_to.plus_one_frame = 1


	def get_move_delta(self, move):
		cell_from, cell_to = move
		i, j =  cell_from.grid_pos
		fi, fj =  cell_to.grid_pos
		di, dj = (fi-i), (fj-j)
		# clamp directions to ints between [-1,1]
		if di > 1:
			di = 1
		elif di < 0:
			di = -1
		if dj > 1:
			dj = 1
		elif dj < 0:
			dj = -1
		return (di, dj)


class AI:
	def __init__(self, player, board):
		self.player = player
		# reference to the board
		self.board = board
		random.seed(datetime.datetime.now())

	def get_move(self):
		'''
			returns board state or potential move (cell_from, cell_to)
		'''
		#stall 
		move = Board.GAME_OVER
		if not self.board.check_game_over():
			move = Board.NO_MOVES # does not own any cells!
			get_all_moves = self.board.get_all_moves(self.player)
			#shuffle the cells
			if get_all_moves:
				moves = []
				while len(get_all_moves) > 0:
					moves.append(get_all_moves.pop(random.randint(0, len(get_all_moves)-1)))
				move = moves[random.randint(0, len(moves)-1)]
		return move


# ---------------------------- Menu Class ------------------------------------
class Menu:
	TEXT_COLOR = [0,55,250]
	BUTTON_COLOR = [155,25,2]
	HIGHLIGHT_COLOR = [255,255,0]
	SMALL_SIZE = 6
	MED_SIZE = 8
	LARGE_SIZE = 10
	# ---------------------------- Menu Definitions ------------------------------------
	def __init__(self, offset):
		self.pos = offset
		self.font = pygame.font.SysFont(None, 48)
		self.buttons = {}
		# start buttons
		start_buttons = ['START', 'SIZE'] 
		size = (120, 32)
		offset =  offset[0] - size[0], offset[1]-size[1]

		for i in range(0,len(start_buttons)):
			label = start_buttons[i] 
			text = self.font.render(label, True, self.TEXT_COLOR, self.BUTTON_COLOR)
			text = pygame.transform.scale(text, size)
			pos = (offset[0], offset[1]+size[1]*i)
			self.buttons[label] = (text, pos, False)

		size_end = size[0]		
		#sizes
		self.sizes = ['S', 'M', 'L'] 
		for i in range(0,len(self.sizes)):
			label = self.sizes[i] 
			text = self.font.render(label, True, self.TEXT_COLOR, self.BUTTON_COLOR)
			text = pygame.transform.scale(text, (int(size[0]/4), size[1]  ))
			pos = (offset[0]+size_end+size[0]/4*(i+1), pos[1])
			
			self.buttons[label] = (text, pos, False)

		# ---- game_over buttons ----
		game_over_buttons = ['RETRY', 'EXIT'] 
		# exit is at same location as start, but is displayed at game_over only
		for i in range(0,len(game_over_buttons)):
			label = game_over_buttons[i] 
			text = self.font.render(label, True, self.TEXT_COLOR, self.BUTTON_COLOR)
			text = pygame.transform.scale(text, size)
			pos = (offset[0], offset[1]+size[1]*i)
			self.buttons[label] = (text, pos, True)

		# selected size button
		self.selected_size = 'S' 


	def draw(self, screen, game_over=False):
			keys  = list(self.buttons.keys())
			for i in range(0, len(keys)):
				key = keys[i]
				text, pos, is_game_over = self.buttons[key]
				if game_over == is_game_over:
					screen.blit(text, pos)
					if key == self.selected_size:
						rect = [pos[0],pos[1],text.get_width(),text.get_height()]
						pygame.draw.rect(screen, self.HIGHLIGHT_COLOR, rect, 3)

	
	def select_size(self, size):
		if size in self.sizes:
			self.selected_size = size 

	
	def get_size(self):
		if self.selected_size == 'S':
			return self.SMALL_SIZE 
		elif self.selected_size == 'M':
			return self.MED_SIZE
		elif self.selected_size == 'L':
			return self.LARGE_SIZE

	
	def get_intersecting_button(self, pos, game_over=False):
		keys  = list(self.buttons.keys())
		for i in range(0, len(keys)):
			text, button_pos, is_game_over  = self.buttons[keys[i]]
			size = text.get_width(),text.get_height()
			if game_over == is_game_over:
				if (pos[0] > button_pos[0] and pos[0] < button_pos[0]+size[0]) \
					and (pos[1] > button_pos[1] and pos[1] < button_pos[1]+size[1]):
					return keys[i]
	
		return None

# ---------------------------- ScoreBoard Class ------------------------------------
class ScoreBoard:
	TEXT_COLOR = [0,155,250]
	# ---------------------------- ScoreBoard Definitions ------------------------------------
	def __init__(self, pos):
		self.font_height = 34
		self.font = pygame.font.SysFont(None, self.font_height)
		self.pos = pos
		self.radius = self.font_height//4

	def draw(self, screen, board, current_player):
		black_score = str(board.get_score(Board.PLAYER_BLACK))
		white_score = str(board.get_score(Board.PLAYER_WHITE))
		gap = 10
		black_text = self.font.render('Black', True,  self.TEXT_COLOR) 
		black_text_pos = (self.pos[0]+gap*2+self.radius*2, self.pos[1])
		black_score_text = self.font.render(black_score, True,  self.TEXT_COLOR) 
		black_score_text_pos = [gap+black_text_pos[0]+black_text.get_width(), black_text_pos[1]]
		# draw player 2 text
		white_text = self.font.render('White', True,  self.TEXT_COLOR)
		white_text_pos = (self.pos[0]+gap*2+self.radius*2, self.pos[1]+white_text.get_height())

		white_score_text = self.font.render(white_score, True,  self.TEXT_COLOR) 
		white_score_text_pos = [gap+white_text_pos[0]+white_text.get_width(), white_text_pos[1]]


		# set score text pos to align along y axis
		if white_score_text_pos[0] > black_score_text_pos[0]:
			black_score_text_pos[0] = white_score_text_pos[0] 
		else:
			white_score_text_pos[0] = black_score_text_pos[0]  
		#draw current turn by drawing small circle near score
		if current_player == Board.PLAYER_BLACK: 
			midpoint = (self.pos[0]+self.radius+gap, black_score_text_pos[1] + self.radius)
			color= Board.BLACK 
		else:
			midpoint = (self.pos[0]+self.radius+gap, white_score_text_pos[1] + self.radius)
			color= Board.WHITE
		
		screen.blit(black_text,black_text_pos)
		screen.blit(white_text,white_text_pos)
		screen.blit(black_score_text,black_score_text_pos)
		screen.blit(white_score_text,white_score_text_pos)
		pygame.draw.circle(screen, color, midpoint,self.radius,0)
		pygame.draw.circle(screen, Board.Cell.HIGHLIGHT_PIECE_COLOR, midpoint,self.radius,0)

# ---------------------------- MMain Entry Point ------------------------------------
def main():
	# window and board size and position settings
	BG_COLOR = [5,5,32]
	border = 2
	size = [550, 650]
	offset = (border, size[1]//15)
	# board variables
	board = None
	ai = None 
	score_board = None
	# game and gui state variables
	player = None
	selected_cell = None 
	current_player = None
	winner = None
	exit = False
	draw_board =False
	start_new_game = False
	game_over = False
	# setup
	pygame.init()
	screen = pygame.display.set_mode(size)
	pygame.display.set_caption("Othello/Reversi ")
	clock = pygame.time.Clock()
	menu = Menu((size[0]//2,size[1]//2))
	hud_font = pygame.font.SysFont(None, 34)
	hud_size = (75, 34)
	hint_text = hud_font.render('Show Hint', True, Menu.TEXT_COLOR, Menu.BUTTON_COLOR)
	hint_button = (border, border,hud_size[0] ,hud_size[1])
	exit_text = hud_font.render('Exit', True, Menu.TEXT_COLOR, Menu.BUTTON_COLOR)
	exit_button = (size[0]-border-exit_text.get_width(), border, hud_size[0] ,hud_size[1])
	hud = [hint_button, exit_button]
	# main while loop
	while not exit:
		mouse_clicked = False
		clock.tick(10)
		for event in pygame.event.get(): 
			if event.type == pygame.QUIT:
				exit=True 
			elif event.type == pygame.KEYDOWN:
				a = None # do nothing
			elif event.type == pygame.MOUSEBUTTONDOWN:
				# if it is the current players turn!
				mouse_clicked = True
				mouse_pos = pygame.mouse.get_pos()

		# if new game is started reinitialize board and player vars
		if start_new_game:
			current_player = random.randint(Board.PLAYER_BLACK, Board.PLAYER_WHITE)
			# set dimension before creating
			Board.DIMEN = menu.get_size()
			board = Board( offset, (size[0], size[0])  ) 
			score_board = ScoreBoard((offset[0], offset[1]+size[0]))
			player = Board.PLAYER_BLACK
			ai = AI(Board.PLAYER_WHITE, board) 
			selected_cell = None 
			winner = None
			show_start_menu = False
			start_new_game = False

		# clear screen
		screen.fill(BG_COLOR)

		if draw_board:
			if winner != None:
				game_over = True
				# set winner if game over
			elif board.check_game_over():
				winner = board.get_winner()
				# display winner!
			# make decision
			else:
				if not board.is_waiting():
					# player selection and is players turn
					if current_player == player:
						all_player_moves = board.get_all_moves(player)
						if not all_player_moves:
							current_player = board.toggle_player(current_player)
						# if player is selecting
						elif mouse_clicked:  
							#pick up piece an high light moves
							if selected_cell == None:
								cell = board.get_intersecting_cell(mouse_pos)
								# select piece if it is owned by player
								if cell and cell.owner == current_player:
									selected_cell = cell 
									potential_moves = board.get_moves(selected_cell)
							else:
								#try to place piece at cell
								cell = board.get_intersecting_cell(mouse_pos)
								if cell in potential_moves:
									# add the piece to the cell and flip all pieces in between
									board.move(current_player, cell)
									current_player = board.toggle_player(current_player)
								# unselect current piece if not selecting new piece
								if cell and cell.owner == current_player:
									selected_cell = cell 
								else:
									selected_cell = None

					elif current_player == ai.player:
						move = ai.get_move()
						if move != Board.NO_MOVES:
							board.move(current_player,move[1])
						# update current player
						current_player = board.toggle_player(current_player)
			#draw board
			board.draw(screen)
			# if cell is celected highlight current piece, and any potential moves
			#if draw move hints by selecting a random cell that has a move
			screen.blit(hint_text, hint_button)
			screen.blit(exit_text, exit_button)
			score_board.draw(screen,board, current_player)
			if mouse_clicked:
				hit_button = None
				for button in hud:
					if (mouse_pos[0] > button [0] and mouse_pos[0] < button [0]+button [2]) \
						and (mouse_pos[1] > button [1] and mouse_pos[1] < button [1]+button[3]): 
						hit_button = button

				if hit_button is hint_button:
					all_moves = board.get_all_moves(current_player)
					selected_cell = all_moves[random.randint(0, len(all_moves)-1)][0]
				elif hit_button is exit_button: 
					del ai; del board; del score_board
					start_new_game = False
					draw_board = False

			if selected_cell:
				# highlight the piece
				potential_moves = board.get_moves(selected_cell)
				selected_cell.draw_highlight(screen, True)
				for move in potential_moves:
					move.draw_highlight(screen)

		# else do not draw board
		else: # show_start_menu:
			if mouse_clicked: # handle menu input
				button_id = menu.get_intersecting_button(mouse_pos)
				# Start game ,create board variables!
				if button_id == 'START':
					start_new_game = True
					draw_board = True
				#tries to select size
				else:
					menu.select_size(button_id)
			menu.draw(screen)
		
		if game_over: 
			menu.draw(screen, True)
			if mouse_clicked:
				button = menu.get_intersecting_button(mouse_pos, True)
				if button == 'RETRY':
					del ai; del board; del score_board
					start_new_game = True
					game_over = False
				elif button == 'EXIT':
					del ai; del board; del score_board
					start_new_game = False
					game_over = False
					draw_board = False

		pygame.display.flip()


if __name__ == '__main__':
	main()
