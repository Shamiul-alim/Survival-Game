import pygame
import random
from pathlib import Path
from settings import *
from entity import Entity
from support import *
import json

# Shared learning data structure (global to all enemies)
ENEMY_LEARNING = {
    # Format: {enemy_type: {'q_table': {...}, 'attack_history': [], 'exploration_rate': 0.3}}
}
LEARNING_FILE = Path('enemy_learning.json')

def init_learning():
    global ENEMY_LEARNING
    try:
        if LEARNING_FILE.exists():
            with open(LEARNING_FILE, 'r') as f:
                ENEMY_LEARNING = json.load(f)
                print("Loaded enemy learning data")
    except Exception as e:
        print(f"Error loading learning data: {e}")
        ENEMY_LEARNING = {}

def save_learning_data():
    try:
        with open(LEARNING_FILE, 'w') as f:
            json.dump(ENEMY_LEARNING, f, indent=2)
            print(f"Saved learning data to {LEARNING_FILE.absolute()}")
    except Exception as e:
        print(f"Error saving learning data: {e}")

class Enemy(Entity):
	def __init__(self,monster_name,pos,groups,obstacle_sprites,damage_player,trigger_death_particles,add_exp):

		# general setup
		super().__init__(groups)
		self.sprite_type = 'enemy'

		# graphics setup
		self.import_graphics(monster_name)
		self.status = 'idle'
		self.image = self.animations[self.status][self.frame_index]

		# movement
		self.rect = self.image.get_rect(topleft = pos)
		self.hitbox = self.rect.inflate(0,-10)
		self.obstacle_sprites = obstacle_sprites

		# stats
		self.monster_name = monster_name
		monster_info = monster_data[self.monster_name]
		self.health = monster_info['health']
		self.exp = monster_info['exp']
		self.speed = monster_info['speed']
		self.attack_damage = monster_info['damage']
		self.resistance = monster_info['resistance']
		self.attack_radius = monster_info['attack_radius']
		self.notice_radius = monster_info['notice_radius']
		self.attack_type = monster_info['attack_type']

		if monster_name not in ENEMY_LEARNING:
			ENEMY_LEARNING[monster_name] = {
                'q_table': {
                    'weapon': {'dodge': 0, 'block': 0, 'counter': 0},
                    'magic': {'dodge': 0, 'block': 0, 'counter': 0}
                },
                'attack_history': [],
                'exploration_rate': 0.3  # Start with 30% exploration
            }
        
		self.shared_data = ENEMY_LEARNING[monster_name]
		self.q_table = self.shared_data['q_table']
		self.attack_history = self.shared_data['attack_history']
		self.exploration_rate = self.shared_data['exploration_rate']

		# Learning parameters
		self.learning_rate = 0.1
		self.discount_factor = 0.9
        
        # Combat tracking
		self.last_player_attack = None
		self.last_enemy_action = None
        
		# player interaction
		self.can_attack = True
		self.attack_time = None
		self.attack_cooldown = 400
		self.damage_player = damage_player
		self.trigger_death_particles = trigger_death_particles
		self.add_exp = add_exp

		# invincibility timer
		self.vulnerable = True
		self.hit_time = None
		self.invincibility_duration = 300

		# sounds
		self.death_sound = pygame.mixer.Sound('audio/death.wav')
		self.hit_sound = pygame.mixer.Sound('audio/hit.wav')
		self.attack_sound = pygame.mixer.Sound(monster_info['attack_sound'])
		self.death_sound.set_volume(0.6)
		self.hit_sound.set_volume(0.6)
		self.attack_sound.set_volume(0.6)
  
		#for dodging distance
		self.is_dodging = False
		self.dodge_direction = None
		self.dodge_start_pos = None
		self.dodge_duration = 300  # milliseconds
		self.dodge_start_time = 0


	def import_graphics(self,name):
		self.animations = {'idle':[],'move':[],'attack':[]}
		main_path = f'graphics/monsters/{name}/'
		for animation in self.animations.keys():
			self.animations[animation] = import_folder(main_path + animation)

	def get_player_distance_direction(self,player):
		enemy_vec = pygame.math.Vector2(self.rect.center)
		player_vec = pygame.math.Vector2(player.rect.center)
		distance = (player_vec - enemy_vec).magnitude()

		if distance > 0:
			direction = (player_vec - enemy_vec).normalize()
		else:
			direction = pygame.math.Vector2()

		return (distance,direction)

	def get_status(self, player):
		distance = self.get_player_distance_direction(player)[0]

		if distance <= self.attack_radius and self.can_attack:
			if self.status != 'attack':
				self.frame_index = 0
			self.status = 'attack'
		elif distance <= self.notice_radius:
			self.status = 'move'
		else:
			self.status = 'idle'

	def actions(self,player):
			"""Ml Modification"""
			if self.status == 'attack':
				self.attack_time = pygame.time.get_ticks()
				
				# Use shared attack history to inform tactics
				if len(self.attack_history) > 5:
					weapon_attacks = self.attack_history.count('weapon')
					magic_attacks = len(self.attack_history) - weapon_attacks
					
					# Adjust behavior based on player's preferred attack type
					if magic_attacks > weapon_attacks * 1.5:  # Player prefers magic
						# Get closer to pressure magic users
						self.direction = self.get_player_distance_direction(player)[1]
						monster_info = monster_data[self.monster_name]
						self.speed = monster_info['speed'] * 1.3
					elif weapon_attacks > magic_attacks * 1.5:  # Player prefers weapons
						# Maintain optimal weapon range
						dist = self.get_player_distance_direction(player)[0]
						ideal_range = self.attack_radius * 0.8
						if dist < ideal_range:
							self.direction = self.get_player_distance_direction(player)[1] * -1
				
				self.damage_player(self.attack_damage, self.attack_type)
				self.attack_sound.play()
				
			elif self.status == 'move':
				self.direction = self.get_player_distance_direction(player)[1]
			else:
				self.direction = pygame.math.Vector2()

	def animate(self):
		animation = self.animations[self.status]
		
		self.frame_index += self.animation_speed
		if self.frame_index >= len(animation):
			if self.status == 'attack':
				self.can_attack = False
			self.frame_index = 0

		self.image = animation[int(self.frame_index)]
		self.rect = self.image.get_rect(center = self.hitbox.center)

		if not self.vulnerable:
			alpha = self.wave_value()
			self.image.set_alpha(alpha)
		else:
			self.image.set_alpha(255)

	def cooldowns(self):
		current_time = pygame.time.get_ticks()
		if not self.can_attack:
			if current_time - self.attack_time >= self.attack_cooldown:
				self.can_attack = True

		# Invincibility cooldown - only check if hit_time is not None
		if self.hit_time is not None:  # Add this check
			if not self.vulnerable:
				if current_time - self.hit_time >= self.invincibility_duration:
					self.vulnerable = True

	def get_damage(self, player, attack_type):
		"""ML Modification"""
		if self.vulnerable:
			self.hit_time = pygame.time.get_ticks()  # Always set hit_time when taking damage
			action = self.choose_action(attack_type)
			print(f"{self.monster_name} chose: {action} against {attack_type} attack")
			print(f"Q-table values: {self.q_table[attack_type]}")
			# Record player attack type in shared history
			self.attack_history.append(attack_type)
			if len(self.attack_history) > 20:  # Keep reasonable history size
				self.attack_history.pop(0)
			
			# Choose defensive action based on shared learning
			action = self.choose_action(attack_type)
			
			# Apply action effects
			if action == 'dodge':
				# 50% chance to dodge
				if random.random() < 0.5:
					self.dodge_direction = self.get_player_distance_direction(player)[1] * -1
					self.dodge_start_pos = pygame.math.Vector2(self.rect.center)
					self.is_dodging = True
					self.dodge_start_time = pygame.time.get_ticks()
					self.vulnerable = False
					self.hit_sound.play()
					self.update_q_table(1)  # Positive reward for successful dodge
					return
			
			elif action == 'block':
				# Reduce damage by 50%
				damage_reduction = 0.5
				self.hit_sound.play()
				self.direction = self.get_player_distance_direction(player)[1]
				if attack_type == 'weapon':
					self.health -= player.get_full_weapon_damage() * damage_reduction
				else:
					self.health -= player.get_full_magic_damage() * damage_reduction
				self.hit_time = pygame.time.get_ticks()
				self.vulnerable = False
				self.update_q_table(0.5)  # Moderate reward for blocking
			
			else:  # counter
				# Take full damage but counter-attack immediately
				self.hit_sound.play()
				self.direction = self.get_player_distance_direction(player)[1]
				if attack_type == 'weapon':
					self.health -= player.get_full_weapon_damage()
				else:
					self.health -= player.get_full_magic_damage()
				self.hit_time = pygame.time.get_ticks()
				self.vulnerable = False
				
				# Counter attack if still alive
				if self.health > 0:
					self.status = 'attack'
					self.actions(player)
					# Get monster info from settings
					monster_info = monster_data[self.monster_name]
					# Reward depends on remaining health
					reward = -0.2 if self.health < monster_info['health'] * 0.2 else 0.8
					self.update_q_table(reward)
			
			# Gradually reduce exploration rate in shared data
			self.shared_data['exploration_rate'] = max(0.05, self.exploration_rate * 0.995)

	def check_death(self):
		if self.health <= 0:
			self.kill()
			self.trigger_death_particles(self.rect.center,self.monster_name)
			self.add_exp(self.exp)
			self.death_sound.play()

	def hit_reaction(self):
		if not self.vulnerable:
			self.direction *= -self.resistance

	def update(self):
		self.hit_reaction()
		self.hit_reaction()
    
		current_time = pygame.time.get_ticks()
    
    	# Handle dodge movement
		if self.is_dodging:
			if current_time - self.dodge_start_time < self.dodge_duration:
				self.direction = self.dodge_direction
			else:
				self.is_dodging = False
            	# Calculate and print final dodge distance
				final_pos = pygame.math.Vector2(self.rect.center)
				dodge_distance = (final_pos - self.dodge_start_pos).length()
				print(f"{self.monster_name} dodged {dodge_distance:.1f} pixels backward")
    
		self.move(self.speed)
		self.animate()
		self.cooldowns()
		self.check_death()

	def enemy_update(self,player):
		self.get_status(player)
		self.actions(player)
  
	#ml method
	def update_q_table(self, reward):
		"""Update shared Q-values based on the last action and its outcome"""
		if self.last_player_attack and self.last_enemy_action:
			old_value = self.q_table[self.last_player_attack][self.last_enemy_action]
			max_q = max(self.q_table[self.last_player_attack].values())
			#q-learning formula
			new_value = old_value + self.learning_rate * (reward + self.discount_factor * max_q - old_value)
			self.q_table[self.last_player_attack][self.last_enemy_action] = new_value

	def choose_action(self, player_attack_type):
		"""Choose an action based on shared Q-values or exploration"""
		if random.random() < self.exploration_rate:
            # Explore: choose random action
			action = random.choice(list(self.q_table[player_attack_type].keys()))
		else:
            # Exploit: choose best known action from shared knowledge
			actions = self.q_table[player_attack_type]
			action = max(actions, key=actions.get)
        
		self.last_player_attack = player_attack_type
		self.last_enemy_action = action
		return action

 