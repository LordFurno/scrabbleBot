import twl
import random
from itertools import permutations

def getMove(rack, board_state, bonus_squares):
    """
    A simple bot that:
    1. Finds anchor points (squares next to existing tiles)
    2. Tries to form valid words using tiles from rack
    3. Returns a valid move found

    This is basically brute forcing what words are possible given the setup. 
    HOWEVER, this bot is not good. It does not check for legal crosswords (words formed perpendicular to the new word),
    nor is it that fast/smart. 
    It also doesn't address the bonus squares, or blank tiles (denoted as "?")

    This is just a way to get an idea of how to approach your bot, as well as the formatting.
    """

    #Check if board is empty (first move)
    board_empty = all(board_state[r][c] == "" for r in range(15) for c in range(15))
    
    if board_empty:
        #First move, must use center square
        move = find_first_move(rack)
        if move:
            return move
        return [] #Pass if no valid first move
    
    #Find all possible moves
    possibleMoves = []
    #A move is formatted as a list of tuples (r,c,ch), where r is the row in the board, 
    #c is the column, and ch is the character (uppercase)
    
    #Try to extend existing words horizontally and vertically
    for r in range(15):
        for c in range(15):
            if board_state[r][c] == "":
                #Check if this is an anchor point (next to an existing tile)
                if is_anchor(r, c, board_state):
                    #Try horizontal placements
                    moves = tryHorizontalPlacements(r, c, rack, board_state)
                    possibleMoves.extend(moves)
                    
                    #Try vertical placements
                    moves = tryVerticalPlacements(r, c, rack, board_state)
                    possibleMoves.extend(moves)
    

    if possibleMoves:
        #Just pick a random valid move for simplicity
        #A better bot would score each move
        return random.choice(possibleMoves)
    
    return [] #Pass if no valid move found

def find_first_move(rack):
    """
    Find a valid word for the first move (must include center square 7,7)
    """
    #Try to form words of length 2-7
    for length in range(min(7, len(rack)), 1, -1):
        #Try different combinations
        
        for perm in permutations(rack, length):
            word = ''.join(perm).upper()
            if twl.check(word.lower()):
                #Place word horizontally centered on (7,7)
                #Lets start at column 7
                move = []
                for i, letter in enumerate(perm):
                    move.append((7, 7 + i, letter.upper()))
                return move
    
    return None

def is_anchor(r, c, board_state):
    """Check if position (r,c) is adjacent to an existing tile"""
    if r > 0 and board_state[r-1][c] != "":
        return True
    if r < 14 and board_state[r+1][c] != "":
        return True
    if c > 0 and board_state[r][c-1] != "":
        return True
    if c < 14 and board_state[r][c+1] != "":
        return True
    return False

def tryHorizontalPlacements(row, col, rack, board_state):
    """Try to place tiles horizontally starting at or including (row, col)"""
    moves = []
    
    #Try words of different lengths
    for length in range(2, min(8, len(rack) + 1)):
        #Try different combinations from rack
        for perm in permutations(rack, min(length, len(rack))):
            #Try placing at different positions
            for start_col in range(max(0, col - length + 1), min(15 - length + 1, col + 1)):
                if start_col + length > 15:
                    #Out of range
                    continue
                
                #Build the word including existing tiles
                word_tiles = []
                move = []
                valid = True
                
                for i in range(length):
                    c = start_col + i
                    if board_state[row][c] != "":
                        #Use existing tile
                        word_tiles.append(board_state[row][c].upper())

                    elif len(move) < len(perm):
                        #Place new tile
                        letter = perm[len(move)]
                        word_tiles.append(letter.upper())
                        move.append((row, c, letter.upper()))

                    else:
                        valid = False
                        break
                
                if not valid or not move:
                    continue
                
                #Check if word is valid
                word = ''.join(word_tiles)
                if len(word) >= 2 and twl.check(word.lower()):
                    #Quick validity check: at least one new tile should be at anchor
                    if any(r == row and c == col for r, c, ch in move):
                        moves.append(move)
    
    return moves

def tryVerticalPlacements(row, col, rack, board_state):
    """Try to place tiles vertically starting at or including (row, col)"""
    moves = []
    
    #Try words of different lengths
    for length in range(2, min(8, len(rack) + 1)):
        #Try different combinations from rack
        for perm in permutations(rack, min(length, len(rack))):
            #Try placing at different positions
            for start_row in range(max(0, row - length + 1), min(15 - length + 1, row + 1)):
                if start_row + length > 15:
                    continue
                
                #Build the word including existing tiles
                word_tiles = []
                move = []
                valid = True
                
                for i in range(length):
                    r = start_row + i
                    if board_state[r][col] != "":
                        #Use existing tile
                        word_tiles.append(board_state[r][col].upper())
                    elif len(move) < len(perm):
                        #Place new tile
                        letter = perm[len(move)]
                        word_tiles.append(letter.upper())
                        move.append((r, col, letter.upper()))
                    else:
                        valid = False
                        break
                
                if not valid or not move:
                    continue
                
                #Check if word is valid
                word = ''.join(word_tiles)
                if len(word) >= 2 and twl.check(word.lower()):
                    #Quick validity check: at least one new tile should be at anchor
                    if any(r == row and c == col for r, c, ch in move):
                        moves.append(move)
    
    return moves


