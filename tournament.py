from pypokerengine.api.game import setup_config, start_poker
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
from bots import RandoPlayer, CowardPlayer, FishPlayer, HotheadPlayer, RankedHandPlayer, EvolvingRankedHandPlayer, EvolvingRankAndTablePlayer

import numpy as np
import time
from pandas import DataFrame, read_csv

def random_name():
    first = ['Alice', 'Bob', 'Charlie', 'Danny', 'Eve', 'Frankie', 'Gavin', 'Harry', 'Irma', 'Katherine', 'Larry', 'Babyface', 'Dudebro', 'Bobby', 'Rolf', 'Gunter', 'Isaac', 'Moe', 'Betty', 'Chip', 'Chop', 'Woody', 'Wow', 'Bearface', 'Leeroy', 'Bam', 'Mr.', 'Miss', 'Madam', 'Sir', 'Old']

    last = ['the Lucky', 'Five Toes', 'Hugginkiss', 'Bobson', 'Blobson', 'the Unlucky', 'the Incompetent', 'Rogers', 'Nah', 'Brosef', 'Knuckles', 'Marston', 'the Dead', 'the Freak', 'Bossanova', 'Guntersnicker', 'Jenkins', 'the Insufferable', 'the Ugly', 'Murderface', 'the Excellent', 'McFish', 'of the Sea', 'Nugget', 'Fish Fillet', 'the Unwise', 'the Unsteady']

    return np.random.choice(first) + ' ' + np.random.choice(last)

def clone(player):
    if str(player) == "Rando":
        return RandoPlayer()
    elif str(player) == "Fish":
        return FishPlayer()
    elif str(player) == "RankedHand":
        return RankedHandPlayer()
    elif "EvolvingRankedHand" in str(player):
        new_player = player.breed()
        return new_player
    elif "EvolvingRankAndTablePlayer" in str(player):
        new_player = player.breed()
        return new_player
    elif str(player) == "Hothead":
        return HotheadPlayer()
    else:
        raise Exception("Could not clone", player)

def rank(hand):
    suited = ' '
    if hand[0][0] == hand[1][0]:
        suited = 's '
    elif hand[0][1] != hand[1][1]:
        suited = 'o '
    handstr = hand[0][1] + hand[1][1] + suited
    try:
        hand = ranked_hands.loc[handstr]
    except:
        handstr = hand[1][1] + hand[0][1] + suited
        hand = ranked_hands.loc[handstr]
    # print(handstr, hand)
    return hand['Rank ']

def fitness(player):
    # returns an absolute score of the player's fitness, the higher the better
    _sum = sum(player['results'])
    median = np.median(player['results'])
    # print("\t\t\t\t\t\tfitness for", player['class'], _sum, median)
    return _sum

initial_stack = 100
games_per_iter = 30
generations = 10

raise_thresh = 40
check_thresh = 90
raise_pwin = 0.2
check_pwin = 0.1
players_dict = {
    # random_name(): { 'class': CowardPlayer(), 'type':"Coward", 'results':[]},
    # random_name(): { 'class': FishPlayer(), 'type':"Fish", 'results':[]},
    # random_name(): { 'class': FishPlayer(), 'type':"Fish", 'results':[]},
    random_name(): { 'class': HotheadPlayer(), 'type':"Hothead", 'results':[]},
    random_name(): { 'class': HotheadPlayer(), 'type':"Hothead", 'results':[]},
    # random_name(): { 'class': RankedHandPlayer(), 'type':"RankedHandPlayer", 'results':[]},
    # random_name(): { 'class': RankedHandPlayer(), 'type':"RankedHandPlayer", 'results':[]},
    random_name(): { 'class': EvolvingRankedHandPlayer(),
                     'type':"EvolvingRankedHandPlayer", 'results':[]
    },
    random_name(): { 'class': EvolvingRankedHandPlayer(),
                     'type':"EvolvingRankedHandPlayer", 'results':[]
    },
    random_name(): { 'class': EvolvingRankedHandPlayer(),
                     'type':"EvolvingRankedHandPlayer", 'results':[]
    },
    # random_name(): { 'class': EvolvingRankAndTablePlayer(raise_pwin, check_pwin, raise_thresh, check_thresh),
    #                  'type':"EvolvingRankAndTablePlayer", 'results':[]
    # },
}

print('\n')
class_fitnesses = { p['type']:[] for p in players_dict.values()}

for h in range(0, generations):
    config = setup_config(max_round=50, initial_stack=initial_stack, small_blind_amount=2)
    for name,player in players_dict.items():
        players_dict[name]['results'] = []
    print(f'\n=== players list {h+1} ===')
    for name,player_dict in players_dict.items():
        print(f"{name:27} ({player_dict['class']})")
        config.register_player(name=name, algorithm=player_dict['class'])
    print('\n')
    for i in range(0,games_per_iter):
        results_str = ''
        # class_results = {}
        game_result = start_poker(config, verbose=0)
        for player in game_result['players']:
            name = player['name']
            players_dict[name]['results'].append(player['stack'])
        results_str += f"{int(i)} games"
        print(results_str, end='\r')

    print('\n')
    best_player = None
    deleteme = None
    lowest_fitness = float('inf')
    highest_fitness = 0

    possible_winnings = initial_stack * games_per_iter * len(players_dict)
    _class_fitnesses = {k:[] for k,v in class_fitnesses.items()}
    for name,player in players_dict.items():
        fit = fitness(player)
        print(f"{name:27} {fit / possible_winnings:.2f}% {player['class']}")
        _class_fitnesses[player['type']].append(fit)
        # if not player['class'].evolves:
            # continue
        if fit < lowest_fitness:
            lowest_fitness = fit
            deleteme = name
        if fit > highest_fitness:
            highest_fitness = fit
            best_player = name

    for k,v in _class_fitnesses.items():
        class_fitnesses[k].append(int(sum(v)/len(v)))
    print('\n')
    if best_player:
        print(f" == breed  {best_player:27} ({players_dict[best_player]['class']})")
        new_player = clone(players_dict[best_player]['class'])
        new_name = random_name()
        if new_name in players_dict:
            new_name += ", PhD"
        print(f' == new player: {new_name:22} ({new_player})')
        players_dict[new_name] = { 'class':new_player, 'type':players_dict[best_player]['type'], 'results':[] }
    if deleteme:
        print(f" == delete {deleteme:27} ({players_dict[deleteme]['class']})")
        del players_dict[deleteme]
    # inp = input('(hit enter to start new round)')

for k,v in class_fitnesses.items():
    print(f"{k:25} {np.median(v):7} {v}")
