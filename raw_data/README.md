
### Expected Inputs

For the first stats season:

    game_id
    side_id
    player_id
    fgm
    fga
    3pm
    3pa
    ftm
    fta
    pts
    oreb
    dreb
    reb *
    ast
    stl
    tov
    blk
    pf

----

### Easystats

To make a workable CSV from their HTML "export":

* Create an empty CSV file
* Open the empty file in Excel
* Select all cells, format cells as "Text"
* Copy paste the table from the HTML page, select "Match Destination Formatting" option in Paste menu.
* Clean up player names
* Open in text editor, replace tabs with commas

Some games have one team, some games have team totals, some don't.

### Statastic

Manual steps involved in preparation:

* Lowercase all
* Remove the invalid character from `TIM` column name
* Replace all player names with their SK PLAYER ID. For example, `Carlos` should be `lostangels-carlos`.
* Rename each file to match the SK GAME ID.
* Replaced semicolons with commas

### SK v3

### SK v4
