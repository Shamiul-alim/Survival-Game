import pygame, sys
from settings import *
from level import Level
from enemy import init_learning,save_learning_data
init_learning()

class Game:
	def __init__(self):
		
		# general setup
		pygame.init()
		self.screen = pygame.display.set_mode((WIDTH,HEIGTH))
		pygame.display.set_caption('Survival Game')
		self.clock = pygame.time.Clock()

		self.level = Level()

		# sound 
		main_sound = pygame.mixer.Sound('audio/main.ogg')
		main_sound.set_volume(0.5)
		main_sound.play(loops = -1)
	
	def run(self):
			while True:
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						pygame.quit()
						sys.exit()
					if event.type == pygame.KEYDOWN:
						if event.key == pygame.K_m:
							self.level.toggle_menu()	
						if event.key == pygame.K_s:  # Debug save
							save_learning_data()
							print("Manually saved learning data!")

				self.screen.fill(WATER_COLOR)
				self.level.run()
				pygame.display.update()
				self.clock.tick(FPS)

	def quit_game(self):
		save_learning_data()
		pygame.quit()
		sys.exit()

if __name__ == '__main__':
	game = Game()
	game.run()