from .exceptions import InvalidInputError, IllegalMoveError
import re


def parse_player_input(inp):
    inp = inp.strip()
    rx_action = r"^(trade|buy|sell|camels)"
    match = re.search(rx_action, inp)
    generic_error = InvalidInputError(f"Input not recognised: {inp}")
    if not match:
        raise generic_error

    action = match.group()

    if action == "trade":
        # capture card groups involved in trade
        rx_trade = r"^trade\s+(.*)\s+for\s+(.*)"
        match = re.search(rx_trade, inp)
        if not match:
            raise generic_error
        card_lists = []
        for card_group in match.groups():
            # parse player cards group
            cards = parse_card_group(card_group)
            # transform into a list of strings
            out = []
            for card, amount in cards.items():
                amount = 1 if amount is None else amount
                out.extend([card] * amount)
            card_lists.append(out)
        return [action, *card_lists]

    elif action == "buy":
        rx_buy = r"^buy\s+(.*)"
        match = re.search(rx_buy, inp)
        if not match:
            raise generic_error
        (card_group,) = match.groups()
        cards = parse_card_group(card_group)
        bad = " ".join(
            f"{1 if amount is None else amount} {card}" for card, amount in cards.items()
        )
        error = IllegalMoveError(
            "You can't buy more than one card type. " f"(You are trying to buy {bad})"
        )
        if len(cards) > 1:
            raise error
        ((card, amount),) = cards.items()
        if amount not in (None, 1):
            raise error
        return action, card

    elif action == "sell":
        # grab the group of cards to sell from the input string
        rx_sell = r"^sell\s+(.*)"
        match = re.search(rx_sell, inp)
        if not match:
            raise generic_error
        (card_group,) = match.groups()
        # grab the amount and card type
        cards = parse_card_group(card_group)
        if len(cards) > 1:
            bad_sale = [thing for thing in cards.keys()]
            raise IllegalMoveError(
                "You can't sell more than one card type. " f"(You are trying to sell {bad_sale})"
            )
        ((card, amount),) = cards.items()
        # if no sale amount specified, set to default: "all"
        if amount is None:
            amount = "all"
        return action, card, amount

    elif action == "camels":
        return ("camels",)

    else:
        raise InvalidInputError(f"Unrecognised action: {inp}")


def parse_card_group(string_of_cards):
    inp = string_of_cards.strip()
    rx = (
        r"\b"  # boundary between word and non-word characters
        r"((\d)+\s+)?"  # optional digit(s) and whitespace(s) (capture)
        r"(\w+)"  # word (capture)
        r"\b"  # boundary between word and non-word characters
    )
    results = re.findall(rx, inp)
    d = dict()
    for __, amount, card in results:
        # convert empty strings to None; numeric strings to int
        amount = int(amount) if amount else None
        if card in d:
            # add amount to d[card], handling the case where either d[card] or
            # amount is None
            d[card] = (1 if d[card] is None else d[card]) + (1 if amount is None else amount)
        else:
            d[card] = amount
    return d
