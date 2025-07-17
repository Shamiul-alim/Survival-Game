import pygame
pygame.init()
font = pygame.font.Font(None,30)

def debug(info,y = 10, x = 10):
	display_surface = pygame.display.get_surface()
	debug_surf = font.render(str(info),True,'White')
	debug_rect = debug_surf.get_rect(topleft = (x,y))
	pygame.draw.rect(display_surface,'Black',debug_rect)
	display_surface.blit(debug_surf,debug_rect)

def show_ai_info(enemy, y=50):
    if hasattr(enemy, 'q_table'):
        info = [
            f"Enemy: {enemy.monster_name}",
            f"Exploration: {enemy.exploration_rate:.2f}",
            "Weapon Responses:",
            f"  Dodge: {enemy.q_table['weapon']['dodge']:.2f}",
            f"  Block: {enemy.q_table['weapon']['block']:.2f}",
            f"  Counter: {enemy.q_table['weapon']['counter']:.2f}",
            f"Last Action: {getattr(enemy, 'last_enemy_action', 'None')}"
        ]
        
        for i, line in enumerate(info):
            debug(line, y=y + i*25)