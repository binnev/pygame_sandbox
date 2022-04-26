import unittest
from classes import Token, Deck
from utilities import parse_player_input, parse_card_group
from exceptions import InvalidInputError, IllegalMoveError

class TestToken(unittest.TestCase):

    def test_intended_use(self):
        # test standard instantiation
        token = Token("gold", 6)
        self.assertEqual(token.name, "gold")
        self.assertEqual(token.value, 6)

    def test_for_illegal_names(self):
        # test for goods that don't exist
        with self.assertRaises(ValueError):
            Token("pineapple", 1)

    def test_for_illegal_values(self):
        # test for zero or negative values
        with self.assertRaises(ValueError):
            Token("leather", -3)
        # test for non integer values
        with self.assertRaises(ValueError):
            Token("cloth", 4.7)
        with self.assertRaises(ValueError):
            Token("spice", 2.0)

class TestDeck(unittest.TestCase):

    def setUp(self):
        self.deck = Deck(default=True)
        self.initial_deck_len = len(self.deck)

    def tearDown(self):
        del self.deck
        del self.initial_deck_len

    def test_draw_default(self):
        drawn_cards = self.deck.draw()
        self.assertEqual(len(drawn_cards), 1)
        self.assertEqual(len(self.deck), self.initial_deck_len-1)

    def test_draw_multiple(self):
        drawn_cards = self.deck.draw(3)
        self.assertEqual(len(drawn_cards), 3)
        self.assertEqual(len(self.deck), self.initial_deck_len-3)

    def test_draw_too_many(self):
        # draw exactly the number of cards left in the deck
        self.deck = Deck(camel=5)
        drawn_cards = self.deck.draw(5)
        self.assertEqual(drawn_cards, ["camel"]*5)
        self.assertEqual(len(self.deck), 0)

        # drawing too many cards should just return available cards
        self.deck = Deck(camel=5)
        drawn_cards = self.deck.draw(10)
        self.assertEqual(drawn_cards, ["camel"]*5)
        self.assertEqual(len(self.deck), 0)

        # draw from an empty deck should return empty list
        self.deck = Deck()
        drawn_cards = self.deck.draw()
        self.assertEqual(drawn_cards, [])
        self.assertEqual(len(self.deck), 0)

        self.deck = Deck()
        drawn_cards = self.deck.draw(10)
        self.assertEqual(drawn_cards, [])
        self.assertEqual(len(self.deck), 0)

    def test_take(self):
        drawn_cards = self.deck.take("camel")
        self.assertEqual(len(drawn_cards), 1)
        self.assertEqual(drawn_cards, ["camel"])

    def test_take_too_many(self):
        with self.assertRaises(ValueError):
            self.deck.take("camel", 100)

    def test_take_when_card_not_present(self):
        # try to draw a card that isn't in the deck
        with self.assertRaises(ValueError):
             self.deck.take("magic carpet")

    def test_take_multiple(self):
        drawn_cards = self.deck.take("silver", 5)
        # check correct number and type of drawn cards
        self.assertEqual(len(drawn_cards), 5)
        self.assertEqual(drawn_cards, ["silver"]*5)
        # check deck reduced in size correctly
        self.assertEqual(len(self.deck), self.initial_deck_len-5)

    def test_shuffle(self):
        unshuffled_deck = self.deck.copy()
        self.deck.shuffle()
        shuffled_deck = self.deck.copy()
        self.assertNotEqual(unshuffled_deck, shuffled_deck)

    def test_peek(self):
        # check correct number of cards seen
        seen_cards = self.deck.peek()
        self.assertEqual(len(seen_cards), 1)
        seen_cards = self.deck.peek(4)
        self.assertEqual(len(seen_cards), 4)

        # check that the peeking didn't change the number of cards in the deck
        self.assertEqual(len(self.deck), self.initial_deck_len)


