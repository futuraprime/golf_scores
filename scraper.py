import requests
import time
import csvkit as csv
from bs4 import BeautifulSoup as Soup

URL = 'http://espn.go.com/golf/leaderboard11/controllers/ajax/playerDropdown'

def parseTable(table, playerId, tournamentId):
    data = [r.find_all('td') for r in table.find_all('tr')]
    out = []
    for i,x in enumerate(data[0]):
        if not x.text.isdigit():
            continue
        out.append({
            'playerId' : playerId,
            'tournamentId' : tournamentId,
            'hole' : int(x.text),
            'par' : int(data[1][i].text),
            'score' : int(data[2][i].text)
        })
    return out

def parsePlayer(tournamentId, playerId):
    r = requests.get(URL, params={
        'playerId' : playerId,
        'tournamentId' : tournamentId,
        'xhr' : 1
    })
    time.sleep(1)
    print(r.url)
    s = Soup(r.text, 'html.parser')
    l = [parseTable(r, playerId, tournamentId) for r in s.find_all(class_='scorecard-table')]
    return [item for sublist in l for item in sublist]

def parseTournament(tournamentId, playerList):
    final_data = [parsePlayer(tournamentId, playerId) for playerId in playerList]
    return [item for sublist in final_data for item in sublist]

#finalData = parseTournament(309, [66,686])

finalData = []

# load in our data
def readTournamentPlayers(row):
    r = [int(r) if r.isdigit() else r for r in row]
    playerList = [id for id in r[3:] if id != '']
    tournamentId = r[2]
    return { 'tournamentId' : tournamentId, 'playerList' : playerList }

with open('tournaments.csv') as f:
    reader = csv.reader(f)
    reader.next() #toss the header row
    tournaments = [readTournamentPlayers(row) for row in reader]

print tournaments

finalData = parseTournament(**tournaments[0])

with open('data.csv', 'w+') as f:
    writer = csv.DictWriter(f, fieldnames=['playerId','tournamentId','hole','par','score'])

    writer.writeheader()
    writer.writerows(finalData)
