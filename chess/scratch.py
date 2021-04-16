# FEN
fen_string = "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR"


def print_fen(string):
    ranks = string.split("/")
    for rank in ranks:
        for char in rank:
            if char.isnumeric():
                rank = rank.replace(char, "." * int(char))

        print(rank)


print_fen(fen_string)
