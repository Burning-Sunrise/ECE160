import pygame
import sys

def handle_input(floor):
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

            mods = pygame.key.get_mods()
            shift = mods & pygame.KMOD_SHIFT

            # Switch symbols
            if pygame.K_1 <= event.key <= pygame.K_4:
                idx = event.key - pygame.K_1
                if idx < len(floor.symbols):
                    floor.current_index = idx
                    floor.current_symbol = floor.symbols[idx]
                    floor.shake_timer = 5

            # BUY
            if event.key == pygame.K_b and shift:
                sym = floor.current_symbol
                price = floor.current_price[sym]
                units = 2
                cost = price * units

                if floor.portfolio < cost:
                    return

                floor.portfolio -= cost

                if sym not in floor.position:
                    floor.position[sym] = {"entry": price, "units": units}
                else:
                    old_entry = floor.position[sym]["entry"]
                    old_units = floor.position[sym]["units"]
                    new_units = old_units + units
                    new_entry = (old_entry * old_units + price * units) / new_units
                    floor.position[sym]["entry"] = new_entry
                    floor.position[sym]["units"] = new_units

                floor.shake_timer = 5

            # SELL
            if event.key == pygame.K_s and shift:
                sym = floor.current_symbol
                if sym in floor.position:
                    entry = floor.position[sym]["entry"]
                    units = floor.position[sym]["units"]
                    price = floor.current_price[sym]
                    value = price * units
                    floor.portfolio += value
                    del floor.position[sym]
                    floor.shake_timer = 8

            # INSIDER TERMINAL
            if event.key == pygame.K_i and shift:
                if not floor.insider_active and floor.insider_cooldown == 0:
                    if floor.portfolio >= floor.insider_cost:
                        floor.portfolio -= floor.insider_cost
                        floor.insider_active = True
                        floor.insider_timer = 180
                        floor.insider_cooldown = 300

            # Toggle holdings
            if event.key == pygame.K_h:
                floor.show_holdings = not floor.show_holdings

        # Mouse tab switching
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if my < 40:
                tab_x = 30
                for i, sym in enumerate(floor.symbols):
                    if tab_x <= mx <= tab_x + 100:
                        floor.current_index = i
                        floor.current_symbol = sym
                        floor.shake_timer = 5
                        break
                    tab_x += 120
