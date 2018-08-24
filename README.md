Plays a set of poker-playing bots against each other in arbitrarily many tournaments. After a set of tournaments, measures the fitness, deleting the least fit and "breeds" the most fit (with random noise added in to parameters).

As of 8/24/2018, the bots so far:

RandoPlayer: Always randomly chooses an action. It's... not a very good poker player, even by the standards of this sorry assortment of bots.
CowardPlayer: Always folds. Will consistently lose to Fish and Hothead.
FishPlayer: Always checks or calls. Surprisingly good against the other terrible bots.
HotheadPlayer: Always raises by the minimum amount. This bot seems to be the optimal strategy in a lot of games with the other terrible bots.
RankedHandPlayer: Always raises if the rank of its cards is above a certain value, or else checks if the rank is above another value. Does not consider cards on the table or the actions of other bots.
EvolvingRankedHandPlayer: Same as RankedHandPlayer, but it has the ability to breed new versions of itself with similar (but not identical) raise / check values.
EvolvingRankAndTablePlayer: Same as EvolvingRankedHandPlayer, but it also considers cards on the table. It will do a rudimentary calculation of the strength of its hand post-flop, and if the probability of it winning is above a certain constant then it will raise or check if above another constant.

The idea is that running even extremely rudimentary bots like this through lots of poker tournaments will bring us to some interesting conclusions and maybe find some nice Nash Equilibria. And it has, but not the ones I was expecting. It seems that one Nash Equilibrium is for a player to simply play all hands, never folding pre-flop. Given enough time, the evolving bots will eventually converge to become Fish, never folding but also never raising.
