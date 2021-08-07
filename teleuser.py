class Teleuser:
    def __init__(self, id):
        self.id = id
        self.name = ''
        self.sex = ''
        self.age = 0
        self.city = ''
        self.description = ''
        self.photo = ''
        self.interests_arr = []
        self.mode = ['main_menu', 0]
        self.profile_created = False

    def __str__(self):
        return f"{self.name}, {self.age}, {self.city}\n\n{self.description}\n\nInterests: {', '.join(self.interests_arr)}"
