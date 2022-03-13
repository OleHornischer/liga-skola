from django.core.management.base import BaseCommand, CommandError
from liga.models import County


class Command(BaseCommand):
    help = 'Loads all counties to the database.'

    def handle(self, *args, **options):
        counties = (
            "Zagrebačka",
            "Krapinsko-zagorska",
            "Sisačko-moslavačka",
            "Karlovačka",
            "Varaždinska",
            "Koprivničko-križevačka",
            "Bjelovarsko-bilogorska",
            "Primorsko-goranska",
            "Ličko-senjska",
            "Virovitičko-podravska",
            "Požeško-slavonska",
            "Brodsko-posavska",
            "Zadarska",
            "Osječko-baranjska",
            "Šibensko-kninska",
            "Vukovarsko-srijemska",
            "Splitsko-dalmatinska",
            "Istarska",
            "Dubrovačko-neretvanska",
            "Međimurska",
            "Grad Zagreb"
        )
        for county_name in counties:
            county = County()
            county.name = county_name
            county.name_lower = county_name.lower()

            county.save()

            self.stdout.write(self.style.SUCCESS('Successfully saved county "%s"' % county))
