"""
This sets the framework for a game of GoFish.

Author: Justin Smith
Date: 1/23/18
"""
import itertools
from random import randint, shuffle

RANKS = ('2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace')
SUITS = ('Spades', 'Clubs', 'Hearts', 'Diamond')

BASE_DECK = tuple(itertools.product(RANKS, SUITS))


class BaseGame(object):
    """
    Serves as a sort of abstract class for Go Fish games.
    """

    def do_turn(self):
        """
        Runs through a single turn of Go Fish according to how it's implemented.
        Raises NotImplementedError if called.
        """
        raise NotImplementedError('This method should be replaced by subclasses.')

    def do_full_round(self):
        """
        Does a full game of Go Fish according to how it's implemented.
        Raises NotImplementedError if called.
        """
        raise NotImplementedError('This method should be replaced by subclasses.')


class BasicGoFish(BaseGame):
    """
    This is the class that runs the game of Go Fish.
    """

    def __init__(self, players: list):
        self.deck = list(BASE_DECK)

        self.active_player_idx = 0
        self.players = players

    @staticmethod
    def card_to_string(card):
        """
        Prints a card tuple in a human-readable string.
        :param card: The card tuple in format (RANK, SUIT).
        :return: A string in how a person would say it.
        """
        return '{} of {}'.format(card[0], card[1])

    @staticmethod
    def check_player_for_book(player):
        """
        Checks if a certain player has a book. If one is found,
        then it is removed from the player's hand and added to their book list.
        """
        rank_count = {}
        for card in player.hand:
            rank_count[card[0]] = rank_count.get(card[0], 0) + 1

        for book in filter(lambda r: rank_count[r] == 4, rank_count):
            for card in itertools.product((book,), SUITS):
                player.hand.remove(card)
            player.books.append(book)
            print('Player {} made a book of {}\'s.'.format(player.name, book))

    def check_all_players_for_books(self):
        """
        Checks every players' hand for a book (group of matching faces). If one is found,
        then it is removed from the player's hand and added to their book list.
        """
        for player in self.players:
            self.check_player_for_book(player)

    def do_turn(self):
        """
        Does the active player's turn and then rotates the index to the next player.
        """
        active_player = self.players[self.active_player_idx]

        if not active_player.hand:
            active_player.playing = self.draw_card(active_player)

        if not active_player.playing:
            print(f'Player {active_player.name} is out!')
            self.active_player_idx = (self.active_player_idx + 1) % len(self.players)
            return

        valid_players = [p for p in self.players if p.playing]

        # We pass the players in case the Player is keeping tracking of that.
        # requested face and requested player.
        r_face, r_player = active_player.ask_for_card(valid_players)

        print('Player {} asked for a {} from Player {}.'.format(active_player.name, r_face,
                                                                r_player.name))
        won_cards = r_player.confirm_ask(r_face)

        # Gotta inform the players who just asked for one.
        for player in valid_players:
            if player != active_player and player != r_player:
                player.hear_ask(active_player, r_face, r_player)
                player.hear_confirm(active_player, bool(won_cards), r_face, r_player)

        if won_cards:
            print('Player {} gained {} {}(s) with {} in hand.'.format(active_player.name,
                                                                      len(won_cards),
                                                                      r_face,
                                                                      active_player.count_copies(r_face)))
            active_player.hand.extend(won_cards)

            # To speed up the game, let's just mark if they can continue playing here.
            if not self.deck:
                if not r_player.hand:
                    r_player.playing = False
                    print(f'Player {r_player.name} is out!')
                if not active_player.hand:
                    active_player.playing = False
                    print(f'Player {active_player.name} is out!')
        else:  # If won cards is empty, then we 'go fish.'
            print('Player {} didn\'t have a {}.'.format(r_player.name, r_face))
            self.draw_card(active_player)

        # Check for books
        # We check here since the active player can draw into a book or start with one.
        self.check_player_for_book(active_player)

        # Increment active player index to the next valid player according to the list.
        # This list isn't always going to be right since we have to check books
        # right after but it's closer than the alternative.
        val_idx = (valid_players.index(active_player) + 1) % len(valid_players)
        self.active_player_idx = self.players.index(valid_players[val_idx])

    def do_full_round(self):
        """
        This method calls do_turn until done is True.

        This simulates an actual game of Go Fish. There is a iteration limit of 100000 in case of
        logic failure.

        :return: the winning player obj
        """
        iterations = 0
        self.setup_game()
        while not self.done and iterations < 100000:
            print('\nTurn {}\n{}'.format(iterations + 1,
                                         '-' * 15))
            self.do_turn()
            iterations += 1

    @property
    def done(self):
        """
        Returns true if none of the players are playing and if deck list is empty.
        """
        return not ([player for player in self.players if player.playing] or self.deck)

    def draw_card(self, player, draw_amount=1):
        """
        Draws a specified number of cards to a player's hand.
        :param player: The player who is drawing card(s).
        :param draw_amount: The number of cards to draw.
        :return: True if the player was able to draw. Otherwise, returns False.
        """
        if len(self.deck) >= draw_amount:
            i = 0
            while i < draw_amount:
                player.hand.append(self.deck.pop(0))
                print('Player {} drew a {}.'.format(player.name,
                                                    player.hand[-1][0]))
                i += 1
            return True
        return False

    def setup_game(self):
        shuffle(self.deck)
        self.active_player_idx = 0

        card_count = 5 if len(self.players) > 4 else 7
        for player in self.players:
            player.playing = True
            player.hand = self.deck[:card_count]
            self.deck = self.deck[card_count:]

    def shuffle_deck(self):
        """
        Quickly scrambles the order of the deck list.
        """
        for i in range(len(self.deck)):
            self.deck.insert(i, self.deck.pop(randint(0, len(self.deck) - 1)))

    @property
    def winner(self):
        """
        The winner(s) of the game.

        If the game is not done, this will return None. This can also return multiple players
        because of ties.

        :return: The player(s) objects that won.
        """
        if not self.done:
            return None

        best_score = max((len(play.books) for play in self.players))
        winners = []
        # Possible tie, so let's return everyone with the best score.
        for player in self.players:
            if len(player.books) == best_score:
                winners.append(player)

        return winners
