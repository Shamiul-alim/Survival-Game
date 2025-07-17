<h1> Survival Game with Adaptive AI Enemies</h1>

A 2D top-down survival game where enemies **learn from your playstyle** using Q-learning. Experience dynamic combat that evolves as you play.


##  Features

- **Adaptive Enemy AI** — Enemies use Q-learning to counter your attacks
- **Dynamic Combat** — Dodge, block, and counter mechanics in real time
- **Multiple Enemy Types** — Each with unique learning patterns
- **Weapon & Magic System** — Melee and spellcasting with switching
- **Dodge Analytics** — Real-time dodge distance tracking and logs
- **Player Progression** — Upgrade your stats as the AI improves


##  AI Learning Overview

- Shared Q-table across enemy instances (hive learning)
- Recognizes and adapts to player attack styles
- Gradually shifts from exploration to exploitation
- Console logs include:
  - Dodge distances
  - Q-values
  - Recognized patterns


##  Getting Started

- git clone the repository
- cd Survival-Game
- pip install -r requirements.txt (for python 3.13 => pip install --pre -r requirements.txt )
- open the folder in your environment(for loading the graphics file)
- python main.py


##  Controls:

| Action              | Key        |
| ------------------- | ---------- |
| Move                | Arrow Keys |
| Attack              | Space      |
| Cast Magic          | Left Ctrl  |
| Switch Weapon/Magic | Q / E      |
| Toggle Menu         | M          |
| Save AI Learning    | S          |
