from lxml import html
import requests
import operator
class playerDayFromRotoWorld:

     def __init__(self, statArray):
         self.date = statArray[0]
         self.gid = statArray[1]
         self.pos = statArray[2]
         self.name = statArray[3]
         self.starter = len(statArray[4]) == 0
         self.dkpoints = float(statArray[5])
         if statArray[6] == 'N/A':
             self.salary = 100000
         else:
             self.salary = int(statArray[6].strip('$').replace(',',''))
         self.team = statArray[7]
         self.home = statArray[8] == 'H'
         self.opponent = statArray[9]
         self.team_score = statArray[10]
         self.opponent_score = statArray[11]
         self.minutes = statArray[12]
         statLine = statArray[13].split(' ')
         for stat in statLine:
             if stat.find('pt') > -1:
                  self.points = int(stat.strip('pt'))
             if stat.find('rb') > -1:
                  self.rebounds = int(stat.strip('rb'))
             if stat.find('as') > -1:
                  self.assists = int(stat.strip('as'))
             if stat.find('st') > -1:
                  self.steals = int(stat.strip('st'))
             if stat.find('to') > -1:
                  self.turnovers = int(stat.strip('to'))
             if stat.find('trey') > -1:
                  self.threes = int(stat.strip('trey'))
             if stat.find('fg') > -1:
                  self.field_goals_attempted = int(stat.strip('fg').split('-')[1])
                  self.field_goals_made = int(stat.strip('fg').split('-')[0])
             if stat.find('ft') > -1:
                  self.free_throws_attempted = int(stat.strip('ft').split('-')[1])
                  self.free_throws_made = int(stat.strip('ft').split('-')[0])

     def getValue(self):
         if self.dkpoints == 0:
             return -10000
         return self.dkpoints * self.dkpoints * self.dkpoints / self.salary

     def __lt__(self, other):
         return self.getValue() > other.getValue()

	 def out(self):
		 print self.name + ' ' + self.salary + ' '
class shotScrape:
	def __init__(self, days, mons, years, url=None, do_replacement=False):
		self.data=None
		self.days = days
		self.mons = mons
		self.years = years
		if url is None:
			self.url='http://rotoguru1.com/cgi-bin/hyday.pl?mon=${mon}&day=${day}&year=${year}&game=dk&scsv=10'
		if do_replacement:
			self.url = self.url.replace('${mon}', self.mons)
			self.url = self.url.replace('${day}', self.days)
			self.url = self.url.replace('${year}', self.years)

	def get(self, reset=False):
		if reset or self.data is None:
			page = requests.get(self.url)
			self.data = page.content
		t = html.fromstring(self.data)
		rawDayData = t.xpath('//table/pre/text()')
		players = []
		for player in rawDayData[0].split('\n')[1:]:
			if player is '' :
				continue
			players.append(playerDayFromRotoWorld(player.split(';')))
		return players