class Test_parse_player_input(unittest.TestCase):

    def test_action(self):
        inp = "trade camel camel leather for diamond gold"
        action, *details = parse_player_input(inp)
        self.assertEqual(action, "trade")

        inp = "sell diamond"
        action, *details = parse_player_input(inp)
        self.assertEqual(action, "sell")

        inp = "camels"
        action, *details = parse_player_input(inp)
        self.assertEqual(action, "camels")

        inp = "buy cloth"
        action, *details = parse_player_input(inp)
        self.assertEqual(action, "buy")

    def test_invalid_action_names(self):
        with self.assertRaises(InvalidInputError):
            inp = "tradeeeeeee camel camel leather for diamond gold"
            action, *details = parse_player_input(inp)

        with self.assertRaises(InvalidInputError):
            inp = "trad ecamel camel leather for diamond gold"
            action, *details = parse_player_input(inp)

        with self.assertRaises(InvalidInputError):
            inp = "flog carpets"
            action, *details = parse_player_input(inp)

        with self.assertRaises(InvalidInputError):
            inp = "selllll stuff"
            action, *details = parse_player_input(inp)

        with self.assertRaises(InvalidInputError):
            inp = "buyyyyyyy camels"
            action, *details = parse_player_input(inp)

    def test_camels(self):
        # intended usage
        inp = "camels"
        action, *details = parse_player_input(inp)
        self.assertEqual(action, "camels")

        # trailing whitespace
        inp = "camels        "
        action, *details = parse_player_input(inp)
        self.assertEqual(action, "camels")

        # redundant input after camels
        inp = "camels and stuff"
        action, *details = parse_player_input(inp)
        self.assertEqual(action, "camels")

        # leading whitespace
        inp = "        camels"
        action, *details = parse_player_input(inp)
        self.assertEqual(action, "camels")

    def test_sell(self):
        # general case -- sell all of a resource
        inp = "sell gold"
        action, goods, amount = parse_player_input(inp)
        self.assertEqual(action, "sell")
        self.assertEqual(goods, "gold")
        self.assertEqual(amount, "all")

        # general case with weird whitespace
        inp = "       sell      gold      "
        action, goods, amount = parse_player_input(inp)
        self.assertEqual(action, "sell")
        self.assertEqual(goods, "gold")
        self.assertEqual(amount, "all")

        # sell a specific number
        inp = "sell 2 gold"
        action, goods, amount = parse_player_input(inp)
        self.assertEqual(action, "sell")
        self.assertEqual(goods, "gold")
        self.assertEqual(amount, 2)

        # sell zero (not legal, but this function should parse it)
        inp = "sell 0 gold"
        action, goods, amount = parse_player_input(inp)
        self.assertEqual(action, "sell")
        self.assertEqual(goods, "gold")
        self.assertEqual(amount, 0)

        # sell a specific number with weird whitespace
        inp = "      sell     2    gold    "
        action, goods, amount = parse_player_input(inp)
        self.assertEqual(action, "sell")
        self.assertEqual(goods, "gold")
        self.assertEqual(amount, 2)

        # trying to sell multiple card types: should raise exception
        with self.assertRaises(IllegalMoveError):
            inp = "sell 2 gold 4 silver"
            action, goods, amount = parse_player_input(inp)
        with self.assertRaises(IllegalMoveError):
            inp = "sell gold silver"
            action, goods, amount = parse_player_input(inp)
        with self.assertRaises(IllegalMoveError):
            inp = "sell gold 3 silver"
            action, goods, amount = parse_player_input(inp)

        # wrong order: should treat number as second card group and raise
        # exception
        with self.assertRaises(IllegalMoveError):
            inp = "sell gold 3"
            action, goods, amount = parse_player_input(inp)

    def test_buy(self):
        # intended usage
        inp = "buy gold"
        action, card = parse_player_input(inp)
        self.assertEqual(card, "gold")

        # buying camels is illegal, but this function should parse it
        inp = "buy camel"
        action, card = parse_player_input(inp)
        self.assertEqual(card, "camel")

        # trying to buy more than one card should raise error
        with self.assertRaises(IllegalMoveError):
            inp = "buy gold silver"
            action, card = parse_player_input(inp)

        # trying to buy more than one of a single card should raise error
        with self.assertRaises(IllegalMoveError):
            inp = "buy 2 camel"
            action, card = parse_player_input(inp)

    def test_trade(self):
        # no numbers
        inp = "trade camel camel leather for diamond gold"
        action, player_cards, market_cards = parse_player_input(inp)
        self.assertEqual(player_cards, ["camel", "camel", "leather"])
        self.assertEqual(market_cards, ["diamond", "gold"])

        # with numbers
        inp = "trade 2 camel 1 leather for 1 diamond 1 gold"
        action, player_cards, market_cards  = parse_player_input(inp)
        self.assertEqual(player_cards, ["camel", "camel", "leather"])
        self.assertEqual(market_cards, ["diamond", "gold"])

        # mixture of numbered and non-numbered goods
        inp = "trade camel camel 1 leather for 1 diamond gold"
        action, player_cards, market_cards  = parse_player_input(inp)
        self.assertEqual(player_cards, ["camel", "camel", "leather"])
        self.assertEqual(market_cards, ["diamond", "gold"])

        inp = "trade camel 2 camel for 1 diamond gold"
        action, player_cards, market_cards  = parse_player_input(inp)
        self.assertEqual(player_cards, ["camel", "camel", "camel"])
        self.assertEqual(market_cards, ["diamond", "gold"])

        # trading zero goods: not legal but this function should parse it.
        # the caller can check the amounts add up for the trade.
        inp = "trade camel camel 0 leather for 1 diamond gold"
        action, player_cards, market_cards  = parse_player_input(inp)
        self.assertEqual(player_cards, ["camel", "camel"])
        self.assertEqual(market_cards, ["diamond", "gold"])

        inp = "trade camel camel 0 camel 0 leather for 1 diamond gold"
        action, player_cards, market_cards  = parse_player_input(inp)
        self.assertEqual(player_cards, ["camel", "camel"])
        self.assertEqual(market_cards, ["diamond", "gold"])


