# plan
## collisions 
So far it seems like pygame can only do collisions between rectangles. This will not cover everything I need. I want to have objects creating collections of hit/hurtboxes and detect collisions between all of these. 

- [ ] Get hitboxes working using just pygame's `Rect` class.
- [ ] Can I get pygame to detect collisions with anything other than rectangles? Perhaps masks? 
- [ ] Can I approximate the hit/hurtboxes I want using only pygame `Rect` and `Ellipse` classes? 
- [ ] Can I program my own hitboxes using [shapely](https://shapely.readthedocs.io/en/latest/manual.html)? And can I plot those arbitrary polygons to the screen? 
"""
Try shapely: 
For intersections of hitboxes, hurtboxes, etc
"""

## drawing objects to screen
Sprite groups have a convenient built in `.draw()` method. However, this method simply blits the sprite objects' `sprite.image` attribute to the screen using the position of `sprite.rect`. 

- [ ] Can I create a transparent `sprite.canvas`? 
- [ ] Can I subclass `SpriteGroup` to have `SpriteGroup.draw()` instead call all the sprite objects' `sprite.draw()` method? This was much easier.  