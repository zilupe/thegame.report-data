SELECT * FROM
(
	SELECT

		player_id,
		team_id,

-- 		opponent_id,

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

		sum(pts) + sum(reb) + sum(ast) + sum(stl) + sum(blk)
		- ((sum(fta) - sum(ftm)) + (sum(fga) - sum(fgm)) + sum(tov) + sum(pf))
		as "pir",

		1.0 * (sum(pts) + sum(reb) + sum(ast) + sum(stl) + sum(blk)
		- ((sum(fta) - sum(ftm)) + (sum(fga) - sum(fgm)) + sum(tov) + sum(pf))) / count(*)
		as "avg_pir"

	from "player_logs"

	group by
		player_id,
		team_id,
		opponent_strength

) aaa

where

aaa.opponent_strength = 'top4'
-- and aaa.num_games >= 2

order by aaa."avg_pir" desc;

;