from models import Team, MatchStats, Fixture
import requests
import json
from bs4 import BeautifulSoup
import re


class UnderstatScraper:
    def __init__(self, league: str, year: int):
        self.league = league
        self.year = year
        self.base_url = "https://understat.com/league/"
        self.url = self.base_url + league + "/" + str(year)
        self.match_data = self.get_match_data()
        self.schedule_data, self.team_data = self.get_schedule_and_team_data()

        self.get_match_ids()

    def get_data(self, table_name: str):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, "lxml")
        scripts = soup.find_all("script")
        p = re.compile(r"(?<=\(')[^']*(?='\))")

        data = [
            p.search(str(el)).group()
            for el in scripts
            if f"{table_name}Data" in str(el)
        ][0]
        data = data.encode("utf8").decode("unicode_escape")

        return json.loads(data)

    def get_match_data(self):
        match_data = self.get_data("teams")
        match_stats = []

        for team_id in match_data.keys():
            for history in match_data[team_id]["history"]:
                history["team_id"] = team_id
                match_stats.append(MatchStats(**history))

        return match_stats

    def get_schedule_and_team_data(self):
        teams = []
        fixtures = self.get_data("dates")
        fixtures = [Fixture(**fixture) for fixture in fixtures]

        for fixture in fixtures:
            teams += [fixture.h, fixture.a]

        teams = list(set(teams))
        teams = sorted(teams)

        return fixtures, teams

    def get_team_data(self):
        team_data = self.get_data("teams")
        teams = []
        for team_id in team_data:
            team_data[team_id].pop("history")
            teams.append(Team(**team_data[team_id]))

        return teams

    def get_match_ids(self):
        for match_stat in self.match_data:
            match_id = next(
                (
                    fixture.id
                    for fixture in self.schedule_data
                    if fixture.datetime == match_stat.date
                    and (
                        fixture.h.id == match_stat.team_id
                        if match_stat.h_a == "h"
                        else fixture.a.id == match_stat.team_id
                    )
                ),
                None,
            )
            match_stat.match_id = match_id


if __name__ == "__main__":
    epl_data = UnderstatScraper("EPL", 2024)
    print("BREAKPOINT!")
