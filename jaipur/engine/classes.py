from dataclasses import dataclass
from random import shuffle

from jaipur.constants import (
    TokenNames,
    DIAMOND,
    GOLD,
    SILVER,
    CLOTH,
    SPICE,
    LEATHER,
    CAMEL,
    COMBO3,
    COMBO4,
    COMBO5,
)
from jaipur.exceptions import InvalidInputError, IllegalMoveError
from jaipur.utils import parse_player_input


@dataclass
class Token:
    """
    Represents the round goods tokens which give players points. Each token
    should have
    - a value (on the back)
    - the name (on the front) e.g. "diamond" or "triple combo"
    """

    name: TokenNames
    value: int

    def __repr__(self):
        return str(self.value)


class Deck(list):
    def add(self, **kwargs):
        for goods, amount in kwargs.items():
            self.extend([goods] * amount)

    def shuffle(self):
        shuffle(self)

    def draw(self, number=1):
        """Draw the next card(s)"""
        drawn_cards = []
        try:
            for __ in range(number):
                drawn_cards.append(self.pop())
        except IndexError:
            pass
        finally:
            return drawn_cards

    def take(self, card, number=1):
        """Take a card by name"""
        return [self.pop(self.index(card)) for __ in range(number)]

    def peek(self, depth=1):
        """Look at the next card(s)"""
        return self[-depth:]

    def default_setup(self):
        contents = {
            DIAMOND: 6,
            GOLD: 6,
            SILVER: 6,
            CLOTH: 8,
            SPICE: 8,
            LEATHER: 10,
            CAMEL: 11,
        }
        self.add(**contents)

    @classmethod
    def setup_with(cls, **kwargs) -> "Deck":
        instance = cls()
        instance.add(**kwargs)
        return instance


class TokenStack(Deck):
    """
    Represents the stacks of tokens. Could be anything from the market goods
    to the Biggest Herd token to the combo tokens.
    Functionally very similar to the Deck class, but not limited to the card
    types
    """

    def __init__(self, *list_of_tokens):
        list.__init__(self, list(list_of_tokens))

    def sort_by_value(self, descending=True):
        """Sort the stack of tokens so that the highest value ones are on top.
        This means the highest value tokens should be the first to get popped
        off the list---meaning they should be at the end of the list.
        """
        self.sort(key=lambda x: x.value)

    def get_values(self):
        return [token.value for token in self]


class Marketplace(Deck):
    """
    Represents the 5 card river marketplace.
    Needs to keep track of empty spaces and/or preserve the order.
    """

    def __init__(self, list_of_5_cards):
        super().__init__()
        self.extend(list_of_5_cards)

    def swap(self, player_card, market_card):
        """Swap one player card for one market card. Illegal move. Intended for
        use as part of the trade() method."""
        # remove market card
        ind = self.index(market_card)
        (out,) = self.take(market_card)  # comma because only ever one card
        self.insert(ind, player_card)  # insert player card into same slot
        return out

    def trade(self, player_cards, market_cards):
        """Swap several player cards for several marketplace cards"""
        # start swapping
        out = []
        for player_card, market_card in zip(player_cards, market_cards):
            out.append(self.swap(player_card, market_card))
        return out

    def take_camels(self):
        return self.take("camel", self.count("camel"))

    def missing(self, cards):
        """Check if the marketplace is missing any of the cards in the list.
        If it is missing any of the cards, return the name of that card.
        If the marketplace has all the cards, return False.
        Used to check that trades will go through."""
        # convert single string to list of strings
        cards = [cards] if isinstance(cards, str) else cards
        counts = {card: cards.count(card) for card in cards}
        for card, amount in counts.items():
            if self.count(card) < amount:
                return card
        return False


