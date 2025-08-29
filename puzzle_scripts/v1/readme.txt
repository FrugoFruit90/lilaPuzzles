# clean - be careful!!!
mongosh lichess --eval "db.puzzle2_puzzle.deleteMany({})"
mongosh lichess --eval "db.puzzle2_path.deleteMany({})"
mongosh lichess --eval "db.game5.deleteMany({})"


# load
mongoimport $MONGO_URL --authenticationDatabase admin --db lichess --collection puzzle2_puzzle --type json --file puzzles_filtered.jsonl
mongoimport $MONGO_URL --authenticationDatabase admin --db lichess --collection puzzle2_path --type json --file paths_filtered_tier_good.jsonl
mongoimport $MONGO_URL --authenticationDatabase admin --db lichess --collection puzzle2_path --type json --file paths_filtered_tier_all.jsonl
mongoimport $MONGO_URL --authenticationDatabase admin --db lichess --collection game5 --type json --file games_filtered.jsonl


mongoimport --db lichess --collection puzzle2_puzzle --type json --file puzzles_filtered.jsonl
mongoimport --db lichess --collection puzzle2_path --type json --file paths_filtered_tier_good.jsonl
mongoimport --db lichess --collection puzzle2_path --type json --file paths_filtered_tier_all.jsonl
mongoimport --db lichess --collection game5 --type json --file games_filtered.jsonl

