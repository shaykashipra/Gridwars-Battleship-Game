from BattleShip_Engine import Game, Player, GeneticAlgorithm
from matplotlib import pyplot

n_games = 10
n_shots = []
n_wins1 = 0
n_wins2 = 0

for i in range(n_games):
    print(f'game {i} running...')
    player1 = Player(use_ga=False)  #  GA for player 1
    player2 = Player(use_ga=False)  # not GA for player 2
    game = Game( human1=False, human2=False,player1=player1,player2=player2)
    #game = Game(human1 =False, human2= False)
    while not game.over:
        if game.player1_turn:
            game.basic_ai()
            #game.basic_ai_with_fuzzy()
        else:
            #game.basic_ai()
            #game.minmax_ai()
            game.basic_ai_with_fuzzy()
    n_shots.append(game.n_shots)
    if game.result == 1:
        n_wins1 += 1
    elif game.result == 2:
        n_wins2 += 1
print(n_shots)
print(n_wins1)
print(n_wins2)
#first move j dicche tar n_wins beshi hocche
values =[]
for i in range(17,200): #best case e 17 ta move cz 5+4+3+2+3 r worst case e 200 shots hbe cz 10X10 board 2 jon player
    values.append(n_shots.count(i))
'''
pyplot.bar(range(17,200),values)
pyplot.show() #random_ai  dile ekdom 200 er dike shb value,basic use korle onk better
'''

pyplot.bar(range(17, 200), values)
pyplot.title("Distribution of Shots per Game")
pyplot.xlabel("Number of Shots")
pyplot.ylabel("Frequency")
pyplot.show()

# Plotting wins by each player
players = ['Player 1', 'Player 2']
wins = [n_wins1, n_wins2]
pyplot.bar(players, wins, color=['blue', 'red'])
pyplot.title("Number of Wins per Player")
pyplot.xlabel("Players")
pyplot.ylabel("Wins")
pyplot.show()