class Player:
    def __init__(self, name):
        self.name = name
        self.hand = Deck()
        self.tokens = []
        self.victory_points = 0
        self.herd = Deck()

    def reset(self):
        self.hand = Deck()
        self.herd = Deck()
        self.tokens = []

    def missing(self, cards):
        """Check if the player is missing any of the cards in the list.
        If it is missing any of the cards, return the name of that card.
        If the player has all the cards, return False.
        Used to check that trades will go through"""
        # convert single string to list of strings
        cards = [cards] if isinstance(cards, str) else cards
        counts = {card: cards.count(card) for card in cards}
        for card, amount in counts.items():
            if self.count(card) < amount:
                return card
        return False

    def count(self, card):
        """Count how many the player has of a single resource card. Checks
        player herd if card is "camel"; checks hand otherwise."""
        return (self.herd if card == "camel" else self.hand).count(card)

    def take(self, cards):
        """Take cards from the player's hand or herd, depending on the card
        type. Return those cards as a list of strings.
        The input can be a single card (string) or a list of strings."""
        if isinstance(cards, str):
            location = self.herd if cards == "camel" else self.hand
            return location.take(cards)
        else:
            return [self.take(card).pop() for card in cards]

    def give(self, cards):
        """Give cards to the player. Depending on the card type, these will be
        stored in the player's hand or herd. Input can be single card (string)
        or a list of strings."""
        if isinstance(cards, str):
            location = self.herd if cards == "camel" else self.hand
            location.append(cards)
        else:
            for card in cards:
                self.give(card)

    @property
    def points(self):
        return sum(token.value for token in self.tokens)


