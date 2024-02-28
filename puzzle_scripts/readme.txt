mongoimport --db lichess --collection puzzle2_puzzle --type json --file puzzles_filtered.jsonl
mongoimport --db lichess --collection puzzle2_path --type json --file paths_filtered.jsonl
mongoimport --db lichess --collection game5 --type json --file games_filtered.jsonl
