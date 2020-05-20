import tkinter as tk
from PIL import Image, ImageTk
from board import all_ranks, all_files, WHITE, BLACK, Board, Move

def click_handler(r_ind, c_ind, board):
	def handle_click(event):
		print('square at row {} col {} was clicked'.format(r_ind, c_ind))
	return handle_click

class Game:

	def __init__(self, board):
		self.board = board
		self.window = tk.Tk()
		self.board_frame = tk.Frame(master=self.window, width=400, height=400, bg="red")
		self.info_frame = tk.Frame(master=self.window, width=200, bg="blue")
		self.board_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		self.info_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

		self.turn = WHITE # white goes first
		self.all_pimgs = {} #PhotoImage cache

		for r_ind, row in enumerate(self.board.board_lst):
			self.board_frame.columnconfigure(r_ind, weight=1, minsize=75) #, minsize=50
			self.board_frame.rowconfigure(r_ind, weight=1, minsize=75)
			for c_ind, piece in enumerate(row):
				color = "saddle brown" if (r_ind + c_ind) % 2 == 1 else "navajo white"
				handler = click_handler(r_ind, c_ind, self.board)
				frame = tk.Frame(master=self.board_frame, relief=tk.GROOVE, borderwidth=1, bg=color)
				frame.bg = color
				frame.bind("<Button-1>", handler)
				frame.grid(row=r_ind, column=c_ind, sticky="nsew")

				if piece is not None:
					self.add_piece(piece, (r_ind, c_ind))


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


	def add_piece(self, piece, loc):
		frame = self.board_frame.grid_slaves(row=loc[0], column=loc[1])[0]
		img = self.get_piece_img(piece)
		handler = click_handler(loc[0], loc[1], self.board)
		label = tk.Label(master=frame, image=img, bg=frame.bg)
		label.photo = img
		label.bind("<Button-1>", handler)
		label.pack(fill=tk.BOTH, expand=True)

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
