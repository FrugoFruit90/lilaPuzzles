from ast import literal_eval
import pymongo


def _dict(o: object) -> dict:
    return o.__dict__ if hasattr(o, "__dict__") else o


def _inupsert(o: object) -> object:
    # if env.args.drop or env.args.drop_db:
    #     return pymongo.InsertOne(o)
    # else:
    #     return pymongo.UpdateOne({"_id": o["_id"]}, {"$set": o}, upsert=True)
    return pymongo.UpdateOne({"_id": o["_id"]}, {"$set": o}, upsert=True)


def bulk_write(
    coll: pymongo.collection.Collection,
    objs: list,
    append: bool = False,
) -> None:
    # append parameter is for bson/json export to forum collections
    if len(objs) < 1:
        return
    # database mode
    ledger = []
    for o in objs:
        ledger.append(_inupsert(_dict(o)))
    res = coll.bulk_write(ledger).bulk_api_result


uri = 'mongodb://rootuser:rootpass@localhost:27017/lichess'


with open('../../../lichess-puzzler/puzzles_filtered.pgn') as f:
    puzzles = [literal_eval(line) for line in f]

client = pymongo.MongoClient(uri, authSource="admin")
db = client.get_default_database()

bulk_write(db.puzzle2_puzzle, puzzles)
print(db.puzzle2_puzzle)
client.close()
