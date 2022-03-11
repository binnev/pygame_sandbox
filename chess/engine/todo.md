# TODO

## Board to check _legal_ moves

- does a move expose king to check

## Special Pawn moves

- double first move
- en passant
- promotion

## Move class

- Will be like a diff between positions
- stack of Moves to record history and allow undoing
- tree with branches to allow analysis
- Move.apply/undo to move up/down the stack
- parser for "rbxa4" type moves (again, Move.to/from_string)

## gui

- token change 
- token change but my git username is binnev now