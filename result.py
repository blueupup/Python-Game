class Result:
    def __init__(self, time_survived, mobs_slain):
        self.points = 0
        self.time_survived = time_survived
        self.mobs_slain = mobs_slain

    def calculate_points(self):
        