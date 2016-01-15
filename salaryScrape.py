from lxml import html
import requests
import json
import os


#TODO: Put this into the constants folder
baseDir = '/Users/christianholmes/NBA'
priceDir = baseDir + '/players/2015/Prices/'

intDays = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31]
intMonths = [10,11,12,1,2,3,4,5]
intYears = [2015,2016]

class shotScrape:

    def __init__(self, days, mons, years):
        self.days = days
        self.mons = mons
        self.years = years


    def get(self):
        url = 'http://rotoguru1.com/cgi-bin/hyday.pl?mon=' + str(self.mons) + '&day=' + str(self.days) + '&year=' + str(self.years) + '&game=dk&scsv=0'
        page = requests.get(url)
        tree = html.fromstring(page.content)
        rawNames = tree.xpath('//tr/td/a["href="]/text()')
        rawPrices = tree.xpath('//td[@align="right"]/text()')
        names = []
        prices = []
        for i in rawNames:
            if ',' in i:
                names.append(i)

        for i in rawPrices:
            if '$' in i or i == 'N/A':
                prices.append(i)


        playerPrices = {}

        for i in range(len(names)):
            playerPrices[names[i]] = prices[i]

        return playerPrices

    def doSavePrices(self):
        prices = self.get()
        with open(priceDir + str(self.mons) + '_' + str(self.days) + '_' + str(self.years), 'w') as outfile:
			json.dump(prices, outfile)

def scrapeAllPrices():
    for year in intYears:
        for mon in intMonths:
            for day in intDays:

                if mon >= 10 and year == 2015:
                    tmp = shotScrape(day,mon,year)
                    tmp.doSavePrices()
                    print tmp
                if mon <= 5 and year == 2016:
                    tmp = shotScrape(day, mon, year)
                    tmp.doSavePrices()
                    print tmp


scrapeAllPrices()
