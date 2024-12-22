import requests
import pandas as pd
import json
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import re
from pprint import pprint

load_dotenv()


class UnderstatWrapper:
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


class TeamsData(UnderstatWrapper):
    def __init__(self, league: str, year: int):
        super().__init__(league, year)
        self.data = self.get_data("teams")


class FixturesData(UnderstatWrapper):
    def __init__(self, league: str, year: int):
        super().__init__(league, year)
        self.data = self.get_data("dates")


if __name__ == "__main__":
    epl_team_data = TeamsData("EPL", 2024)
    epl_fixture_data = FixturesData("EPL", 2024)
    pprint(epl_team_data.data)
    pprint(epl_fixture_data.data)
    print("BREAKPOINT!")
