#Survival Game with Adaptive AI Enemies
A 2D top-down survival game featuring enemies that learn from player behavior using reinforcement learning techniques.

Key Features
Intelligent Enemy AI using Q-learning algorithms

Dynamic Combat System where enemies adapt to player tactics

Dodge Mechanics with distance tracking and printing

Multiple Enemy Types with unique behaviors and learning patterns

Weapon & Magic Systems with different attack types

Player Progression with stats upgrades

Technical Highlights
Implemented Q-learning for enemy decision making:

Enemies track player attack patterns

Choose optimal defensive actions (dodge/block/counter)

Shared learning between enemy instances

Real-time combat analytics:

Dodge distance measurements

Q-table value tracking

Attack pattern recognition

How Enemies Learn
Enemies utilize a shared Q-table to:

Remember successful defensive actions against different attack types

Gradually reduce exploration as they learn

Adapt movement patterns based on player preferences

Print learning metrics to console for debugging

Try It Out
Clone the repository

Install requirements: pip install -r requirements.txt

Run: python main.py

Controls:

Arrow keys: Movement

Space: Attack

L-Ctrl: Magic

Q/E: Switch weapons/magic

M: Toggle menu

S: Save learning data
