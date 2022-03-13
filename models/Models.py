class Competition:
    def __init__(self, id, name, topic, year):
        self.id = id
        self.name = name
        self.topic = topic
        self.year = year

    def __str__(self):
        return "{ id: " + str(self.id) + " / topic: " + self.topic + " / year: " + str(self.year) + " / name: " + self.name + " }"


class Result:
    def __init__(self, competition, county, school, grade, rank):
        self.competition = competition
        self.county = county
        self.school = school
        self.grade = grade
        self.rank = rank

    def __str__(self):
        return "{ competition: " + self.competition + " / county: " + self.county + " / school: " + self.school + " / grade: " + self.grade + \
               " / rank: " + self.rank + " }"
