#THIS IS WHERE ALL OF THE UPDATING OF VALUES FOR THE HUD AND STATES WILL BE HELD
#THIS IS THE "BRAINS" OF THIS PROGRAM AND THE STORAGE OF THE SYSTEM THAT THEN FEEDS TO THE OTHER GAMES


# THIS IS WHERE ALL OF THE UPDATING OF VALUES FOR THE HUD AND STATES WILL BE HELD
# THIS IS THE "BRAINS" OF THIS PROGRAM AND THE STORAGE OF THE SYSTEM THAT THEN FEEDS TO THE OTHER GAMES

class GameState:
    def __init__(self):
        # --- Core Player Stats ---
        self.money = 1000          # Starting money
        self.day = 1               # Current day
        self.stress = 0            # Mood / stress level
        self.max_stress = 100      # Stress cap

        # --- Trading Limits ---
        self.max_trades_per_day = 3
        self.trades_today = 0

        # --- Time of Day ---
        self.time_of_day = "DAY"   # DAY or NIGHT

    # ------------------------------------------------
    # Trading Logic
    # ------------------------------------------------
    def record_trade(self):
        """Call this when the player performs a trade."""
        self.trades_today += 1

        # Increase stress each trade
        self.add_stress(10)

        # If out of trades, switch to night
        if self.trades_today >= self.max_trades_per_day:
            self.time_of_day = "NIGHT"

    def reset_trades(self):
        """Reset trades at the start of a new day."""
        self.trades_today = 0

    # ------------------------------------------------
    # Stress / Mood Logic
    # ------------------------------------------------
    def add_stress(self, amount):
        self.stress += amount
        if self.stress > self.max_stress:
            self.stress = self.max_stress

    def recover_stress(self, amount):
        """General stress recovery function."""
        self.stress -= amount
        if self.stress < 0:
            self.stress = 0

    def recover_stress_pills(self, amount):
        """Recovery from pills."""
        self.recover_stress(amount)

    def recover_stress_night(self, amount):
        """Recovery from sleeping at night."""
        self.recover_stress(amount)

    def is_nightmare(self):
        """If stress hits max, trigger nightmare screen."""
        return self.stress >= self.max_stress

    # ------------------------------------------------
    # Day/Night Cycle
    # ------------------------------------------------
    def advance_day(self):
        """Move to the next day and reset daily stats."""
        self.day += 1
        self.time_of_day = "DAY"
        self.reset_trades()

        # Recover stress each morning
        self.recover_stress_night(20)

    # ------------------------------------------------
    # Money Management
    # ------------------------------------------------
    def add_money(self, amount):
        self.money += amount

    def subtract_money(self, amount):
        self.money -= amount
        if self.money < 0:
            self.money = 0
