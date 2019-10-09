SELECT
    player_id,
    team_id,
    num_games,
    printf("%.1f", avg_pir) as "avg_pir",
    printf("%.1f", avg_fga) as "avg_fga",
    printf("%.1f", 100. * "fg%") as "fg%",
    printf("%.1f", avg_3pa) as "avg_3pa",
    printf("%.1f", 100. * "3p%") as "3p%",
    printf("%.1f", avg_2pa) as "avg_2pa",
    printf("%.1f", 100. * "2p%") as "2p%",
    printf("%.1f", avg_fta) as "avg_fta",
    printf("%.1f", 100. * "ft%") as "ft%",
    printf("%.1f", avg_reb) as "avg_reb",
    printf("%.1f", avg_ast) as "avg_ast",
    printf("%.1f", avg_stl) as "avg_stl",
    printf("%.1f", avg_tov) as "avg_tov",
    printf("%.1f", avg_blk) as "avg_blk",
    printf("%.1f", avg_pf) as "avg_pf"
FROM
(
	SELECT

		player_id,
		team_id,

        case when opponent_id in ('burritos', 'lostangels', 'dropbears', 'rockets') then 'top4'
	    else 'bottom4' end as 'opponent_strength',

		count(*) as num_games,

		sum(pts) as "pts",
		avg(pts) as "avg_pts",

		sum(fgm) as "fgm",
		sum(fga) as "fga",
		1.0 * sum(fgm) / sum(fga) as "fg%",

		avg(fgm) as "avg_fgm",
		avg(fga) as "avg_fga",

		sum(tpm) as "3pm",
		sum(tpa) as "3pa",
		1.0 * sum(tpm) / sum(tpa) as "3p%",

		avg(tpm) as "avg_3pm",
		avg(tpa) as "avg_3pa",

		sum(fgm) - sum(tpm) as "2pm",
		sum(fga) - sum(tpa) as "2pa",
		1.0 * (sum(fgm) - sum(tpm)) / (sum(fga) - sum(tpa)) as "2p%",

		avg(fgm - tpm) as "avg_2pm",
		avg(fga - tpa) as "avg_2pa",

		sum(ftm) as "ftm",
		sum(fta) as "fta",
		1.0 * sum(ftm) / sum(fta) as "ft%",

		avg(ftm) as "avg_ftm",
		avg(fta) as "avg_fta",

		sum(oreb) as "oreb",
		sum(dreb) as "dreb",
		sum(reb) as "reb",

		avg(oreb) as "avg_oreb",
		avg(dreb) as "avg_dreb",
		avg(reb) as "avg_reb",

		sum(ast) as "ast",
		avg(ast) as "avg_ast",

		sum(stl) as "stl",
		avg(stl) as "avg_stl",

		sum(tov) as "tov",
		avg(tov) as "avg_tov",

		sum(blk) as "blk",
		avg(blk) as "avg_blk",

		sum(pf) as "pf",
		avg(pf) as "avg_pf",

		sum(pir) as "pir",
		avg(pir) as "avg_pir",

		sum(enthusiasm_rating) as "enthusiasm_rating",
		avg(enthusiasm_rating) as "avg_enthusiasm_rating"

	from "player_logs"

	group by
		player_id,
		team_id,
	    opponent_strength


) aaa

where

      aaa.num_games >= 2
      and opponent_strength = 'top4'

order by aaa."avg_pir" desc

;