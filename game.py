import tkinter as tk
from PIL import Image, ImageTk
from board import all_ranks, all_files, WHITE, BLACK, Board, Move, other

#TODO:
# 0) winning/losing/drawing (via info pane)
# 1) promotion (via info pane)
# 2) print moves (via info pane)
# 3) undo move(s) (via info pane)
# 4) support arbitrary config files
# 5) testing
human_colors = {WHITE: 'white', BLACK: 'black'}

def click_handler(r_ind, c_ind, game):
	def handle_click(event):
		
		grid_row, grid_col = game.bcoords2gcoords(r_ind, c_ind)
		clicked_frame = game.board_frame.grid_slaves(row=grid_row, column=grid_col)[0]
		if game.selected is None:
			piece = game.get_piece(r_ind, c_ind)
			if piece and piece.color == game.turn:
				game.select_sq(r_ind, c_ind, clicked_frame)
		else:
			r_sel, c_sel = game.selected
			grid_r_sel, grid_c_sel = game.bcoords2gcoords(r_sel, c_sel)
			sel_frame = game.board_frame.grid_slaves(row=grid_r_sel, column=grid_c_sel)[0]

			if not (r_sel == r_ind and c_sel == c_ind):
				# abstraction to deal with castling and en passant
				mv = game.create_move(game.selected, (r_ind, c_ind))
				if mv.is_valid():
					mv.make_move()
					game.turn = other(game.turn)
					game.notif_label.grid_forget()
					game.check_finished()	
					game.update_all()
				game.selected = None
			game.deselect_sq(sel_frame)

		#print('square at row {} col {} was clicked'.format(r_ind, c_ind))
		#print('square {}{} clicked'.format(all_files[c_ind], all_ranks[r_ind]))
	return handle_click

