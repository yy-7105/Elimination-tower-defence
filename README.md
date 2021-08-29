# Elimination-tower-defence
Rules:
- There are three types of tower, Cannon, Sniper, and Crusher: 
Canon deal average damage and has a high attack speed and an average attack range; 
Sniper deals high damage and deal increasing damage to Square; its attack range is larger but its reloading speed is low; 
Crusher deals low to average damage and has a small attack range, but it smashes all enemies in his attack range!
- There are two types of enemies, Circle and Square:
Circle moves in a higher speed and has less health while Square is tankier but moves slower, moreover Square takes increased damage from Sniper tower
- Player can select and deselect a gird. When a grid is selected, if a tower is placed on the grid, the player sees the attack range of the tower; and if not, player could choose a tower from the buttom right corner of the screen.
- When three towers are placed in a sequence of 3 (either in row or in column), 3 towers merge into one higher level tower at the position player places the tower.
- Eliminate an enemy earns player 10 points times the score multiplier.
- Player has 10 seconds to place tower after a wave of enemy is cleared
- Survive as long as possible!

Defects:
- Calculating the enemies' path using DFS method, not often the best route
- Haven't add images yet
- Need more tower types and enemy types
- Need more tests on current tower and enemy attributes
