#THIS IS WHERE ALL OF THE UPDATING OF VALUES FOR THE HUD AND STATES WILL BE HELD
#THIS IS THE "BRAINS" OF THIS PROGRAM AND THE STORAGE OF THE SYSTEM THAT THEN FEEDS TO THE OTHER GAMES


class GameState:
    def __init__(self):

        #Initial starting progression
        self.day = 1
        self.trades_today = 0

        #player statistics
        self.stress = 0       #From 0 to 100 possible ***subject to change
        self.money = 500

        #rules / limits
        self.max_trades_per_day = 3
        self.max_stress = 100

    #------------------------------------------------
    # Trade Logic and Documentation
    #------------------------------------------------
    def register_trade(self):
        self.trades_today += 1

        #***For now, putting stress increasing with each trade as default
        self.stress += 10
        self.stress = min(self.stress, self.max_stress)

        #check if the day is over
        if self.trades_today >= self.max_trades_per_day:
            return "DAY_OVER"
        return "OK"
    
    #--------------------------------------------------
    # Pharmacy / Recovery Mechanics
    #--------------------------------------------------
    def reduce_stress(self, amount):
        self.stress -= amount
        self.stress = max(0, self.stress)
    
    def spend_money(self, amount):
        if self.money >= amount:
            self.money -= amount
            return True
        else:
            return False
    
    #----------------------------------------------------
    # End of day outcome logic
    #----------------------------------------------------

    """Determining the outcome of what happens after the recovery room"""
    def end_of_night_outcome(self):
        if self.stress >= 100:
            return "GAME_OVER"
    
        if self.stress >= 50:
            return "NIGHTMARE"
        else:
            return "STATUS_QUO"
    
    #------------------------------------------------------
    # Day progression and counting
    #-----------------------------------------------------

    def next_day(self):
        #moves to the next day
        self.day += 1
        self.trades_today = 0