class Game:

	def __init__(self, board):
		self.board = board

		## Tkinter stuff
		self.window = tk.Tk()
		self.board_frame = tk.Frame(master=self.window, width=400, height=400, bg="red")
		self.info_frame = tk.Frame(master=self.window, width=200, bg="blue")
		self.board_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		self.info_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
		self.all_pimgs = {} #PhotoImage cache

		## state used for turns
		self.turn = WHITE # white goes first
		self.selected = None # no piece (square) selected


		letter_frame = tk.Frame(master=self.board_frame, bg='white')
		letter_frame.grid(row=0, column=0) # blank corner
		letter_frame = tk.Frame(master=self.board_frame, bg='white')
		letter_frame.grid(row=len(self.board.board_lst), column=0) # blank corner
		## put pieces on board
		for r_ind, row in enumerate(self.board.board_lst):
			self.board_frame.columnconfigure(r_ind + 1, weight=1, minsize=75) #, minsize=50
			self.board_frame.rowconfigure(r_ind + 1, weight=1, minsize=75)
			for c_ind, piece in enumerate(row):
				if r_ind == 0:
					letter_frame = tk.Frame(master=self.board_frame, bg='white')
					letter_frame.grid(row=0, column=c_ind + 1)
					letter_lbl = tk.Label(master=letter_frame, text=all_files[c_ind])
					letter_lbl.pack(fill=tk.BOTH, expand=True)
				if c_ind == 0:
					letter_frame = tk.Frame(master=self.board_frame, bg='white')
					letter_frame.grid(row=r_ind + 1, column=0)

					letter_lbl = tk.Label(master=letter_frame, text=all_ranks[r_ind])
					letter_lbl.pack(fill=tk.BOTH, expand=True)
					letter_frame.lbl = letter_lbl

				if r_ind == len(self.board.board_lst) - 1:
					letter_frame = tk.Frame(master=self.board_frame, bg='white')
					letter_frame.grid(row=len(self.board.board_lst) + 1, column=c_ind + 1)
					letter_lbl = tk.Label(master=letter_frame, text=all_files[c_ind])
					letter_lbl.pack(fill=tk.BOTH, expand=True)

				color_switch = 0 if self.turn == WHITE else 1
				color = "saddle brown" if (r_ind + c_ind) % 2 == color_switch else "navajo white"
				handler = click_handler(r_ind, c_ind, self)
				frame = tk.Frame(master=self.board_frame, relief=tk.GROOVE, borderwidth=1, bg=color)
				frame.bg = color
				frame.displayed_label = None
				frame.bind("<Button-1>", handler)
				frame.grid(row=r_ind + 1, column=c_ind + 1, sticky="nsew")

				#self.update_square(r_ind, c_ind)

		## Add info pane stuff 
		self.turn_label = tk.Label(self.info_frame, text='Turn: White')
		self.turn_label.grid(row=0, column=0, sticky='nsew')

		# Move List (see attributions for code source)

		frame_canvas = tk.Frame(self.info_frame)
		frame_canvas.grid(row=1, column=0, pady=(5, 0), sticky='nw')
		frame_canvas.grid_rowconfigure(0, weight=1)
		frame_canvas.grid_columnconfigure(0, weight=1)
		# Set grid_propagate to False to allow 5-by-5 buttons resizing later
		frame_canvas.grid_propagate(False)

		# Add a canvas in that frame
		canvas = tk.Canvas(frame_canvas, bg="yellow")
		canvas.grid(row=0, column=0, sticky="news")

		# Link a scrollbar to the canvas
		vsb = tk.Scrollbar(frame_canvas, orient="vertical", command=canvas.yview)
		vsb.grid(row=0, column=1, sticky='ns')
		canvas.configure(yscrollcommand=vsb.set)

		# Create a frame to contain the buttons
		frame_labels = tk.Frame(canvas, bg="blue")
		canvas.create_window((0, 0), window=frame_labels, anchor='nw')

		# Add 1 by 2 moves to the frame
		
		moves = [['White', 'Black']] #+ [['a', 'b'] for _ in range(10)]
		rows = len(moves)
		columns = len(moves[0])
		for i in range(0, rows):
		    for j in range(0, columns):
		        moves[i][j] = tk.Label(frame_labels, text=moves[i][j])
		        if i == 0:
		        	moves[i][j].config(bg='orange')
		        moves[i][j].grid(row=i, column=j, sticky='news')

		# Update buttons frames idle tasks to let tkinter calculate buttons sizes
		frame_labels.update_idletasks()
		self.frame_labels = frame_labels

		# Resize the canvas frame to show exactly 5-by-5 labels and the scrollbar
		first5columns_width = sum([moves[0][j].winfo_width() for j in range(columns)])
		first5rows_height = moves[0][0].winfo_height() * 5
		frame_canvas.config(width=first5columns_width + vsb.winfo_width(),
		                    height=first5rows_height)

		# Set the canvas scrolling region
		canvas.config(scrollregion=canvas.bbox("all"))
		self.moves_canvas = canvas

		self.notif_label = tk.Label(self.info_frame, text='')


		self.update_all()
				# TODO: at some point, add letters/numbers on the outside
				#if (r_ind == len(self.board.board_lst) - 1):
				#	mini_text = tk.Label(master=frame, text=all_files[c_ind])
					#mini_text.grid(row=0, column=0, sticky="se")

	def get_piece_img(self, piece):
		key = str(piece)
		if key not in self.all_pimgs:
			img = Image.open(piece.get_img())
			render = ImageTk.PhotoImage(img)
			self.all_pimgs[key] = render
			return render
		return self.all_pimgs[key]

	def get_piece(self, r, c):
		return self.board.board_lst[r][c]

	def bcoords2gcoords(self, row, col):
		grid_row = row + 1 if self.turn == BLACK else len(all_ranks) - row
		return grid_row, col + 1

	def update_square(self, row, col):
		piece = self.board.board_lst[row][col]


		grid_row, grid_col = self.bcoords2gcoords(row, col)
		frame = self.board_frame.grid_slaves(row=grid_row, column=grid_col)[0]

		color_switch = 0 #if self.turn == BLACK else 1
		color = "saddle brown" if (row + col) % 2 == color_switch else "navajo white"
		frame.config(bg=color)
		frame.bg = color

		handler = click_handler(row, col, self)
		frame.bind("<Button-1>", handler)

		if frame.displayed_label is not None:
			frame.displayed_label.pack_forget()
			frame.displayed_label.destroy()
			frame.displayed_label = None

		if piece is not None:
			img = self.get_piece_img(piece)
			label = tk.Label(master=frame, image=img, bg=frame.bg)
			label.photo = img
			label.bind("<Button-1>", handler)
			label.pack(fill=tk.BOTH, expand=True)

			frame.displayed_label = label

	def update_all(self):
		self.turn_label.config(text='Turn: {}'.format(human_colors[self.turn]))
		for txt in self.frame_labels.grid_slaves():
			txt.grid_forget()
			txt.destroy()

		mv_texts = ['White', 'Black'] + self.board.moves_as_text()
		for i, mv_text in enumerate(mv_texts):
			row = (i//2)
			col = i % 2
			lbl = tk.Label(self.frame_labels, text=mv_text)
			if row == 0:
				lbl.config(bg='orange')
			lbl.grid(row=row, column=col, sticky='news')
		if col == 0:
			lbl = tk.Label(self.frame_labels, text='')
			lbl.grid(row=row, column=1, sticky='news')

		self.frame_labels.update_idletasks()

		# Set the canvas scrolling region
		self.moves_canvas.config(scrollregion=self.moves_canvas.bbox("all"))
		

		self.frame_labels
		for r_ind, row in enumerate(self.board.board_lst):
			frame = self.board_frame.grid_slaves(row=r_ind + 1, column=0)[0]
			letter_ind = r_ind if self.turn == BLACK else len(all_ranks) - r_ind - 1
			frame.lbl.config(text=all_ranks[letter_ind])
			for c_ind, piece in enumerate(row):
				self.update_square(r_ind, c_ind)

	def select_sq(self, r_ind, c_ind, frame):
		self.selected = (r_ind, c_ind)
		frame.config(highlightthickness=2)
		frame.config(highlightbackground='red')

	def deselect_sq(self, frame):
		self.selected = None
		frame.config(highlightthickness=0)

	def create_move(self, src, dst):
		return Move(src, dst, self.board)

	def check_finished(self):
		

		in_check = self.board.in_check(self.turn)
		if not self.board.player_has_moves(self.turn):
			if in_check:
				self.notif_label.config(text='{} wins!'.format(human_colors[other(self.turn)]))
				self.board.notify_last_move_checkmate()
				print('The {} player wins!'.format(human_colors[other(self.turn)]))
			else:
				self.notif_label.config(text='stalemate!')
				print('Stalemate! It is a draw!!')
			self.notif_label.grid(row=2, column=0, sticky='news')
		elif in_check:
			self.notif_label.config(text='check!')
			self.notif_label.grid(row=2, column=0, sticky='news')
			self.board.notify_last_move_check()
		

	def display_board(self):
		self.window.mainloop()


class Player:
	def get_move(board):
		return None

class HumanPlayer(Player):
	def get_move(board):
		return None

def play_game(board):
	pass