class dkTeam:
	team_salary=50000
	def __init__(self):
		self.players = []
		self.pg = None
		self.sg = None
		self.sf = None
		self.c = None
		self.pf = None
		self.util = None
		self.g = None
		self.f = None

	def isOverCap(self):
		return sum([p.salary for p in self.players]) > self.team_salary

	def isValidTeam(self):
		if self.isOverCap():
			return False
		if self.pg is None or self.sg is None or self.sf is None or self.pf is None:
			return False
		if self.util is None or self.c is None or self.f is None or self.g is None:
			return False
		return True

	def getNumRemainingPlayers(self):
		return 8 - len(self.players)

	def copy(self, other):
		other.players = list(self.players)
		other.pg = self.pg
		other.sg = self.sg
		other.sf = self.sf
		other.c = self.c
		other.pf = self.pf
		other.util = self.util
		other.g = self.g
		other.f = self.f

	def clearPlayers(self):
		self.players=[]
		self.pg = None
		self.sg = None
		self.sf = None
		self.c = None
		self.pf = None
		self.util = None
		self.g = None
		self.f = None

	def addPG(self, pg):
		if self.pg is not None:
			return False
		if pg.pos != 'PG':
			return False
		self.pg = pg
		if self.isOverCap() or pg in self.players:
			self.pg = None
			return False
		self.players.append(pg)
		return True

	def removePG(self):
		if self.pg is not None:
			self.players.remove(self.pg)
			self.pg = None

	def addSG(self, sg):
		if self.sg is not None:
			return False
		if sg.pos != 'SG':
			return False
		self.sg = sg
		if self.isOverCap() or sg in self.players:
			self.sg = None
			return False
		self.players.append(sg)
		return True

	def removeSG(self):
		if self.sg is not None:
			self.players.remove(self.sg)
			self.sg = None

	def addPF(self, pf):
		if self.pf is not None:
			return False
		if pf.pos != 'PF':
			return False
		self.pf = pf
		if self.isOverCap() or pf in self.players:
			self.pf = None
			return False
		self.players.append(pf)
		return True

	def removePF(self):
		if self.pf is not None:
			self.players.remove(self.pf)
			self.pf = None

	def addSF(self, sf):
		if self.sf is not None:
			return False
		if sf.pos != 'SF':
			return False
		self.sf = sf
		if self.isOverCap() or sf in self.players:
			self.sf = None
			return False
		self.players.append(sf)
		return True

	def removeSF(self):
		if self.sf is not None:
			self.players.remove(self.sf)
			self.sf = None

	def addC(self, c):
		if self.c is not None:
			return False
		if c.pos != 'C':
			return False
		self.c = c
		if self.isOverCap() or c in self.players:
			self.c = None
			return False
		self.players.append(c)
		return True

	def removeC(self):
		if self.c is not None:
			self.players.remove(self.c)
			self.c = None

	def addG(self, g):
		if self.g is not None:
			return False
		if g.pos != 'PG' and g.pos != 'SG':
			return False
		self.g = g
		if self.isOverCap() or g in self.players:
			self.g = None
			return False
		self.players.append(g)
		return True

	def removeG(self):
		if self.g is not None:
			self.players.remove(self.g)
			self.g = None

	def addF(self, f):
		if self.f is not None:
			return False
		if f.pos != 'PF' and f.pos != 'SF':
			return False
		self.f = f
		if self.isOverCap() or f in self.players:
			self.f = None
			return False
		self.players.append(f)
		return True

	def removeF(self):
		if self.f is not None:
			self.players.remove(self.f)
			self.f = None

	def addUtil(self, util):
		if self.util is not None:
			return False
		self.util = util
		if self.isOverCap() or util in self.players:
			self.util = None
			return False
		self.players.append(util)
		return True

	def removeUtil(self):
		if self.util is not None:
			self.players.remove(self.util)
			self.util = None

	def getScore(self):
		return sum([q.dkpoints for q in self.players])

	def getRemainingBudget(self):
		return self.team_salary - sum([p.salary for p in self.players])

	#def printTeam(self):
		#print 'PG / SG / SF / PF / C / G / F / Util: ' + self.pg.print() + self.sg.print() + self.sf.print() + self.pf.print() + self.c.print() + self.g.print() + self.f.print() + self.util.print()


