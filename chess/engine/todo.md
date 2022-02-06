# TODO

## Special Pawn moves

- en passant
- double first move
- promotion

## Move class

- Will be like a diff between positions
- stack of Moves to record history and allow undoing
- tree with branches to allow analysis
- Move.apply/undo to move up/down the stack
- parser for "rbxa4" type moves (again, Move.to/from_string)

## gui