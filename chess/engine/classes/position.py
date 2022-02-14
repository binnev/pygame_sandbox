class Position(str):
    """Static chess position represented as a string of FEN notation, with some helper methods to
    do static analysis"""

    def readable_str(self, V_SEP="\n", H_SEP=""):
        rows = self.split("/")
        new_rows = []

        for row in rows:
            new_row = []
            for char in row:
                if char.isnumeric():
                    new_row.extend(["."] * int(char))
                else:
                    new_row.append(char)
            new_rows.append(new_row)

        return V_SEP.join(H_SEP.join(char for char in row) for row in new_rows)