class Game:
    def __init__(self):
        """Setup actions at the very beginning of the game"""
        # create players
        self.player1 = Player(name="Player 1")
        self.player2 = Player(name="Player 2")
        self.players = self.player1, self.player2
        self.current_player = 0

    def setup_round(self):
        """Setup actions at the start of each round"""
        # create token piles
        # populate tokens dictionary
        self.resource_tokens = {
            DIAMOND: [5, 5, 5, 7, 7],
            GOLD: [5, 5, 5, 6, 6],
            SILVER: [5, 5, 5, 5, 5],
            LEATHER: [1, 1, 1, 1, 1, 1, 2, 3, 4],
            CLOTH: [1, 1, 2, 2, 3, 3, 5],
            SPICE: [1, 1, 2, 2, 3, 3, 5],
        }
        self.bonus_tokens = {
            COMBO3: [1, 1, 2, 2, 2, 3, 3],
            COMBO4: [4, 4, 5, 5, 6, 6],
            COMBO5: [8, 8, 9, 10, 10],
        }

        # convert values to TokenStacks
        for key, values in self.resource_tokens.items():
            self.resource_tokens[key] = TokenStack(*(Token(key, v) for v in values))
            self.resource_tokens[key].sort_by_value()
        for key, values in self.bonus_tokens.items():
            self.bonus_tokens[key] = TokenStack(*(Token(key, v) for v in values))
            self.bonus_tokens[key].shuffle()

        # create deck
        self.deck = Deck()
        self.deck.default_setup()
        self.deck.shuffle()

        # create marketplace/river (always start with 3 camels)
        camels = self.deck.take("camel", 3)
        rest = self.deck.draw(2)
        self.marketplace = Marketplace(camels + rest)

        # setup players
        for player in self.players:
            player.reset()
            player.give(self.deck.draw(4))  # deal player hands

    def check_for_game_over(self):
        # has the market run out of cards?
        if len(self.deck) == 0:
            return True
        # are three or more resource tokens depleted?
        stack_lengths = [len(stack) for stack in self.resource_tokens.values()]
        if stack_lengths.count(0) >= 3:
            return True
        return False

    def prompt_player_turn(self, player):
        message = (
            f"{player.name}, it is your turn. \n"
            "Do one of the following:\n"
            "\t1) 'buy diamond' --> take 1 diamond from the market\n"
            "\t2) 'trade leather camel for diamond gold' --> trade your leather & camel for gold & diamond\n"
            "\t    or 'trade 3 camel for 3 leather'\n"
            "\t3) 'sell cloth' --> sell all your cloth. You can specify a number to sell: 'sell 2 cloth'\n"
            "\t4) 'camels' --> take all the camels\n"
        )
        return input(message).strip()

    def refill_marketplace(self):
        while len(self.marketplace) < 5:
            self.marketplace.extend(self.deck.draw())
            if len(self.deck) == 0:
                break

    def buy(self, player, card):
        # player hand size can't exceed 7
        if len(player.hand) >= 7:
            raise IllegalMoveError("You already have 7 cards in your hand. " "You can't buy.")
        # you can't buy a camel
        if card == "camel":
            raise IllegalMoveError("You can't buy a camel. Use the 'camels' action " "instead.")
        # can't buy stuff that's not in the marketplace
        if self.marketplace.missing(card):
            raise IllegalMoveError(f"There is no {card} in the marketplace.")

        # take card from marketplace into player hand
        player.hand.extend(self.marketplace.take(card))
        self.refill_marketplace()

    def sell(self, player, goods, amount):
        if amount == "all":
            amount = player.count(goods)
        if goods == "camel":
            raise IllegalMoveError("You can't sell camels")
        if player.missing(goods):
            raise IllegalMoveError(f"You don't have any {goods} to sell.")
        if amount == 0:
            raise IllegalMoveError("You can't sell zero goods")
        if amount > player.count(goods):
            raise IllegalMoveError(f"You don't have {amount} {goods} to sell.")
        if goods in ("diamond", "gold", "silver") and amount < 2:
            raise IllegalMoveError(f"You can't sell less than 2 {goods}")

        # remove the cards from the player's hand
        player.hand.take(goods, amount)
        # take tokens from the token pile and add to player tokens
        player.tokens.extend(self.resource_tokens[goods].draw(amount))

        # handle combo tokens for large trades
        if amount == 3:
            player.tokens.extend(self.bonus_tokens["combo3"].draw())
        if amount == 4:
            player.tokens.extend(self.bonus_tokens["combo4"].draw())
        if amount >= 5:
            player.tokens.extend(self.bonus_tokens["combo5"].draw())

    def trade(self, player, player_cards, market_cards):
        # check card lists are equal length
        if len(player_cards) != len(market_cards):
            raise IllegalMoveError(
                "The number of player cards doesn't match " "the number of market cards for trade."
            )
        # don't allow single-card trades
        if len(player_cards) == 1:
            raise IllegalMoveError("You can't trade less than 2 cards.")
        # don't allow trading for marketplace camels
        if "camel" in market_cards:
            raise IllegalMoveError("You can't trade for camels in the market")
        # check the player has all the cards they want to trade in
        card = player.missing(player_cards)
        if card:
            raise IllegalMoveError(f"You don't have enough {card} to make this" " trade.")
        # check if the requested market_cards are all there
        card = self.marketplace.missing(market_cards)
        if card:
            raise IllegalMoveError(
                f"There are not enough {card} cards in the " "marketplace for this trade"
            )
        # check hand size
        non_camel_cards = [c for c in player_cards if c != "camel"]
        if len(player.hand) - len(non_camel_cards) + len(market_cards) > 7:
            raise IllegalMoveError("Your hand will be greater than 7 cards " "after this trade")

        # take the cards out of the player's hand (or herd, if camel)
        player.take(player_cards)
        # do the market trade
        self.marketplace.trade(player_cards, market_cards)
        # give market cards to player
        player.give(market_cards)

    def take_camels(self, player):
        if self.marketplace.count("camel") == 0:
            raise IllegalMoveError("There are no camels in the marketplace. " "Try another action.")
        player.give(self.marketplace.take_camels())
        self.refill_marketplace()

    def player_turn(self):
        # get current player
        player = self.players[self.current_player % 2]

        # prompt player for action
        inp = self.prompt_player_turn(player)
        action, *details = parse_player_input(inp)

        # make arrangements for the player's request
        if action == "buy":
            (goods,) = details
            self.buy(player, goods)
        elif action == "trade":
            player_cards, market_cards = details
            self.trade(player, player_cards, market_cards)
        elif action == "sell":
            goods, amount = details
            self.sell(player, goods, amount)
        elif action == "camels":
            self.take_camels(player)
        else:
            raise InvalidInputError(f"Unrecognised input: {inp}")

        # execute player requests
        return True  # turn satisfactorily resolved

    def play_round(self):
        self.setup_round()
        while self.check_for_game_over() is not True:
            response = ""
            while response is not True:
                print(self)  # print the board
                if response:
                    print(">" * 90 + "\n" + response + "\n" + ">" * 90)
                try:
                    response = self.player_turn()  # play out player turn
                except (IllegalMoveError, InvalidInputError) as e:
                    response = str(e)
            self.current_player += 1  # increment current player

        print("END OF THE ROUND!")
        # after round has finished,
        # award the largest herd token
        player1_herd_size = len(self.player1.herd)
        player2_herd_size = len(self.player2.herd)
        if player1_herd_size > player2_herd_size:
            print("Player 1 has the largest herd and gets 5 points")
            self.player1.tokens.append(Token("largest_herd", 5))
        else:
            print("Player 2 has the largest herd and gets 5 points")
            self.player2.tokens.append(Token("largest_herd", 5))

        # count token points
        player1_points = self.player1.points
        player2_points = self.player2.points
        print(f"{self.player1.name} has {player1_points} points")
        print(f"{self.player2.name} has {player2_points} points")

        # award victory points
        if player1_points > player2_points:
            self.player1.victory_points += 1
            print(f"{self.player1.name} wins this round.")
        elif player1_points < player2_points:
            self.player2.victory_points += 1
            print(f"{self.player2.name} wins this round.")
        else:
            self.player1.victory_points += 1
            self.player2.victory_points += 1
            print(f"It's a draw! Both players get a victory point.")

    def play_game(self):
        print("ROUND 1!")
        self.play_round()
        print("ROUND 2!")
        self.play_round()
        for player in self.players:
            if player.victory_points == 2:
                print(f"THE WINNER IS {player.name.upper()}!")
                return None
        print("ROUND 3!")
        self.play_round()
        for player in self.players:
            if player.victory_points == 2:
                print(f"THE WINNER IS {player.name.upper()}!")
                return None

    def __repr__(self):
        diamond = "{:<10}".format("diamond:") + "{:<20}".format(
            str(self.resource_tokens["diamond"])
        )
        gold = "{:<10}".format("gold:") + "{:<20}".format(str(self.resource_tokens["gold"]))
        silver = "{:<10}".format("silver:") + "{:<20}".format(str(self.resource_tokens["silver"]))
        spice = "{:<10}".format("spice:") + "{:<20}".format(str(self.resource_tokens["spice"]))
        cloth = "{:<10}".format("cloth:") + "{:<20}".format(str(self.resource_tokens["cloth"]))
        leather = "{:<10}".format("leather:") + "{:<20}".format(
            str(self.resource_tokens["leather"])
        )

        player1_vp = (
            f"({self.player1.victory_points} victory points)" if self.player1.victory_points else ""
        )
        player2_vp = (
            f"({self.player2.victory_points} victory points)" if self.player2.victory_points else ""
        )

        strings = [
            "=" * 90,
            f"{self.player1.name} {player1_vp}",
            f"\thand: {sorted(self.player1.hand)}",
            f"\ttokens: {self.player1.tokens}",
            f"\therd: {'*'*len(self.player1.herd)}",
            f"MARKETPLACE: {self.marketplace}",
            f"DECK: {'*'*len(self.deck)}",
            "TOKENS:",
            "\t" + diamond,
            "\t" + gold,
            "\t" + silver,
            "\t" + spice,
            "\t" + cloth,
            "\t" + leather,
            f"{self.player2.name} {player2_vp}",
            f"\thand: {sorted(self.player2.hand)}",
            f"\ttokens: {self.player2.tokens}",
            f"\therd: {'*'*len(self.player2.herd)}",
        ]
        return "\n".join(strings)


""" TODO:
    - fix which player starts on alternating rounds. Loser of the last round
      to start.
    - don't allow "trade leather cloth for diamond cloth". That's a 1-trade.
    - If it's a draw on points, go by who has the most bonus tokens. If that's
      a draw too, go by who has the most goods cards.
"""
