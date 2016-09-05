# Game API Project Overview for the FSND Program

#BATTLESHIPS


##Game Description:
The game is played on 2 grids, one for each player. The grids are typically square – usually 10×10 – 
and the individual squares in the grid are identified by letter and number. 
Before play begins, each player secretly arranges their ships on their primary grid. 
Each ship occupies a number of consecutive squares on the grid, arranged either horizontally or vertically. 
The number of squares for each ship is determined by the type of the ship. 
The ships cannot overlap (i.e., only one ship can occupy any given square in the grid). 
The types and numbers of ships allowed are the same for each player. 
These may vary depending on the rules.
After the ships have been positioned, the game proceeds in a series of rounds. 
In each round, each player takes a turn to announce a target square in the opponent's grid which is to be shot at. 
The API announces whether or not the square is occupied by a ship, and if it is a "hit" the API marks that in the grid owners of the ship hitted

When all of the squares of a ship have been hit, the ship is sunk, and the API announces this 
(e.g. "You sank the battleship!"). If all of a player's ships have been sunk, the game is over and their opponent wins.



#Types of Ships for each player

| Class of Ship        | Size          |
|----------------------|---------------|
| Aircraft carrier     | 5             |
| Battleship           | 4             |
| Submarine            | 3             |
| Destroyer (or Cruiser| 3             |
| Patrol boat          | 2             |