class Test_parse_card_group(unittest.TestCase):
    def test_repeated_cards(self):
        inp = "camel camel leather leather leather"
        cards = parse_card_group(inp)
        self.assertEqual(cards, {"camel": 2, "leather": 3})

    def test_single_cards(self):
        inp = "   camel   "
        cards = parse_card_group(inp)
        self.assertEqual(cards, {"camel": None})

        inp = "camel leather gold"
        cards = parse_card_group(inp)
        self.assertEqual(cards, {"camel": None, "leather": None, "gold": None})

        inp = "    camel    leather     gold    "
        cards = parse_card_group(inp)
        self.assertEqual(cards, {"camel": None, "leather": None, "gold": None})

    def test_specified_amounts(self):
        inp = "3 camel 2 leather"
        cards = parse_card_group(inp)
        self.assertEqual(cards, {"camel": 3, "leather": 2})

        # not a legal move, but this function should still parse it
        inp = "3 camel 0 leather"
        cards = parse_card_group(inp)
        self.assertEqual(cards, {"camel": 3, "leather": 0})

    def test_repeated_cards_and_specified_amounts(self):
        inp = "camel 2 camel 2 leather leather"
        cards = parse_card_group(inp)
        self.assertEqual(cards, {"camel": 3, "leather": 3})

        inp = "camel 1 camel 1 leather leather"
        cards = parse_card_group(inp)
        self.assertEqual(cards, {"camel": 2, "leather": 2})

        inp = "camel camel 3 leather"
        cards = parse_card_group(inp)
        self.assertEqual(cards, {"camel": 2, "leather": 3})

    def test_repeated_cards_and_single_cards(self):
        inp = "camel camel leather"
        cards = parse_card_group(inp)
        self.assertEqual(cards, {"camel": 2, "leather": None})

    def test_single_cards_and_specified_amounts(self):
        # the difference between None and 1 is important for other functions
        inp = "camel 1 leather"
        cards = parse_card_group(inp)
        self.assertEqual(cards, {"camel": None, "leather": 1})


if __name__ == "__main__":
    unittest.main()