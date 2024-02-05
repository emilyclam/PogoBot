class QuizPlayer:
    def __init__(self, name):
        self.name = name
        self.points = 0

    def __str__(self):
        return f"{self.name} ({self.points})"

    def add_points(self):
        self.points += 1

