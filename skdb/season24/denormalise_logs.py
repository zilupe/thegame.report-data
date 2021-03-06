import csv

import pandas as pd


def denormalise_player_logs(path):

    outcomes = {}
    tl = pd.read_csv("teamlogs-normalised.csv")
    for game_id, group in tl.groupby(["game_id"]):
        sides = [group[group["side_id"] == 0], group[group["side_id"] == 1]]
        outcomes[game_id] = (
            "w" if sides[0]["pts"].sum() > sides[1]["pts"].sum() else "d",
            "w" if sides[1]["pts"].sum() > sides[0]["pts"].sum() else "d",
        )

    ignored_names = ["enthusiasm_rating"]

    with open(path) as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            for k in ignored_names:
                row.pop(k, None)
            row["twoptm"] = int(row["fgm"]) - int(row["threeptm"])
            row["twopta"] = int(row["fga"]) - int(row["threepta"])

            game_id = row["game_id"]
            if game_id in outcomes:
                row["outcome"] = outcomes[game_id][int(row["side_id"])]
            else:
                # A game in which only one side was tracked
                if game_id == "20190815-1930-lions-burritos" and row["side_id"] == "1":
                    row["outcome"] = "w"
            yield row


def denormalise_team_logs(path):

    # Count players in game based on playerlogs
    pl = pd.read_csv("playerlogs.csv")
    num_players = {}
    for game_id, group in pl.groupby(["game_id"]):
        num_players[game_id] = (
            len(group[group["side_id"] == 0].index),
            len(group[group["side_id"] == 1].index),
        )

    tl = pd.read_csv(path)
    column_names = [c for c in tl.columns]
    fact_names = ['season_id', 'game_id', 'side_id', 'team_id', 'opp_team_id']
    ignored_names = ['opponent_pts', 'x_factor', 'possessions', 'defensive_eff', 'offensive_eff']
    measure_names = [c for c in column_names if c not in fact_names and c not in ignored_names]

    for game_id, group in tl.groupby(["game_id"]):
        sides = [group[group["side_id"] == 0], group[group["side_id"] == 1]]

        side_rows = []
        for side_id in range(2):
            side = sides[side_id]
            row = {
                "season_id": side["season_id"].iloc[0],
                "game_id": game_id,
                "side_id": side_id,
                "team_id": side["team_id"].iloc[0],
                "opp_team_id": side["opp_team_id"].iloc[0],
                **{m: side[m].iloc[0] for m in measure_names},
            }
            side_rows.append(row)

        for side_id in range(2):
            opp_side_id = abs(side_id - 1)

            side_rows[side_id]["twoptm"] = side_rows[side_id]["fgm"] - side_rows[side_id]["threeptm"]
            side_rows[side_id]["twopta"] = side_rows[side_id]["fga"] - side_rows[side_id]["threepta"]
            side_rows[side_id]["opp_twoptm"] = side_rows[opp_side_id]["fgm"] - side_rows[opp_side_id]["threeptm"]
            side_rows[side_id]["opp_twopta"] = side_rows[opp_side_id]["fga"] - side_rows[opp_side_id]["threepta"]

            side_rows[side_id]["fd"] = side_rows[opp_side_id]["fc"]
            side_rows[side_id]["blka"] = side_rows[opp_side_id]["blk"]

            side_rows[side_id]["opp_fd"] = side_rows[side_id]["fc"]
            side_rows[side_id]["opp_fc"] = side_rows[opp_side_id]["fc"]
            side_rows[side_id]["opp_blk"] = side_rows[opp_side_id]["blk"]
            side_rows[side_id]["opp_blka"] = side_rows[side_id]["blk"]

            side_rows[side_id]["outcome"] = "w" if side_rows[side_id]["pts"] > side_rows[opp_side_id]["pts"] else "d"

            for m in measure_names:
                side_rows[side_id][f"opp_{m}"] = side_rows[opp_side_id][m]

        for side_id in range(2):
            s = side_rows[side_id]
            s["pir"] = (
                (s["pts"] + s["reb"] + s["ast"] + s["stl"] + s["blk"])
                - (s["fta"] - s["ftm"])
                - (s["fga"] - s["fgm"])
                - s["tov"]
                - s["fc"]
            )

        for side_id in range(2):
            opp_side_id = abs(side_id - 1)
            side_rows[side_id]["opp_pir"] = side_rows[opp_side_id]["pir"]

            if game_id in num_players:
                side_rows[side_id]["num_players"] = int(num_players[game_id][side_id])
                side_rows[side_id]["opp_num_players"] = int(num_players[game_id][opp_side_id])

        for row in side_rows:
            yield row


if __name__ == "__main__":
    denorm = pd.DataFrame(denormalise_team_logs("teamlogs-normalised.csv"))
    denorm["num_players"] = denorm["num_players"].fillna("")
    denorm["opp_num_players"] = denorm["opp_num_players"].fillna("")
    with open("teamlogs.csv", "w") as f:
        csv_writer = csv.DictWriter(f, fieldnames=denorm.columns)
        csv_writer.writeheader()
        for row in denorm.T.to_dict().values():
            row["num_players"] = int(row["num_players"]) if row["num_players"] else None
            row["opp_num_players"] = int(row["opp_num_players"]) if row["opp_num_players"] else None
            csv_writer.writerow(row)

    denorm = pd.DataFrame(denormalise_player_logs("playerlogs-normalised.csv"))
    with open("playerlogs.csv", "w") as f:
        csv_writer = csv.DictWriter(f, fieldnames=denorm.columns)
        csv_writer.writeheader()
        for row in denorm.T.to_dict().values():
            csv_writer.writerow(row)
