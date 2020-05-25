# http://programarcadegames.com/index.php?chapter=introduction_to_sprites
# plan

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
- [ ] clickable menus 
- [ ] Create a Move class that combines 
    - [ ] Animation frames
    - [ ] Active hitboxes
    - [ ] An easy-to-program format
- [ ] Update the SpriteAnimation class to allow mapping & repeating frames. 
- [x] Fix clipping through solid platforms (use rect and collisions)
- [x] Fix automatic rect generation from sprite
- [ ] Look into [Tiled](https://sourceforge.net/projects/tiled/) for textures
- [ ] Use [Piskel](www.piskelapp.com) for sprites