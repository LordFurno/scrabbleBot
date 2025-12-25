from scrabble import Board, LetterBag
from collections import Counter
import pygame
import sys


#Example bot function
from exampleBot import getMove

def removeTilesFromRack(rack, placements):
    for r,c,ch in placements:
        if ch.islower():
            #blank used
            try:
                rack.remove('?')
            except:
                #try to remove uppercase letter if no blank found (shouldnt happen)
                try:
                    rack.remove(ch.upper())
                except:
                    pass
        else:
            try:
                rack.remove(ch.upper())
            except:
                try:
                    rack.remove('?')
                except:
                    pass

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

#Pygame visualization setup
class ScrabbleVisualizer:
    def __init__(self, board_obj):
        pygame.init()
        self.CELL_SIZE = 40
        self.BOARD_SIZE = 15
        self.MARGIN = 50
        self.INFO_WIDTH = 350
        
        self.WIDTH = self.BOARD_SIZE * self.CELL_SIZE + 2 * self.MARGIN + self.INFO_WIDTH
        self.HEIGHT = self.BOARD_SIZE * self.CELL_SIZE + 2 * self.MARGIN + 100
        
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Scrabble Bot Battle")
        self.clock = pygame.time.Clock()
        
        self.board = board_obj
        
        #Colors
        self.BG_COLOR = (245, 245, 220)
        self.BOARD_COLOR = (34, 139, 34)
        self.CELL_COLOR = (255, 248, 220)
        self.TW_COLOR = (255, 0, 0)
        self.DW_COLOR = (255, 192, 203)
        self.TL_COLOR = (0, 0, 255)
        self.DL_COLOR = (173, 216, 230)
        self.TEXT_COLOR = (0, 0, 0)
        self.TILE_COLOR = (255, 228, 181)
        
        self.font = pygame.font.Font(None, 28)
        self.small_font = pygame.font.Font(None, 18)
        self.info_font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 32)
    
    def get_bonus_color(self, r, c):
        bonus = self.board.bonus.get((r, c))
        if bonus == "TW":
            return self.TW_COLOR
        elif bonus == "DW":
            return self.DW_COLOR
        elif bonus == "TL":
            return self.TL_COLOR
        elif bonus == "DL":
            return self.DL_COLOR
        return self.CELL_COLOR
    
    def draw_board(self, players, current_turn, last_move_info=None, message=""):
        self.screen.fill(self.BG_COLOR)
        
        #Draw title
        title = self.title_font.render("Scrabble Bot Battle", True, (139, 69, 19))
        title_rect = title.get_rect(center=(self.WIDTH // 2, 20))
        self.screen.blit(title, title_rect)
        
        #Draw board
        for r in range(self.BOARD_SIZE):
            for c in range(self.BOARD_SIZE):
                x = self.MARGIN + c * self.CELL_SIZE
                y = self.MARGIN + r * self.CELL_SIZE
                
                #Draw cell background
                color = self.get_bonus_color(r, c)
                pygame.draw.rect(self.screen, color, (x, y, self.CELL_SIZE, self.CELL_SIZE))
                pygame.draw.rect(self.screen, self.BOARD_COLOR, (x, y, self.CELL_SIZE, self.CELL_SIZE), 2)
                
                #Draw bonus text
                bonus = self.board.bonus.get((r, c))
                if bonus and not self.board.state[r][c]:
                    text = self.small_font.render(bonus, True, (100, 100, 100))
                    text_rect = text.get_rect(center=(x + self.CELL_SIZE // 2, y + self.CELL_SIZE // 2))
                    self.screen.blit(text, text_rect)
                
                #Draw center star
                if r == 7 and c == 7 and self.board.state[r][c] == "":
                    star = self.font.render("★", True, (255, 215, 0))
                    star_rect = star.get_rect(center=(x + self.CELL_SIZE // 2, y + self.CELL_SIZE // 2))
                    self.screen.blit(star, star_rect)
                
                #Draw tile
                tile = self.board.state[r][c]
                if tile:
                    #Draw tile background
                    tile_rect = pygame.Rect(x + 3, y + 3, self.CELL_SIZE - 6, self.CELL_SIZE - 6)
                    pygame.draw.rect(self.screen, self.TILE_COLOR, tile_rect)
                    pygame.draw.rect(self.screen, self.TEXT_COLOR, tile_rect, 2)
                    
                    #Draw letter
                    letter = tile.upper()
                    text = self.font.render(letter, True, self.TEXT_COLOR)
                    text_rect = text.get_rect(center=(x + self.CELL_SIZE // 2, y + self.CELL_SIZE // 2 - 3))
                    self.screen.blit(text, text_rect)
                    
                    #Draw point value (small, bottom right)
                    if letter != '?' and not tile.islower():
                        points = self.board.letterScores.get(letter, 0)
                        point_text = self.small_font.render(str(points), True, self.TEXT_COLOR)
                        point_rect = point_text.get_rect(bottomright=(x + self.CELL_SIZE - 5, y + self.CELL_SIZE - 5))
                        self.screen.blit(point_text, point_rect)
        
        #Draw player info
        info_x = self.MARGIN + self.BOARD_SIZE * self.CELL_SIZE + 20
        info_y = self.MARGIN + 20
        
        for i, player in enumerate(players):
            is_current = (i == current_turn % 2)
            color = (100, 255, 100) if is_current else (220, 220, 220)
            
            #Player box
            box_height = 120
            pygame.draw.rect(self.screen, color, (info_x - 10, info_y - 10, self.INFO_WIDTH - 20, box_height), border_radius=10)
            pygame.draw.rect(self.screen, (0, 0, 0), (info_x - 10, info_y - 10, self.INFO_WIDTH - 20, box_height), 2, border_radius=10)
            
            #Player name
            name_text = self.info_font.render(player["name"], True, self.TEXT_COLOR)
            if is_current:
                name_text = self.title_font.render(player["name"] + " ◄", True, self.TEXT_COLOR)
            self.screen.blit(name_text, (info_x, info_y))
            info_y += 35
            
            #Score
            score_text = self.info_font.render(f"Score: {player['score']}", True, self.TEXT_COLOR)
            self.screen.blit(score_text, (info_x, info_y))
            info_y += 30
            
            #Rack
            rack_text = self.small_font.render("Rack:", True, self.TEXT_COLOR)
            self.screen.blit(rack_text, (info_x, info_y))
            info_y += 20
            
            rack_str = " ".join(player["rack"])
            rack_tiles = self.info_font.render(rack_str, True, self.TEXT_COLOR)
            self.screen.blit(rack_tiles, (info_x, info_y))
            info_y += 50
        
        #Draw last move info
        if last_move_info:
            info_y += 20
            pygame.draw.rect(self.screen, (255, 255, 200), (info_x - 10, info_y - 10, self.INFO_WIDTH - 20, 80), border_radius=10)
            pygame.draw.rect(self.screen, (0, 0, 0), (info_x - 10, info_y - 10, self.INFO_WIDTH - 20, 80), 2, border_radius=10)
            
            move_text = self.info_font.render("Last Move:", True, self.TEXT_COLOR)
            self.screen.blit(move_text, (info_x, info_y))
            info_y += 30
            
            score_text = self.title_font.render(f"+{last_move_info['points']} pts", True, (0, 120, 0))
            self.screen.blit(score_text, (info_x, info_y))
            
            if last_move_info.get('bingo'):
                bingo_text = self.info_font.render("BINGO! 🎉", True, (255, 0, 0))
                self.screen.blit(bingo_text, (info_x + 150, info_y))
        
        #Draw message at bottom
        if message:
            msg_y = self.HEIGHT - 60
            msg_box = pygame.Rect(self.MARGIN, msg_y, self.WIDTH - 2 * self.MARGIN, 50)
            pygame.draw.rect(self.screen, (255, 255, 255), msg_box, border_radius=5)
            pygame.draw.rect(self.screen, (0, 0, 0), msg_box, 2, border_radius=5)
            
            msg_text = self.info_font.render(message, True, self.TEXT_COLOR)
            msg_rect = msg_text.get_rect(center=msg_box.center)
            self.screen.blit(msg_text, msg_rect)
        
        pygame.display.flip()
        self.clock.tick(60)

#Initialize game
board = Board()
bag = LetterBag()

players = [
    {"name": "Bot 1", "rack": bag.draw(7), "score": 0, "function": getMove, "illegal": False},
    {"name": "Bot 2", "rack": bag.draw(7), "score": 0, "function": getMove, "illegal": False},
]
consec_passes = 0
moves_played = 0
turn = 0
game_over = False
last_move_info = None

#Initialize visualizer
visualizer = ScrabbleVisualizer(board)

print("Initial racks:")
for p in players:
    print(p["name"], p["rack"])
print()

#Initial display
visualizer.draw_board(players, turn, message="Press SPACE to start | ESC to quit")

#Game state
waiting_for_space = True
auto_play = False
running = True

#Main game loop
while running:
    #Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                if game_over:
                    running = False
                else:
                    waiting_for_space = False
            elif event.key == pygame.K_a:
                auto_play = not auto_play
                print(f"Auto-play: {'ON' if auto_play else 'OFF'}")
    
    #Game logic
    if not game_over and (not waiting_for_space or auto_play):
        current = players[turn % 2]
        rack = current["rack"]
        name = current["name"]
        bot_function = current["function"]
        
        isFirst = (moves_played == 0)
        
        visualizer.draw_board(players, turn, last_move_info, f"{name} is thinking...")
        pygame.time.wait(300 if auto_play else 100)  
        
        #Ask bot for its move
        try:
            placements = bot_function(list(rack), [row[:] for row in board.state], dict(board.bonus))
            
            print(f"{name} returned: {placements}")
        except Exception as e:
            print(f"{name} crashed with error: {e}")
            placements = []
            game_over = True
            visualizer.draw_board(players, turn, last_move_info, f"{name} CRASHED - Game Over!")
            players [turn % 2]["illegal"] = True
            pygame.time.wait(3000)
            continue
        
        if not placements:
            consec_passes += 1
            print(f"{name} passes. (Consecutive passes: {consec_passes})")
            last_move_info = None
            visualizer.draw_board(players, turn, last_move_info, f"{name} passed")
            waiting_for_space = not auto_play
            turn += 1
            
            if consec_passes >= 2:
                print("Game ends due to consecutive passing")
                game_over = True
            continue
        
        #Validate rack usage
        letters = [ch for r, c, ch in placements]
        if not canMakeWord(rack, letters):
            print(f"{name} has made an invalid move - used letters not in rack.")
            print(f"Rack: {rack}, Tried to use: {letters}")
            visualizer.draw_board(players, turn, last_move_info, 
                                f"{name} used invalid tiles - Game Over!")
            pygame.time.wait(3000)
            game_over = True
            players [turn % 2]["illegal"] = True
            continue
        
        

        #Check if move is legal
        legal, msg, details = board.is_legal(placements, isFirst)
        
        if not legal:
            print(f"{name} has attempted an illegal move: {msg}")
            players [turn % 2]["illegal"] = True
            visualizer.draw_board(players, turn, last_move_info, f"{name} illegal move: {msg}")
            pygame.time.wait(3000)
            game_over = True
            continue
        
        #Process legal move
        print("????????")
        print(placements)
        result = board.score_move(placements, validate=False, isFirstMove=isFirst, blankLocations=findBlanks(rack, placements))
        current["score"] += result["score"]
        removeTilesFromRack(rack, placements)
        draw_n = 7 - len(rack)
        if draw_n > 0:
            rack.extend(bag.draw(draw_n))
        
        moves_played += 1
        consec_passes = 0
        
        #Prepare move info
        word = result['mainWordInfo'][0] if result['mainWordInfo'] else "???"
        print(f"{name} played: {word} at {placements[0][:2]} → +{result['score']} points (total {current['score']})")
        if result['bingo']:
            print("🎉 BINGO! +50 bonus points!")
        
        last_move_info = {"points": result["score"], "bingo": result.get("bingo", False)}
        visualizer.draw_board(players, turn, last_move_info, f"{name} played {word} for {result['score']} points!")
        
        #Check for game end conditions
        if consec_passes >= 2:
            print("Game ends due to consecutive passing")
            game_over = True
            continue
        
        for p in players:
            if len(p["rack"]) == 0 and bag.remainingTiles() == 0:
                print(f"Game ends: {p['name']} used all tiles and bag empty.")
                game_over = True
                break
        
        if game_over:
            continue
        
        turn += 1
        waiting_for_space = not auto_play
        
        if auto_play:
            pygame.time.wait(1000)  #1 second between moves in auto mode
    
    #Update display
    if game_over:
        scores = [p["score"] for p in players]
        if players [turn % 2]["illegal"] == True:
            message = f"{current["name"]} has made an illegal move. {players[(turn+1)%2]["name"]} has won."
            winner = None
        
        elif scores[0] > scores[1]:
            winner = players[0]["name"]
            margin = scores[0] - scores[1]
        elif scores[1] > scores[0]:
            winner = players[1]["name"]
            margin = scores[1] - scores[0]
        else:
            winner = "TIE"
            margin = 0
        
        if winner == "TIE":
            message = f"Game Over - It's a TIE! Press SPACE to exit"
        elif winner is not None:
            message = f"Game Over - {winner} wins by {margin} points! Press SPACE to exit"
        
        visualizer.draw_board(players, turn, last_move_info, message)
        print(f"\nFinal scores:")
        for p in players:
            print(f"{p['name']}: {p['score']}")
        print(message)
        break
    else:
        msg = "Press SPACE for next move | Press A to toggle auto-play | ESC to quit"
        visualizer.draw_board(players, turn, last_move_info, msg)
    
    visualizer.clock.tick(60)

pygame.quit()
sys.exit()
