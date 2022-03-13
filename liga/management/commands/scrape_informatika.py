#!/usr/bin/env python3

import urllib.request
import re
from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup
from liga.models import County, Competition, School, Result


class Command(BaseCommand):
    help = 'Loads all counties to the database.'

    def handle(self, *args, **options):
        counties = County.objects.all()
        counties_domain = get_counties()
        for number in range(0, 1000):
            try:
                scrape_competition(number, counties, counties_domain)
            except Exception as e:
                self.stdout.write(self.style.ERROR('Error scraping competition "%s"' % number))
        # scrape_competition(1, counties, counties_domain)


def get_selected(div):
    if div is None:
        return None
    li_selected_category = div.findChildren("li", attrs={'class': 'selected'}, recursive=True)
    selected_category = li_selected_category[0].findChildren("span", attrs={'class': 'center'}, recursive=True)
    return selected_category[0].text


def scrape_competition(number, counties, counties_domain):
    existing_competition = Competition.objects.filter(external_id=number)
    if len(existing_competition) != 0:
        #print("Competition \""+existing_competition[0].name+"\" is already scraped.")
        return
    url = "https://informatika.azoo.hr/natjecanje/dogadjaj/" + str(number) + "/rezultati"
    parsed_html = get_parsed_html(url)
    category = get_selected(parsed_html.body.find('div', attrs={'id': 'categoryList'}))
    if category is None:
        return
    year = get_selected(parsed_html.find('div', attrs={'id': 'yearList'}))
    competition_name = get_selected(parsed_html.body.find('div', attrs={'id': 'competitionList'}))
    event = get_selected(parsed_html.body.find('div', attrs={'id': 'competitionEventList'}))
    competition = Competition()
    competition.external_id = number
    competition.name = category.strip()+" "+competition_name.strip()+" "+event.strip()
    competition.topic = 'Informatika'
    competition.year = year
    competition.save()

    top_score = get_top_score(number)

    for county in counties:
        # print("Scraping competition \""+competition.name+"\" for county "+county.name)
        county_id = counties_domain[county.name_lower]
        scrape_schools(competition, county, county_id)

    scrape_results(competition, top_score)


def get_counties():
    parsed_html = get_parsed_html("https://informatika.azoo.hr/natjecanje/dogadjaj/1/rezultati")
    counties_element = parsed_html.body.find('select', attrs={'id': 'regionFilter'})
    counties = counties_element.findChildren("option", recursive=True)
    county_dictionary = {}
    for county in counties:
        county_dictionary[str(county.text).lower()] = county['value']
    return county_dictionary


def scrape_results(competition, top_score):
    result_list = []
    page = 1
    page_counter = 0

    while page is not None:
        url = "https://informatika.azoo.hr/Parts/CompetitionEventController/ResultsListPage?page="+str(page_counter) + \
              "&competitionEventId=" + str(competition.external_id)
        #print(url)
        page_content = get_raw_html(url)
        if page_content.strip().startswith("<!DOCTYPE html"):
            page = None
        else:
            parsed_html = BeautifulSoup(page_content, features="html.parser")
            rows = parsed_html.findChildren('tr', recursive=False)
            if len(rows) == 1 & (rows[0].findChildren('tr', attrs={'class':'emptyList'}) is not None):
                return result_list
            for row in rows:
                rank = row.findChildren("td", attrs={'class': 'rank'})[0].text
                grade = row.findChildren("td", attrs={'class': 'grade'})[0].text
                school_name = row.findChildren("td", attrs={'class': 'school'})[0].text
                schools = School.objects.filter(name_lower=school_name.strip().lower())
                school = schools[0]

                result_columns = row.findChildren("td", attrs={'class': 'result-column'})

                if len(result_columns) > 0:
                    score = result_columns[-1].text
                else:
                    score = top_score - int(rank) + 1

                performance = 0 if top_score == 0 else round(float(str(score).replace(',', '.'))/top_score, 4)*100

                result = Result()
                result.competition = competition
                result.county = school.county
                result.school = school
                result.grade = grade
                result.rank = rank
                result.performance = performance

                result.save()

                result_list.append(result)
            page_counter = page_counter + 1
    return result_list


def scrape_schools(competition, county, county_id):
    page = 1
    page_counter = 0

    while page is not None:
        url = "https://informatika.azoo.hr/Parts/CompetitionEventController/ResultsListPage?page="+str(page_counter) + \
              "&competitionEventId=" + str(competition.external_id)+"&filterRegionId=" + str(county_id)
        #print(url)
        page_content = get_raw_html(url)
        if page_content.strip().startswith("<!DOCTYPE html"):
            page = None
        else:
            parsed_html = BeautifulSoup(page_content, features="html.parser")
            rows = parsed_html.findChildren('tr', recursive=False)
            if len(rows) == 0:
                return
            for row in rows:
                school_field = row.findChildren("td", attrs={'class': 'school'})
                if len(school_field) == 0:
                    return
                school_name = row.findChildren("td", attrs={'class': 'school'})[0].text
                schools = School.objects.filter(name_lower=school_name.strip().lower())

                if len(schools) == 0:
                    school = School()
                    school.name = school_name.strip()
                    school.name_lower = school_name.strip().lower()
                    school.county = county
                    school.save()
                    #print(school.name+" "+school.county.name)
        page_counter = page_counter + 1



def get_top_score(number):
    url_participants = "https://informatika.azoo.hr/Parts/CompetitionEventController/FilteredResults?competitionEventId="+str(number)
    url_results = "https://informatika.azoo.hr/Parts/CompetitionEventController/ResultsListPage?page=0&competitionEventId=" + str(number)+"&filterRegionId="
    top_score = -1
    content_results = get_parsed_html(url_results)
    all_rows = content_results.findChildren('tr', recursive=False)
    if len(all_rows) > 0:
        columns = all_rows[0].findChildren("td", attrs={'class': 'result-column'})
        if len(columns) > 0:
            top_score = float(str(columns[-1].text).replace(',', '.'))
    else:
        content_participants = get_parsed_html(url_participants)
        top_score = int(re.findall("[0-9]+", str(content_participants.findChildren('div', attrs={'class': 'count'})[0].text))[0])
    return top_score


def get_parsed_html(url):
    html = get_raw_html(url)
    parsed_html = BeautifulSoup(html, features="html.parser")
    return parsed_html


def get_raw_html(url):
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    html_bytes = response.read()
    response.close()
    html = html_bytes.decode("utf8")
    return html
