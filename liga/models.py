from django.db import models


# Create your models here.
class Competition(models.Model):
    external_id = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    topic = models.CharField(max_length=200)
    year = models.IntegerField()

    def __str__(self):
        return "{ id: " + self.external_id + " / topic: " + self.topic + " / year: " + str(self.year) + " / name: " + self.name + " }"

    def to_fixture(self):
        return ""


class County(models.Model):
    name = models.CharField(max_length=200)
    name_lower = models.CharField(max_length=200)

    def __str__(self):
        return "{ id: " + str(self.id) + " / name: " + self.name + " }"

    def to_fixture(self):
        return "- model: liga.county" \
               "  pk: 1" \
               "  fields:" \
               "    name: " + self.name


class Place(models.Model):
    name = models.CharField(max_length=200)
    name_lower = models.CharField(max_length=200)
    county = models.ForeignKey(
        County,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return "{ id: " + str(self.id) + " / name: " + self.name + " }"

    def to_fixture(self):
        return "- model: liga.place" \
               "  pk: 1" \
               "  fields:" \
               "    name: " + self.name


class School(models.Model):
    name = models.CharField(max_length=200)
    name_lower = models.CharField(max_length=200)
    county = models.ForeignKey(
        County,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return "{ id: " + str(self.id) + " / name: " + self.name + " }"


class Result(models.Model):
    grade = models.IntegerField()
    rank = models.IntegerField()
    performance = models.DecimalField(max_digits=5, decimal_places=2)
    county = models.ForeignKey(
        County,
        on_delete=models.CASCADE
    )
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE
    )
    competition = models.ForeignKey(
        Competition,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return "{ competition: " + self.competition.name + " / county: " + self.county.name + " / school: " + self.school.name + \
               " / grade: " + str(self.grade) + " / rank: " + str(self.rank) + " / performance: " + str(self.performance) + " }"
