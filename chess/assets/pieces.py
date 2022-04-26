from base.image import SpriteDict, relative_folder
from chess import conf

folder = relative_folder(__file__, "images")


chess_pieces = SpriteDict(
    folder=folder,
    size=conf.SPRITE_SIZE,
    scale=conf.SCALE_SPRITES,
    file_mapping=dict(
        pawn="pawn.png",
        king="king.png",
        queen="queen.png",
        rook="rook.png",
        knight="knight.png",
        bishop="bishop.png",
    ),
)
