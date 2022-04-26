import math


def distance(obj1, obj2):
    dx = obj1.rect.centerx - obj2.rect.centerx
    dy = obj1.rect.centery - obj2.rect.centery
    return math.sqrt(dx**2 + dy**2)
