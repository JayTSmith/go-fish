"""
The executable test script for fish_lib.

Author: Justin Smith
Date: 1/23/18
"""
import sys

from fish_lib.game import BasicGoFish
from fish_lib.players import TryingPlayer


def build_players():
    return [TryingPlayer(name=f'{i+1}') for i in range(6)]


def stat_run():
    win_count = {}
    for i in range(10000):
        g = BasicGoFish(build_players())
        g.do_full_round()
        for win in g.winner:
            win_count[type(win)] = win_count.get(type(win), 0) + 1

    for k in win_count:
        print(k, win_count[k])


def main():
    """
    Executed when the script is ran as an executable script.
    :return: The fish_lib.BaseGame object created for testing.
    """
    line_sep_char = '#'
    
    fish = BasicGoFish(build_players())

    print(('{0:%s^30}' % line_sep_char).format('Players'))
    for i in fish.players:
        print(line_sep_char, 'Player {}: {}'.format(i.name, type(i)))
    
    fish.do_full_round()

    win_string = '{1} Winners: {0}'.format(', '.join(['Player ' + p.name for p in fish.winner]),
                                           line_sep_char)
    sep = line_sep_char * len(win_string)
    print('\n{0}\n{1}\n{0}'.format(sep, win_string))
    return fish


def prof_main():
    from cProfile import Profile

    prof = Profile()
    prof.enable()
    fish = BasicGoFish(build_players())
    prof.disable()

    line_sep_char = '#'

    win_string = '{1} Winners: {0}'.format(', '.join(['Player ' + p.name for p in fish.winner]),
                                           line_sep_char)
    sep = line_sep_char * len(win_string)
    print('\n{0}\n{1}\n{0}'.format(sep, win_string))

    prof.print_stats()
    return fish


if __name__ == '__main__':
    # Used if the script is used in an interactive environment
    if '-p' in sys.argv:
        prof_main()
    else:
        main()
