# http://programarcadegames.com/index.php?chapter=introduction_to_sprites
# plan
## collisions 
So far it seems like pygame can only do collisions between rectangles. This will not cover everything I need. I want to have objects creating collections of hit/hurtboxes and detect collisions between all of these. 

- [ ] Can I get pygame to detect collisions with anything other than rectangles? Perhaps masks? 
- [ ] Get hitboxes working using just pygame's `Rect` class.
- [ ] Look into `draw.polygon()`
- [ ] Can I approximate the hit/hurtboxes I want using only pygame `Rect` classes? 
- [ ] Can I program my own hitboxes using [shapely](https://shapely.readthedocs.io/en/latest/manual.html)? And can I plot those arbitrary polygons to the screen? 
"""
Try shapely: 
For intersections of hitboxes, hurtboxes, etc
"""

## drawing objects to screen
Sprite groups have a convenient built in `.draw()` method. However, this method simply blits the sprite objects' `sprite.image` attribute to the screen using the position of `sprite.rect`. 

- [x] Can I create a transparent `sprite.canvas`? Yes. Set the `Surface` color, and then set the `colorkey` to the same color:
    ```python
    # Set the background color and set it to be transparent
    self.image = pygame.Surface([width, height])
    self.image.fill(WHITE)
    self.image.set_colorkey(WHITE)
 
    # Draw an ellipse
    pygame.draw.ellipse(self.image, color, [0, 0, width, height])
    ```
- [x] Can I subclass `SpriteGroup` to have `SpriteGroup.draw()` instead call all the sprite objects' `sprite.draw()` method? This was much easier.  

## sprites
- typical `Sprite` instance has attributes: 
    - image (used for sprite group `.draw()` method)
    - rect (used for collisions)
    - mask (used for collisions)
    
Learn how to do this "the pygame way" before you start homebrewing loads of stuff. 

## To do
- [ ] Fix clipping through solid platforms (use rect and collisions)
- [ ] Fix automatic rect generation from sprite