# Elimination-tower-defence
Rules:
- There are three types of tower, Cannon, Sniper, and Crusher: 
Canon deal average damage and has a high attack speed and an average attack range; 
Sniper deals high damage and deal increasing damage to Square; its attack range is larger but its reloading speed is low; 
Crusher deals low to average damage in a small attack range (deael 50% more damage to triangle), but it smashes all enemies in his attack range!
- There are two types of enemies, Circle, Square and Triangle:
Circle moves at a medium speed and has medium hp.
Square moves slow but has high hp. Meanwhile it takes increased damage from Sniper tower.
Triangle moves fast but has low hp, and takes increased damage from Crusher.
- Player can select and deselect a gird. When a grid is selected, if a tower is placed on the grid, the player sees the information of the tower (attack range, level, attack damage, attack interval); and if not, player could choose and place a tower from the buttom right corner of the screen.
- When three towers are placed in a sequence of 3 (either in row or in column), 3 towers merge into one higher level tower at the position player places the tower.
- Eliminate an enemy earns player 10 points times the score multiplier.
- Player has 15 seconds to place tower after a wave of enemy is cleared. One can also click the "GO!" button to skip the waiting time.
- Survive as long as possible!

Features:
- BFS and DFS algorithm for enemies' path
- Combine tower defence game with elimination game
- Open for adding new types of enemies and towers

August 29, 2021 update:
- Calculating enemy path using BFS algorithm
- Lower FPS
- Add new enemy: Triangle
- Limit max number of towers that can be built each wave (can be added up)
- Show enemies info in the next wave on the right
- Show selected tower's attributes
- Add option to skip to next wave after current waves cleared
- Adjusted towers and enemies' attributes
- Bugs fixed