class SetOfPlayers:
	def key1(self, a):
		return(a.salary, -a.dkpoints)

	def getValidPlayers(self,players,num=3):
		tmp1=[0] * num
		players.sort(key=self.key1)
		counter=0
		while counter < len(players):
			tmp1.sort(reverse=True)
			player = players[counter]
			if player.dkpoints <= tmp1[-1]:
				players.remove(player)
				continue
			tmp1.pop()
			tmp1.append(player.dkpoints)
			counter += 1
		return players

	def __init__(self, players):
		players.sort()
		self.bestVal = players[0].dkpoints / players[0].salary
		self.pgs=self.getValidPlayers([x for x in players if x.pos == 'PG' and x.dkpoints > 0])
		self.sgs=self.getValidPlayers([x for x in players if x.pos == 'SG' and x.dkpoints > 0])
		self.gs=self.getValidPlayers( self.sgs + self.pgs )
		self.pfs=self.getValidPlayers([x for x in players if x.pos == 'PF' and x.dkpoints > 0])
		self.sfs=self.getValidPlayers([x for x in players if x.pos == 'SF' and x.dkpoints > 0])
		self.fs=self.getValidPlayers( self.pfs + self.sfs )
		self.cs=self.getValidPlayers([x for x in players if x.pos == 'C' and x.dkpoints > 0], 2)
		self.uts=self.getValidPlayers( self.gs + self.fs + self.cs )

	def notGoingToWork(self, team, bestTeam):
		if team.getNumRemainingPlayers() * 3000 > team.getRemainingBudget():
			return True
		if team.getRemainingBudget() * self.bestVal + team.getScore() < bestTeam.getScore():
			return True
		return False

	def getPerms(self):
		return len(self.pgs) * len(self.sgs) * len(self.gs) * len(self.sfs) * len(self.pfs) * len(self.cs)* len(self.fs) * len(self.uts)

	def getStats(self):
		return (self.bestTeam.getScore(), self.tries, self.getPerms(), float(self.tries) / self.getPerms(), len(self.improvements), self.improvements)

	def findBest(self):
		self.pgs.sort()
		self.sgs.sort()
		self.gs.sort()
		self.pfs.sort()
		self.sfs.sort()
		self.cs.sort()
		self.fs.sort()
		self.uts.sort()
		self.bestTeam = dkTeam()
		self.tries = 0
		self.improvements = []
		for pg in self.pgs:
			team = dkTeam()
			team.removePF()
			if not team.addPG(pg) or self.notGoingToWork(team, self.bestTeam):
				team.removePG()
				continue
			for sg in self.sgs:
				if not team.addSG(sg) or self.notGoingToWork(team, self.bestTeam):
					team.removeSG()
					continue
				for g in self.gs:
					if not team.addG(g) or self.notGoingToWork(team, self.bestTeam):
						team.removeG()
						continue
					for pf in self.pfs:
						if not team.addPF(pf) or self.notGoingToWork(team, self.bestTeam):
							team.removePF()
							continue
						for sf in self.sfs:
							if not team.addSF(sf) or self.notGoingToWork(team, self.bestTeam):
								team.removeSF()
								continue
							for f in self.fs:
								if not team.addF(f) or self.notGoingToWork(team, self.bestTeam):
									team.removeF()
									continue
								for c in self.cs or self.notGoingToWork(team, self.bestTeam):
									if not team.addC(c) or self.notGoingToWork(team, self.bestTeam):
										team.removeC()
										continue
									for ut in self.uts:
										if not team.addUtil(ut) or self.notGoingToWork(team, self.bestTeam):
											team.removeUtil()
											continue
										self.tries += 1
										if team.getScore() > self.bestTeam.getScore() and team.isValidTeam():
											self.improvements.append((self.tries, self.bestTeam.getScore()))
											self.bestTeam.clearPlayers()
											team.copy(self.bestTeam)
										team.removeUtil()
									team.removeC()
								team.removeF()
							team.removeSF()
						team.removePF()
					team.removeG()
				team.removeSG()



def doThing(y):
	ys=[y[x:x+20] for x in range(10)]
	ns=[SetOfPlayers(x) for x in ys]
	for n in ns:
		t1=time.time()
		n.findBest()
		t2=time.time()
		print t2-t1
		print n.getStats()
		if len(n.bestTeam.players) is not 0:
			print [x.name for x in n.bestTeam.players]

def __main__():
	yesterday=shotScrape('0','0','0', None, True)
	players=yesterday.get()
	players.sort()
	doThing(players)