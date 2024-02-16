import ast
import numpy as np

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

GENERATOR_VERSION = 1

rows_to_skip = [0, 1, 2] + np.arange(4, 5615, 2).tolist()
print(rows_to_skip)
puzzle_ids = []
with open("generator/puzzles.pgn", "r") as f:
    lines = f.readlines()
with open("puzzles_filtered.pgn", "w") as f:
    for i, line in enumerate(lines):
        if i not in set(rows_to_skip):
            puzzle_dict = ast.literal_eval(line)
            puzzle_dict['_id'] = f"puzzle{i}"
            puzzle_dict['gameId'] = f"game{i}"
            puzzle_dict['themes'] = []
            puzzle_dict['glicko'] = {'r': 1500,
                                     'd': 100,
                                     'v': 0.01},
            puzzle_dict['plays'] = 0
            puzzle_dict['vote'] = 0
            puzzle_dict['vd'] = 0
            puzzle_dict['vu'] = 0
            puzzle_dict['users'] = []
            puzzle_dict['line'] = ' '.join(puzzle_dict['moves'])
            puzzle_dict['generator'] = GENERATOR_VERSION
            del puzzle_dict['white']
            del puzzle_dict['black']
            del puzzle_dict['ply']
            del puzzle_dict['moves']
            del puzzle_dict['game_id']
            del puzzle_dict['generator_version']

            if set(puzzle_dict.keys()) != set(default.keys()):
                raise ValueError(f"Wrong keys in line {i}")
            puzzle_ids.append(puzzle_dict['_id'])
            f.write(str(puzzle_dict) + '\n')
print("Done")
