import pygame
import numpy
import random
import twl
class LetterBag():

    dist = {
        "A": 9, "B": 2, "C": 2, "D": 4, "E": 12,
        "F": 2, "G": 3, "H": 2, "I": 9, "J": 1,
        "K": 1, "L": 4, "M": 2, "N": 6, "O": 8,
        "P": 2, "Q": 1, "R": 6, "S": 4, "T": 6,
        "U": 4, "V": 2, "W": 2, "X": 1, "Y": 2,
        "Z": 1, "?": 2  
    }
    #? are blanks
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.tiles = []
        for letter,count in self.dist.items():
            self.tiles.extend([letter]*count)
        random.shuffle(self.tiles)
    
    def draw(self,n):
        #Draw n tiles
        drawn = []
        for i in range(n):
            if not self.tiles:
                break
            drawn.append(self.tiles.pop())
        return drawn
    def returnTiles(self, tiles):
        for t in tiles:
            self.tiles.append(t.upper())
        
        random.shuffle(tiles)
    def remainingTiles(self):
        return len(self.tiles)

class Board():
    def __init__(self):
        """
        Attributes:
        bonus (dictionary: List[tuples]): The location of the bonus squares
        state (15x15 matrix): The state of the game, where each letters are
        """
        self.state = [[""]*15 for i in range(15)]
        self.bonus = self._make_bonus_map()
        self.letterScores = {
            **dict.fromkeys(list("AEILNORSTU"), 1),
            **dict.fromkeys(list("DG"), 2),
            **dict.fromkeys(list("BCMP"), 3),
            **dict.fromkeys(list("FHVWY"), 4),
            "K": 5,
            **dict.fromkeys(list("JX"), 8),
            **dict.fromkeys(list("QZ"), 10),
        }
        self.size = 15
        self.blankLocations = []
    

    def _make_bonus_map(self):
        B = {}
        for p in [(0,0),(0,7),(0,14),(7,0),(7,14),(14,0),(14,7),(14,14)]:
            B[p] = "TW"
        # Double word (including center)
        for p in [(1,1),(2,2),(3,3),(4,4),(1,13),(2,12),(3,11),(4,10),
                  (10,4),(11,3),(12,2),(13,1),(13,13),(12,12),(11,11),(10,10),
                  (7,7)]:
            B[p] = "DW"
        # Triple letter
        for p in [(1,5),(1,9),(5,1),(5,5),(5,9),(5,13),
                  (9,1),(9,5),(9,9),(9,13),(13,5),(13,9),
                  (2,6),(2,8),(6,2),(6,6),(6,8),(6,12),
                  (8,2),(8,6),(8,8),(8,12),(12,6),(12,8)]:
            B[p] = "TL"
        # Double letter
        for p in [(0,3),(0,11),(2,0),(2,7),(2,14),(3,2),(3,6),(3,8),(3,12),
                  (6,3),(6,7),(6,11),(7,3),(7,11),(8,3),(8,7),(8,11),(11,2),
                  (11,6),(11,8),(11,12),(12,0),(12,7),(12,14),(14,3),(14,11)]:
            B[p] = "DL"
        return B
    def in_bounds(self, r, c):
        return 0 <= r < self.size and 0 <= c < self.size

    def set_tile(self, r, c, letter):
        self.state[r][c] = letter
    
    def get_tile(self, r, c):
        return self.state[r][c]
    
    def updateBlanks(self, newBlanks):
        self.blankLocations.extend(newBlanks)
    
    
    def is_legal(self, placements, isFirstMove):
        #Returns true or false. If false, it explains why


        
        #First check bounds and if space is empty
        for r,c,ch in placements:
            if not self.in_bounds(r,c):
                return False, f"Position {(r,c)} out of range", {}
            if self.state[r][c] != "":
                return False, f"Position {(r,c)} already occupied", {}
            
            #Make sure letter is valid
            if len(ch)!=1 or  (not ch.isalpha()):
                return False, f"Invalid letter at {(r,c)}: {ch}", {}
        
        #Must be a single row or column, no diagonal placements
        rows = {r for r,c,ch in placements}
        cols = {c for r,c,ch in placements}
        # print(rows)
        # print(cols)
        if len(rows) != 1 or len(cols) != 1:
            if len(placements) == 1:
                pass #This is okay, you can play 1 letter
            elif len(rows)==1 and len(cols)==1 and len(placements)!=1:

                return False, f"Tiles must be in a single row/column", {}

        placement_map = {(r,c): ch for (r,c,ch) in placements}
        pos = {(r,c) for r,c,ch in placements}

        def letter_at(r,c):
            if (r,c) in placement_map:
                return placement_map[(r,c)]
            if self.state[r][c] != "":
                #exsisting thing
                return self.state[r][c]
            return None

        #Figure out orientation
        if len(rows) == 1 and len(cols)>1:
            orientation = "H"
            r = next(iter(rows))
            minC = min(cols)
            maxC = max(cols)

            #Make sure it is consecutive and connected
            for c in range(minC, maxC+1):
                if letter_at(r,c) is None:
                    return False, "Gap in tile placements", {}
        elif len(cols) == 1 and len(rows)>1:
            orientation = "V"
            c = next(iter(cols))
            minR = min(rows)
            maxR = max(rows)

            for r in range(minR, maxR+1):
                if letter_at(r,c) is None:
                    return False, "Gap in tile placements", {}
        else:
            orientation = None
            #There is a single tile
        
        #Has to touch exsisting tile or be placed in the middle
        touch_exsisting = False
        for r,c,ch in placements:
            #Check neigbours
            for dr,dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = r+dr, c+dc
                if self.in_bounds(nr, nc) and self.state[nr][nc]!="":
                    touch_exsisting = True
        if isFirstMove:
            if (7,7) not in pos:
                return False, "First move must cover the center (7,7)", {}
        else:
            if not touch_exsisting:
                return False, "Move must connect to exsisting tiles", {}

        #Now build the word
        mainWord = ""
        mainPos = []
        if orientation == "H" or orientation is None and len(placements)>0:
            #Pick row (for single tile pick its row)
            r = next(iter(rows))
            minC = min(cols)
            #Find start of main word
            start = minC
            while start-1>=0 and letter_at(r, start-1) is not None:
                start -= 1
            #Make word
            word = []
            c = start
            while c < self.size and letter_at(r,c) is not None:
                word.append(letter_at(r,c))
                mainPos.append((r,c))
                c += 1
            mainWord = "".join(ch.upper() for ch in word)
            wordStart = (r, start)
            wordDir = "H"
        if orientation == "V" or (orientation is None and len(placements) == 1 and mainWord == ""):
            if cols:
                c = next(iter(cols))
            else:
                c = placements[0][1]
            minR = min(rows)
            start= minR
            while start-1 >= 0 and letter_at(start-1,c) is not None:
                start-=1
            word = []
            r = start
            while r<self.size and letter_at(r,c) is not None:
                word.append(letter_at(r,c))
                mainPos.append((r,c))
                r+=1
            mainWord = "".join(ch.upper() for ch in word)
            wordStart = (r,c)
            wordDir = "V"
    
        #THe formed word has be at least 2 long
        formed = False
        if len(mainWord) >= 2:
            formed = True
            #Check if valid english word
            if not twl.check(mainWord.lower()):
                return False, f"Main word: {mainWord} not a valid word", {}


        #Check for cross words
        for r,c,ch in placements:
            if wordDir == "H":
                #Check for vertical crosses
                
                start = r
                while start-1 >=0 and letter_at(start-1,c) is not None:
                    start -= 1
                letters = []
                rr = start
                while rr <self.size and letter_at(rr,c) is not None:
                    letters.append(letter_at(rr,c))
                    rr+=1
                if len(letters)>1:
                    formed = True
                    w = "".join(x.upper() for x in letters)
                    #Check valid word again  (w)
                    if not twl.check(w.lower()):
                        return False, f"Cross word: {w} not a valid word", {}
            else:
                #Check horizontal cross
                start = c
                while start-1>=0 and letter_at(r,start-1) is not None:
                    start-=1
                letters = []
                cc = start
                while cc<self.size and letter_at(r,cc) is not None:
                    letters.append(letter_at(r,cc))
                    cc+=1
                
                if len(letters)>1:
                    formed = True
                    w = "".join(x.upper() for x in letters)
                    #Check if valid word
                    if not twl.check(w.lower()):
                        return False, f"Cross word: {w} not a valid word", {}
        if not formed:
            return False, "Move does not form any word of length>=2", {}
        

        details = {
            "placement_map": placement_map,
            "pos": pos,
            "mainWord": mainWord,
            "wordStart": wordStart,
            "wordDir": wordDir,
            "wordPos": mainPos

        }
        return True, "", details

    def score_move(self, placements, validate, isFirstMove):
        #Placements is a list [(r,c, letter)]
        #This scores the move assuming that it is a valid move

        if validate:
            legal, msg, details = self.is_legal(placements, isFirstMove)
            if not legal:
                raise ValueError(f"Invalid Move: {msg}")
        else:
            legal, msg, details = self.is_legal(placements,isFirstMove)

        if not legal:
            return False

        placement_map = details["placement_map"]
        pos = details["pos"]
        mainPositions = details["wordPos"]
        mainWord = details["mainWord"]
        mainStart = details["wordStart"]
        mainDir = details["wordDir"]

        def baseValue(ch):
            if ch == "?":
                #Blank square
                return 0
            else:
                return self.letterScores.get(ch.upper(),0)
            
        def letter_at(r,c):
            if (r,c) in placement_map:
                return placement_map[(r,c)]
            if self.state[r][c] != "":
                #exsisting thing
                return self.state[r][c]
            return None

        #Score main word
        mainLetterVals = []
        mainWordMult = 1

        for r,c in mainPositions:
            ch = letter_at(r,c)
            new = (r,c) in pos #Not reused from exsisting letters

            letterMult = 1
            if (r,c) in self.blankLocations:
                base = 0
            else:
                base = baseValue(ch)
                
            if new:
                bonus = self.bonus.get((r,c))
                if bonus == "DL":
                    letterMult = 2
                elif bonus == "TL":
                    letterMult = 3
                elif bonus == "DW":
                    mainWordMult *= 2
                elif bonus == "TW":
                    mainWordMult *= 3
            mainLetterVals.append(base*letterMult)
        mainWordScore = sum(mainLetterVals) * mainWordMult
        #Score cross words
        crossWords = []
        for r,c,ch in placements:
            if mainDir == "H":
                #Vertical crosses
                start = r
                while start-1>=0 and letter_at(start-1,c) is not None:
                    start -= 1
                rr = start
                letters = []
                positions = []
                while rr<self.size and letter_at(rr,c) is not None:
                    letters.append(letter_at(rr,c))
                    positions.append((rr,c))
                    rr+=1
                
                if len(letters)>1:
                    cwScore = 0
                    cwWordMult = 1
                    for rrr,ccc in positions:
                        ch2 = letter_at(rrr,ccc)
                        new = (rrr,ccc) in pos
                        lm = 1
                        if (rrr,ccc) in self.blankLocations:
                            lv = 0
                        else:
                            lv = baseValue(ch2)
                        if new:
                            bonus = self.bonus.get((rrr,ccc))
                            if bonus == "DL":
                                lm = 2
                            elif bonus == "TL":
                                lm = 3
                            elif bonus == "DW":
                                cwWordMult *= 2
                            elif bonus == "TW":
                                cwWordMult *= 3
                        cwScore += lv*lm #letter value * letter multiplier
                    cwScore *= cwWordMult 
                    crossWords.append(("".join(x.upper() for x in letters),(start,c),"V", cwScore))
            else:
                #Horizontal crosses
                start = c
                while start-1>=0 and letter_at(r,start-1) is not None:
                    start-=1
                cc = start
                letters = []
                positions = []
                while cc<self.size and letter_at(r,cc) is not None:
                    letters.append(letter_at(r,cc))
                    positions.append((r,cc))
                    cc += 1
                if len(letters)>1:
                    cwScore = 0
                    cwWordMult = 1
                    for (rrr, ccc) in positions:
                        ch2 = letter_at(rrr, ccc)
                        new = (rrr, ccc) in pos
                        lm = 1
                        
                        if (rrr,ccc) in self.blankLocations:
                            lv = 0
                        else:
                            lv = baseValue(ch2)
                        if new:
                            bonus = self.bonus.get((rrr, ccc))
                            if bonus == "DL":
                                lm = 2
                            elif bonus == "TL":
                                lm = 3
                            elif bonus == "DW":
                                cwWordMult *= 2
                            elif bonus == "TW":
                                cwWordMult *= 3
                        cwScore += lv*lm
                    cwScore *= cwWordMult
                    crossWords.append(("".join(x.upper() for x in letters),(r,start),"H", cwScore))
        totalCross = sum(i[3] for i in crossWords)
        totalScore = mainWordScore + totalCross

        bingo = len(pos)==7
        if bingo:
            totalScore += 50
        
        #Update tiles
        for r,c,ch in placements:
            self.set_tile(r,c,ch)
            if (r,c) in self.bonus:
                del self.bonus[(r,c)]
        
        return {
            "score": totalScore,
            "mainWordInfo": (mainWord, mainStart, mainDir, mainWordScore),
            "crossWordInfo": crossWords,
            "bingo": bingo
        }

    def print_board(self):
        for r in range(self.size):
            row = []
            for c in range(self.size):
                ch = self.state[r][c] if self.state[r][c] != "" else "."
                row.append(ch)
            print(" ".join(row))

    def _board_empty(self):
        for r in range(self.size):
            for c in range(self.size):
                if self.state[r][c] != "":
                    return False
        return True

