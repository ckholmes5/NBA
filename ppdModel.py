import requests
from lxml import html


def get():
    url = 'http://rotoguru1.com/cgi-bin/hyday.pl?mon=' + str(11) + '&day=' + str(4) + '&year=' + str(2014) + '&game=dk&scsv=0'
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
print get()