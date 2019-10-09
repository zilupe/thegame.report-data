SELECT

team_id,
opponent_id,
x_factor,
num_games,
avg_possessions,
avg_defensive_eff,
avg_offensive_eff,
avg_pts,
avg_opponent_pts,
"fg%",
"3p%",
"ft%",
"2p%",
"avg_oreb",
"avg_dreb",
"avg_reb",
"avg_ast",
"avg_stl",
"avg_tov",
"avg_blk",
"avg_pf"

FROM
(
	SELECT

		team_id,

		opponent_id,

-- 	    case when opponent_id in ('burritos', 'lostangels', 'dropbears', 'rockets') then 'top4'
-- 	    else 'bottom4' end as 'opponent_strength',

	    x_factor,

		count(*) as num_games,

	    avg(possessions) as "avg_possessions",
	    avg(defensive_eff) as "avg_defensive_eff",
	    avg(offensive_eff) as "avg_offensive_eff",

		sum(pts) as "pts",
		sum(opponent_pts) as "opponent_pts",

		avg(pts) as "avg_pts",
		avg(opponent_pts) as "avg_opponent_pts",

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
		avg(pf) as "avg_pf"

	from "team_logs"

	group by
		team_id,
		opponent_id,
-- 		opponent_strength,
	    x_factor

) aaa

-- order by aaa."avg_ast" desc;

where team_id = 'burritos'

;
