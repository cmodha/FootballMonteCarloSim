import requests
import json
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import re
from pprint import pprint

load_dotenv()


# Base class that scrapes the data from the understat website.
class BaseWrapper:
    def __init__(self, league: str, year: int):
        self.league = league
        self.year = year
        self.base_url = "https://understat.com/league/"
        self.url = self.base_url + league + "/" + str(year)

    def get_data(self, table_name: str):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, "lxml")
        scripts = soup.find_all("script")
        p = re.compile(r"(?<=\(')[^']*(?='\))")

        team_data = [
            p.search(str(el)).group()
            for el in scripts
            if f"{table_name}Data" in str(el)
        ][0]
        team_data = team_data.encode("utf8").decode("unicode_escape")

        return json.loads(team_data)


# Class that formats the team data.
class Teams(BaseWrapper):
    def __init__(self, league: str, year: int):
        super().__init__(league, year)
        self.raw = self.get_data("teams")
        self.ref_table = self.get_team_names()
        self.data = self.format_data()

    @staticmethod
    def calculate_ppda_coefs(history: dict):
        history["ppda_coef"] = (
            history["ppda"]["att"] / history["ppda"]["def"]
            if history["ppda"]["def"] != 0
            else 0
        )
        history["ppda_allowed_coef"] = (
            history["ppda_allowed"]["att"] / history["ppda_allowed"]["def"]
            if history["ppda"]["def"] != 0
            else 0
        )

        return history

    @staticmethod
    def calculate_diffs(history: dict):
        history["xG_diff"] = history["xG"] - history["scored"]
        history["xGA_diff"] = history["xGA"] - history["missed"]
        history["xpts_diff"] = history["xpts"] - history["pts"]

        return history

    def format_data(self) -> list:
        match_histories = []

        for team_id in self.raw.keys():
            for history in self.raw[team_id]["history"]:
                history = self.calculate_ppda_coefs(history)
                history = self.calculate_diffs(history)
                history["team_id"] = team_id
                match_histories.append(history)

        return match_histories

    def get_team_names(self):
        teams = {}
        for team_id in self.raw:
            teams[team_id] = self.raw[team_id]["title"]
        return teams


# Class that formats the fixtures data.
class Fixtures(BaseWrapper):
    def __init__(self, league: str, year: int):
        super().__init__(league, year)
        self.data = self.get_data("dates")


# Class that scrapes the data from the understat website.
class UnderstatDataScraper:
    def __init__(self, league: str, year: int):
        self.league = league
        self.year = year
        self.teams = Teams(league, year)
        self.fixtures = Fixtures(league, year)

        self.teams.data = self.add_match_ids()

    def add_match_ids(self):
        new_data = []
        for match_stat in self.teams.data:
            # horrible filter to find match_id
            match_id = list(
                filter(
                    lambda fixture: (
                        fixture["datetime"] == match_stat["date"]
                    )  # looking for fixture with same date and team_id based on 'h_a' value.
                    and (
                        (fixture["h"]["id"] == match_stat["team_id"])
                        if match_stat["h_a"] == "h"
                        else (fixture["a"]["id"] == match_stat["team_id"])
                    ),
                    self.fixtures.data,
                )
            )

            match_stat["match_id"] = match_id[0].get("id", None) if match_id else None
            new_data.append(match_stat)

        return new_data


if __name__ == "__main__":
    epl_data = UnderstatDataScraper("EPL", 2024)
    pprint(epl_data.teams.ref_table)
    pprint(epl_data.teams.data)
    pprint(epl_data.fixtures.data)
