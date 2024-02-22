import ast
import datetime
import pathlib
import re

import chess.pgn
import numpy as np
from jnius import autoclass
import jnius_config

default2 = {'black': 'Lebel Arias, Julia',
            'cp': 688,
            'fen': '2R5/3rq1k1/p6p/1p3pNQ/Pb2p3/4P2P/5PP1/6K1 w - - 1 30',
            'game_id': '',
            'generator_version': '48WC9',
            'moves': ['c8e8', 'e7g5', 'e8g8', 'g7g8'], 'ply': 58,
            'white': 'Hindle, Kathleen'}

default = {'_id': '01tg7',
           'gameId': 'TaHSAsYD',
           'fen': '8/1bnr2pk/4pq1p/p1p1Rp2/P1B2P2/1PP3Q1/3r1BPP/4R1K1 w - - 1 44',
           'themes': ['middlegame', 'short', 'fork', 'advantage'],
           'glicko': {'r': 1541.7361815070494,
                      'd': 75.48127091813447,
                      'v': 0.08991697492001756},
           'plays': 209,
           'vote': 0.9266055226325989,
           'line': 'f2c5 d2g2 g3g2 b7g2',
           'generator': 14.0,
           'cp': 468.0,
           'vd': 8,
           'vu': 210,
           'users': ['reda', 'cted']}


def remove_move_numbers(pgn_string):
    # Regular expression to match move numbers followed by optional spaces and a period
    pattern = re.compile(r'\b\d+\s*\.\s*')

    # Replace all occurrences of the pattern with an empty string
    pgn_without_move_numbers = re.sub(pattern, '', pgn_string)

    # Normalize whitespace to single space
    pgn_without_move_numbers = re.sub(r'\s+', ' ', pgn_without_move_numbers)

    return pgn_without_move_numbers.strip()

GENERATOR_VERSION = 1

rows_to_skip = [0, 1, 2] + np.arange(4, 5615, 2).tolist()
print(rows_to_skip)

with open("puzzles.pgn", "r") as f:
    lines = f.readlines()

games_file = open("300k.pgn", encoding="utf-8-sig")
game = chess.pgn.read_game(games_file)  # first read

games_filtered = open("games_filtered.pgn", "w")

# path = str((pathlib.Path.home() / ".cache/coursier/v1/https/raw.githubusercontent.com/lichess-org/lila-maven/master/org/lichess/compression_3/1.10/*").absolute())
# jnius_config.set_classpath(".", path)
# encoder = autoclass("org.lichess.compression.game.Encoder")

with open("puzzles_filtered.pgn", "w") as f:
    for i, line in enumerate(lines):
        if i not in set(rows_to_skip):
            generator_dict = ast.literal_eval(line)
            puzzle_dict = {
                '_id': f"p{str(i).zfill(4)}",  # total len is 5
                'cp': generator_dict['cp'],
                'fen': generator_dict['fen'],
                'gameId': f"game{str(i).zfill(4)}",  # total len is 8
                'themes': [],
                'glicko': {'r': 1500,
                           'd': 100,
                           'v': 0.01},
                'plays': 0,
                'vote': 0,
                'vd': 0,
                'vu': 0,
                'users': [],
                'line': ' '.join(generator_dict['moves']),
                'generator': GENERATOR_VERSION
            }

            while game.headers["White"] != generator_dict['white'] or game.headers["Black"] != generator_dict['black']:
                game = chess.pgn.read_game(games_file)
            game_dict = {
                '_id': puzzle_dict['gameId'],
                'an': False,  # annotated
                'c': b'\x0f\x0f\x00\xdaY\x01<\xf8',  # "clock"? what does that even mean?
                'ca': datetime.datetime(2024, 2, 10, 9, 55, 17, 568000),  # createdAt
                'cb': '',  # blackClockHistory
                'cw': '',  # whiteClockHistory
                'hp': remove_move_numbers(str(game.mainline_moves())),  # huffmanPgn
                'is': 'A9fgA9gA',  # playerIds... but wtf?
                'p0': {'e': game.headers["WhiteElo"], 'd': 5},
                'p1': {'e': game.headers["BlackElo"], 'd': 5},
                'ra': False,  # rated
                's': 31,  # status
                'so': 12,  # source
                't': 109,  # turns... like plies?
                'ua': datetime.datetime(2024, 2, 10, 10, 52),
                'us': [game.headers["White"].replace(" ", ""), game.headers["Black"].replace(" ", "")],  # playerUids
                'v': 1,  # variant
                'w': True,  # winnerColor, seems like it's True for White winning, but what about the draw?
                'wid': ''  # winnerID
            }

            if set(puzzle_dict.keys()) != set(default.keys()):
                raise ValueError(f"Wrong keys in line {i}")
            f.write(str(puzzle_dict) + '\n')
            games_filtered.write(str(game_dict) + '\n')

games_file.close()
print("Done")
