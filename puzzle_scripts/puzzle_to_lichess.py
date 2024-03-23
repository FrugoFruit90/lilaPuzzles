import pathlib

import jnius_config

path = str(
    (
        pathlib.Path.home()
        / ".cache/coursier/v1/https/raw.githubusercontent.com/lichess-org/lila-maven/master/org/lichess/compression_3/1.10/*"
    ).absolute()
)
jnius_config.set_classpath(".", path)

import ast
import base64
import datetime
import json

import chess.pgn
import more_itertools
import numpy as np
from jnius import autoclass

GENERATOR_VERSION = 1

encoder = autoclass("org.lichess.compression.game.Encoder")

default = {
    "_id": "01tg7",
    "gameId": "TaHSAsYD",
    "fen": "8/1bnr2pk/4pq1p/p1p1Rp2/P1B2P2/1PP3Q1/3r1BPP/4R1K1 w - - 1 44",
    "themes": ["middlegame", "short", "fork", "advantage"],
    "glicko": {
        "r": 1541.7361815070494,
        "d": 75.48127091813447,
        "v": 0.08991697492001756,
    },
    "plays": 209,
    "vote": 0.9266055226325989,
    "line": "f2c5 d2g2 g3g2 b7g2",
    "generator": 14.0,
    "cp": 468.0,
    "vd": 8,
    "vu": 210,
    "users": ["reda", "cted"],
}


class BinData:

    def __init__(self, data: bytes) -> None:
        self.data = data

    def toJson(self):
        return {
            "$binary": {
                "base64": f'{base64.b64encode(self.data).decode("utf8")}',
                "subType": "00",
            }
        }


class ISODate:

    def __init__(self, date: datetime.datetime) -> None:
        self.date = date

    def toJson(self):
        return {"$date": f"{self.date.isoformat()}"}


def get_san_moves(game):
    board = game.board()
    result = []
    for move in game.mainline_moves():
        san = board.san(move)
        result.append(san)
        board.push_san(san)
    return result


rows_to_skip = [0, 1, 2] + np.arange(4, 5615, 2).tolist()
print(rows_to_skip)

with open("puzzles.pgn", "r") as f:
    lines = f.readlines()


games_file = open("300k.pgn", encoding="utf-8-sig")
game = chess.pgn.read_game(games_file)  # first read


incorrect_games = []

puzzle_ids = []

with open("puzzles_filtered.jsonl", "w") as puzzles_filtered, open(
    "games_filtered.jsonl", "w"
) as games_filtered:
    for i, line in enumerate(lines):
        if i not in set(rows_to_skip):
            generator_dict = ast.literal_eval(line)
            puzzle_dict = {
                "_id": f"p{str(i).zfill(4)}",  # total len is 5
                "cp": generator_dict["cp"],
                "fen": generator_dict["fen"],
                "gameId": f"game{str(i).zfill(4)}",  # total len is 8
                "themes": [],
                "glicko": {"r": 1500, "d": 100, "v": 0.01},
                "plays": 0,
                "vote": 0,
                "vd": 0,
                "vu": 0,
                "users": [],
                "line": " ".join(generator_dict["moves"]),
                "generator": GENERATOR_VERSION,
            }

            while (
                game.headers["White"] != generator_dict["white"]
                or game.headers["Black"] != generator_dict["black"]
            ):
                game = chess.pgn.read_game(games_file)

            san_moves = get_san_moves(game)
            encoded = encoder.encode(san_moves)
            if encoded is None:
                incorrect_games.append(str(game))
                continue
            hp = BinData(encoded.tostring()).toJson()

            game_dict = {
                "_id": puzzle_dict["gameId"],
                "an": "false",  # annotated
                "c": BinData(
                    b"\x0f\x0f\x00\xdaY\x01<\xf8"
                ).toJson(),  # "clock"? what does that even mean?
                "ca": ISODate(
                    datetime.datetime(
                        2024, 2, 10, 9, 55, 17, 568000, tzinfo=datetime.timezone.utc
                    )
                ).toJson(),  # createdAt
                "cb": BinData(b"").toJson(),  # blackClockHistory
                "cw": BinData(b"").toJson(),  # whiteClockHistory
                "hp": hp,  # huffmanPgn
                "is": "A9fgA9gA",  # playerIds... but wtf?
                "p0": {"e": game.headers["WhiteElo"], "d": 5},
                "p1": {"e": game.headers["BlackElo"], "d": 5},
                "ra": "false",  # rated
                "s": 31,  # status
                "so": 12,  # source
                "t": len(list(game.mainline_moves())),  # turns... like plies?
                "ua": ISODate(
                    datetime.datetime(2024, 2, 10, 10, 52, tzinfo=datetime.timezone.utc)
                ).toJson(),
                "us": [
                    game.headers["White"].replace(" ", ""),
                    game.headers["Black"].replace(" ", ""),
                ],  # playerUids
                "v": 1,  # variant
                "w": "true",  # winnerColor, seems like it's True for White winning, but what about the draw?
                "wid": "",  # winnerID
            }

            if set(puzzle_dict.keys()) != set(default.keys()):
                raise ValueError(f"Wrong keys in line {i}")
            puzzles_filtered.write(json.dumps(puzzle_dict) + "\n")
            puzzle_ids.append(puzzle_dict["_id"])
            games_filtered.write(json.dumps(game_dict) + "\n")


def create_puzzle_path(theme: str, tier: str, number: int, chunk: list[str]):
    result = {
        "_id": f"{theme}|{tier}|0000-9999|1620110906065|{number}",
        "min": f"{theme}|{tier}|0000",
        "max": f"{theme}|{tier}|9999",
        "ids": chunk,
        "tier": tier,
        "theme": theme,
        "gen": 1620110906065,
    }
    return result


theme = "mix"
tier_good = "good"
tier_all = "all"
with open("paths_filtered_tier_good.jsonl", "w") as paths_filtered_tier_good, open(
    "paths_filtered_tier_all.jsonl", "w"
) as paths_filtered_tier_all:
    for i, chunk in enumerate(more_itertools.chunked(puzzle_ids, 10)):
        paths_filtered_tier_good.write(
            json.dumps(
                create_puzzle_path(theme=theme, tier=tier_good, number=i, chunk=chunk)
            )
            + "\n"
        )
        paths_filtered_tier_all.write(
            json.dumps(
                create_puzzle_path(theme=theme, tier=tier_all, number=i, chunk=chunk)
            )
            + "\n"
        )

# print(len(incorrect_games))

print("Done")
