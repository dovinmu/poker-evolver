from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate

import random
from pandas import DataFrame, read_csv

ranked_hands = read_csv("all_169_hands_ranked.tsv", sep='\t', index_col=1)

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

class RandoPlayer(BasePokerPlayer):
    def __init__(self):
        super().__init__()
        self.evolves = False

    def declare_action(self, valid_actions, hole_card, round_state):
        # valid_actions format => [raise_action_info, call_action_info, fold_action_info]
        action_info = random.choice(valid_actions)
        action, amount = action_info["action"], action_info["amount"]
        if action == 'raise':
            if amount['min'] == amount['max']:
                amount = amount['min']
            else:
                amount = random.randint(amount['min'], amount['max'])

        return action, amount

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "Rando"

class CowardPlayer(RandoPlayer):
    def declare_action(self, valid_actions, hole_card, round_state):
        return "fold", 0

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "Coward"

class FishPlayer(RandoPlayer):  # Do not forget to make parent class as "BasePokerPlayer"
    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):
        call_action_info = valid_actions[1]
        action, amount = call_action_info["action"], call_action_info["amount"]
        # print(self.name, "(fish)", action, amount)
        return action, amount   # action returned here is sent to the poker engine

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "Fish"

class HotheadPlayer(RandoPlayer):
    # always raises
    def declare_action(self, valid_actions, hole_card, round_state):
        raise_action_info = valid_actions[2]
        action, amount = raise_action_info["action"], raise_action_info["amount"]["min"]
        return action, amount

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "Hothead"

class RankedHandPlayer(RandoPlayer):
    # Only considers the rank of its hand in making decisions.
    def __init__(self):
        super().__init__()
        self.raise_rank = 0
        self.check_rank = 100

    def declare_action(self, valid_actions, hole_card, round_state):
        # valid_actions format => [fold_action_info, call_action_info, raise_action_info]
        hand_rank = rank(hole_card)
        if hand_rank < self.raise_rank:
            raise_action_info = valid_actions[2]
            action, amount = raise_action_info["action"], raise_action_info["amount"]['min'] * 2
            return action, amount
        elif hand_rank < self.check_rank or valid_actions[1]['amount'] == 0:
            call_action_info = valid_actions[1]
            action, amount = call_action_info["action"], call_action_info["amount"]
            return action, amount
        else:
            return "fold", 0

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "RankedHand"

class EvolvingRankedHandPlayer(RankedHandPlayer):
    def __init__(self, raise_rank=None, check_rank=None):
        super().__init__()
        self.evolves = True
        if raise_rank:
            self.raise_rank = max(min(raise_rank, 169), 0)
        else:
            self.raise_rank = random.randint(3, 50)
        if check_rank:
            self.check_rank = max(min(check_rank, 169), raise_rank)
        else:
            self.check_rank = random.randint(min(self.raise_rank + 1, 168), 169)

    def breed(self, other=None):
        raise_range = 20
        check_range = 50

        if not other:
            other = EvolvingRankedHandPlayer(self.raise_rank, self.check_rank)
        if self.raise_rank > other.raise_rank:
            raise_rank = random.randint(other.raise_rank - raise_range, self.raise_rank + raise_range + 1)
        else:
            raise_rank = random.randint(self.raise_rank - raise_range, other.raise_rank + raise_range + 1)

        if self.check_rank > other.check_rank:
            check_rank = random.randint(other.check_rank - check_range, self.check_rank + check_range + 1)
        else:
            check_rank = random.randint(self.check_rank - check_range, other.check_rank + check_range + 1)

        return EvolvingRankedHandPlayer(raise_rank, check_rank)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"EvolvingRankedHand r:{self.raise_rank} c:{self.check_rank}"

class EvolvingRankAndTablePlayer(EvolvingRankedHandPlayer):
    def __init__(self, raise_pwin=None, check_pwin=None, raise_rank=None, check_rank=None):
        super().__init__(raise_rank, check_rank)
        self.evolves = True
        if raise_pwin:
            self.raise_pwin = max(min(raise_pwin, 1), 0)
        else:
            self.raise_pwin = random.random()

        if check_pwin:
            self.check_pwin = max(min(check_pwin, self.raise_pwin), 0)
        else:
            self.check_pwin = self.rand_in_range(0, self.raise_pwin)
        # print("new", self)

    def rand_in_range(self, a, b):
        return a + (b - a) * random.random()

    def breed(self, other=None):
        raise_pwin_range = 0
        check_pwin_range = 0

        if not other:
            other = EvolvingRankAndTablePlayer(self.raise_pwin, self.check_pwin, self.raise_rank, self.check_rank)
        parent = super().breed(other)
        if self.raise_rank > other.raise_rank:
            raise_pwin = self.rand_in_range(other.raise_pwin - raise_pwin_range, self.raise_pwin + raise_pwin_range)
        else:
            raise_pwin = self.rand_in_range(self.raise_pwin - raise_pwin_range, other.raise_pwin + raise_pwin_range)

        if self.check_pwin > other.check_pwin:
            check_pwin = self.rand_in_range(other.check_pwin - check_pwin_range, self.check_pwin + check_pwin_range)
        else:
            check_pwin = self.rand_in_range(self.check_pwin - check_pwin_range, other.check_pwin + check_pwin_range)

        return EvolvingRankAndTablePlayer(raise_pwin, check_pwin, parent.raise_rank, parent.check_rank)

    # Considers the rank of its hand, position, and stack sizes.
    def declare_action(self, valid_actions, hole_card, round_state):
        # valid_actions format => [fold_action_info, call_action_info, raise_action_info]
        # print(hole_card)
        if round_state['street'] == 'preflop':
            return super().declare_action(valid_actions, hole_card, round_state)
        # print(round_state)
        p_win = estimate_hole_card_win_rate(nb_simulation=10, nb_player=len(round_state['seats']), hole_card=gen_cards(hole_card), community_card=gen_cards(round_state['community_card']))
        # print('prob win', int(p_win*100), '%')
        if p_win > self.raise_pwin and random.random()*2 < (len(round_state['seats']) * p_win):
            raise_action_info = valid_actions[2]
            action, amount = raise_action_info["action"], raise_action_info["amount"]['min'] * 2
            return action, amount
        elif p_win > self.check_pwin or valid_actions[1]['amount'] == 0:
            call_action_info = valid_actions[1]
            action, amount = call_action_info["action"], call_action_info["amount"]
            return action, amount
        else:
            return "fold", 0

    def __str__(self):
        return f"EvolvingRankAndTablePlayer (r:{self.raise_pwin:.2f} c:{self.check_pwin:.2f}) (preflop r:{self.raise_rank} c:{self.check_rank:3})"