from collections import Counter
def findBlanks(avail, used):
    """
    Has to be used AFTER canMakeWord()
    Returns a list with inex, letter that contains the letter that comes from the blank
    """
    usedLetters = [i[2] for i in used]
    rackCounter = Counter(avail)
    wildcards = []
    for index, letter in enumerate(usedLetters):
        if rackCounter[letter] > 0:
            rackCounter[letter] -= 1
        else:
            wildcards.append(used[index][:-1])

    return wildcards
def canMakeWord(avail, used):
    rack = Counter(avail)
    wordCount = Counter(used)
    wildcards = rack.get("?",0)
    needed = 0
    for letter,count in wordCount.items():
        missing = count - rack.get(letter,0)
        if missing>0:
            needed += missing
            if needed > wildcards:
                return False
    return True



# test = Board()
# rack = ["E","?","Q","I","T","Y","X"]
# placements = [(7, 7, "A"), (7, 8, "D"), (7, 9, "A"), (7, 10, "G"), (7, 11, "I"),(7,12,"O")]
# letters = [ch for r, c, ch in placements]
# print(canMakeWord(rack,letters))
# print(test.score_move(placements, validate=True, isFirstMove=True, blankLocations=[]))


# test = Board()
# rack = ["?","A","N","D","C","A","R"]
# placements = [(7, 4, "H"), (7, 5, "A"), (7, 6, "N"), (7, 7, "D"), (7, 8, "C"),(7,9,"A"),(7,10,"R")]
# letters = [ch for r, c, ch in placements]
# print(canMakeWord(rack,letters))
# newBlanks = findBlanks(rack, placements)
# test.updateBlanks(newBlanks)
# print(test.score_move(placements, validate=True, isFirstMove=True))



# placements = [(6, 4, "T"), (8, 4, "U"), (9, 4, "J"), (10, 4, "A")]
# print(test.score_move(placements, validate=True, isFirstMove=False))

#Bug is that board does'nt keep track if a blank is on there or not

# placements = [(8, 7, "H"), (8, 8, "E"), (8, 9, "W")]
# print(test.score_move(placements, validate=True, isFirstMove=False, blankLocations=[]))

# test = Board()
# rack = ["?","Q","U","I","T","Y","X"]
# placements = [(7, 7, "E"), (7, 8, "Q"), (7, 9, "U"), (7, 10, "I"), (7, 11, "T"),(7,12,"Y")]
# letters = [ch for r, c, ch in placements]
# print(canMakeWord(rack,letters))
# print(test.score_move(placements, validate=True, isFirstMove=True, blankLocations=findBlanks(rack, placements)))


