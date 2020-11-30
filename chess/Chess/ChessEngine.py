class GameState:
    def __init__(self):
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],
        ]
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = ()
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = '--'
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--'

        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()

        if move.isCastleMove:
            if move.endCol - move.startCol == 2:
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = '--'
            else:
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = '--'

        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                                 self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove

            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--'
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()

            # undo castling
            self.castleRightsLog.pop()
            newRights = self.castleRightsLog[-1]
            self.currentCastlingRight = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs)

            if move.isCastleMove:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = '--'
                else:
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = '--'

    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.bks = False

    def getValidMoves(self):
        tempEmpassantPossible = self.enpassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                        self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)
        moves = self.getAllPosibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
                print("CHECKMATE")
            else:
                self.staleMate = True
                print("STALEMATE")
        else:
            self.checkMate = False
            self.staleMate = False

        self.enpassantPossible = tempEmpassantPossible
        self.currentCastlingRight = tempCastleRights
        return moves

    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPosibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    def getAllPosibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    if piece == 'p':
                        self.getPawnMoves(r, c, moves)
                    elif piece == 'R':
                        self.getRookMoves(r, c, moves)
                    elif piece == 'B':
                        self.getBishopMoves(r, c, moves)
                    elif piece == 'N':
                        self.getKnightMoves(r, c, moves)
                    elif piece == 'Q':
                        self.getBishopMoves(r, c, moves)
                        self.getRookMoves(r, c, moves)
                    elif piece == 'K':
                        self.getKingMoves(r, c, moves)
        return moves

    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:
            if self.board[r - 1][c] == '--':
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == '--':
                    moves.append(Move((r, c), (r - 2, c), self.board))

            # capture
            if c - 1 >= 0:
                if self.board[r - 1][c - 1][0] == 'b':
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnpassantMove=True))
            if c + 1 <= 7:
                if self.board[r - 1][c + 1][0] == 'b':
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnpassantMove=True))

        else:
            if r + 1 < 8:
                if self.board[r + 1][c] == '--':
                    moves.append(Move((r, c), (r + 1, c), self.board))
                    if r == 1 and self.board[r + 2][c] == '--':
                        moves.append(Move((r, c), (r + 2, c), self.board))

                    # capture
                if c - 1 >= 0:
                    if self.board[r + 1][c - 1][0] == 'w':
                        moves.append(Move((r, c), (r + 1, c - 1), self.board))
                    elif (r + 1, c - 1) == self.enpassantPossible:
                        moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnpassantMove=True))
                if c + 1 <= 7:
                    if self.board[r + 1][c + 1][0] == 'w':
                        moves.append(Move((r, c), (r + 1, c + 1), self.board))
                    elif (r + 1, c + 1) == self.enpassantPossible:
                        moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnpassantMove=True))

    def getRookMoves(self, r, c, moves):
        # sus
        for i in reversed(range(r)):
            if self.board[i][c] == '--':
                moves.append(Move((r, c), (i, c), self.board))

            if (self.whiteToMove and self.board[i][c][0] == 'b') or (
                    not self.whiteToMove and self.board[i][c][0] == 'w'):
                moves.append(Move((r, c), (i, c), self.board))
                break

            if (self.whiteToMove and self.board[i][c][0] == 'w') or (
                    not self.whiteToMove and self.board[i][c][0] == 'b'):
                break
        # jos
        for i in (range(r + 1, 8)):
            if self.board[i][c] == '--':
                moves.append(Move((r, c), (i, c), self.board))

            if (self.whiteToMove and self.board[i][c][0] == 'b') or (
                    not self.whiteToMove and self.board[i][c][0] == 'w'):
                moves.append(Move((r, c), (i, c), self.board))
                break

            if (self.whiteToMove and self.board[i][c][0] == 'w') or (
                    not self.whiteToMove and self.board[i][c][0] == 'b'):
                break
        # stanga
        for i in reversed(range(c)):
            if self.board[r][i] == '--':
                moves.append(Move((r, c), (r, i), self.board))

            if (self.whiteToMove and self.board[r][i][0] == 'b') or (
                    not self.whiteToMove and self.board[r][i][0] == 'w'):
                moves.append(Move((r, c), (r, i), self.board))
                break

            if (self.whiteToMove and self.board[r][i][0] == 'w') or (
                    not self.whiteToMove and self.board[r][i][0] == 'b'):
                break
        # drepata
        for i in (range(c + 1, 8)):
            if self.board[r][i] == '--':
                moves.append(Move((r, c), (r, i), self.board))

            if (self.whiteToMove and self.board[r][i][0] == 'b') or (
                    not self.whiteToMove and self.board[r][i][0] == 'w'):
                moves.append(Move((r, c), (r, i), self.board))
                break

            if (self.whiteToMove and self.board[r][i][0] == 'w') or (
                    not self.whiteToMove and self.board[r][i][0] == 'b'):
                break

    def getBishopMoves(self, r, c, moves):

        # dreapta sus
        i = r - 1
        j = c + 1
        while i >= 0 and j <= 7:
            if self.board[i][j] == '--':
                moves.append(Move((r, c), (i, j), self.board))

            if (self.whiteToMove and self.board[i][j][0] == 'b') or (
                    not self.whiteToMove and self.board[i][j][0] == 'w'):
                moves.append(Move((r, c), (i, j), self.board))
                break

            if (self.whiteToMove and self.board[i][j][0] == 'w') or (
                    not self.whiteToMove and self.board[i][j][0] == 'b'):
                break
            i = i - 1
            j = j + 1

        # stanga jos
        i = r + 1
        j = c - 1
        while i <= 7 and j >= 0:
            if self.board[i][j] == '--':
                moves.append(Move((r, c), (i, j), self.board))

            if (self.whiteToMove and self.board[i][j][0] == 'b') or (
                    not self.whiteToMove and self.board[i][j][0] == 'w'):
                moves.append(Move((r, c), (i, j), self.board))
                break

            if (self.whiteToMove and self.board[i][j][0] == 'w') or (
                    not self.whiteToMove and self.board[i][j][0] == 'b'):
                break
            i = i + 1
            j = j - 1

        # stanga sus
        i = r - 1
        j = c - 1
        while i >= 0 and j >= 0:
            if self.board[i][j] == '--':
                moves.append(Move((r, c), (i, j), self.board))

            if (self.whiteToMove and self.board[i][j][0] == 'b') or (
                    not self.whiteToMove and self.board[i][j][0] == 'w'):
                moves.append(Move((r, c), (i, j), self.board))
                break

            if (self.whiteToMove and self.board[i][j][0] == 'w') or (
                    not self.whiteToMove and self.board[i][j][0] == 'b'):
                break
            i = i - 1
            j = j - 1

        # stanga sus
        i = r + 1
        j = c + 1
        while i <= 7 and j <= 7:
            if self.board[i][j] == '--':
                moves.append(Move((r, c), (i, j), self.board))

            if (self.whiteToMove and self.board[i][j][0] == 'b') or (
                    not self.whiteToMove and self.board[i][j][0] == 'w'):
                moves.append(Move((r, c), (i, j), self.board))
                break

            if (self.whiteToMove and self.board[i][j][0] == 'w') or (
                    not self.whiteToMove and self.board[i][j][0] == 'b'):
                break
            i = i + 1
            j = j + 1

    def getKnightMoves(self, r, c, moves):
        pos = [(r + 2, c + 1), (r + 2, c - 1), (r - 2, c + 1), (r - 2, c - 1), (r + 1, c + 2), (r - 1, c + 2),
               (r + 1, c - 2), (r - 1, c - 2)]

        for i, j in pos:
            if 0 <= i <= 7 and 0 <= j <= 7:
                if self.board[i][j] == '--':
                    moves.append(Move((r, c), (i, j), self.board))

                if (self.whiteToMove and self.board[i][j][0] == 'b') or (
                        not self.whiteToMove and self.board[i][j][0] == 'w'):
                    moves.append(Move((r, c), (i, j), self.board))

    def getKingMoves(self, r, c, moves):
        pos = [(r + 1, c - 1), (r + 1, c), (r + 1, c + 1), (r - 1, c - 1), (r - 1, c), (r - 1, c + 1), (r, c - 1),
               (r, c + 1)]
        for i, j in pos:
            if 0 <= i <= 7 and 0 <= j <= 7:
                if self.board[i][j] == '--':
                    moves.append(Move((r, c), (i, j), self.board))

                if (self.whiteToMove and self.board[i][j][0] == 'b') or (
                        not self.whiteToMove and self.board[i][j][0] == 'w'):
                    moves.append(Move((r, c), (i, j), self.board))

    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return
        if (self.whiteToMove and self.currentCastlingRight.wks) or (
                not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (
                not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
            if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:
    ranksToRows = {'1': 7, '2': 6, '3': 5, '4': 4, '5': 3, '6': 2, '7': 1, '8': 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (
                    self.pieceMoved == 'bp' and self.endRow == 7)
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        self.isCastleMove = isCastleMove

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
