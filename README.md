# todo: 
## events
  - event timers (`pygame.time.set_timer(event_id: int, countdown: int)`)
  - use events to trigger stuff like screen shake where the object creating the event doesn't necessarily have access to the object that implements the event behaviour.
  - integrate events in stuff like KeyHandler to reduce the overhead in their read /update actions? 
## dirty rect blitting (only updating parts of the screen that have changed) 
  - Group.clear() can remove sprites from the screen (overwrite them with BG image). 
  - Then just need to re-blit the sprites to screen; updating only the parts of the screen under their rects.
  - DirtySprite?
  - LayeredDirty has some clip functionality
  - pymunk physics http://www.pymunk.org/en/latest/

## Reusable GUI buttons / input fields
- [ ] Button implementing reliable on_press etc
  - [ ] Test states that do a constant thing e.g. glow
  - [ ] Or a button that flashes ONCE when hovered over / clicked
- Menu class that tells the buttons when they are hovered/pressed
  - mouse menu
  - keyboard menu
  - controller menu 
- Draggable thing
- Text input field

## Other
- Composition for Entity/PhysicalEntity -- e.g. Visible, Physical as interfaces that can be used in composing an entity. 

## Entity / Group structure
- Groups contain Entities 
- An Entity can have Groups containing child Entities (e.g. particle effects or projectiles belonging to it)
- The result is a tree structure: 
```
Entity
    Group
        Entity
        Entity
    Group
        Entity
            Group
                Entity
                Entity  
```

Pros: 
- The main game loop doesn't need to have a group for every single type of thing; the .draw() and .update() calls propagate down the tree of entities/groups
- Creating layers of drawing is easy; it is the same as the order of the list of Groups
  - An entity's child entities are rendered in the same layer as itself (e.g. added particles don't appear above the GUI, if that's in a separate layer)
- Each class stays pretty clean and easy to test

Cons: 
- Often an Entity doesn't have direct access to the main Game class
  - This is solved by our new Event / message logic, at least for simple cases like adding screen shake. 
  - If we wanted something more complex e.g. adding a particle to the game.particles, that couldn't be encoded in an event. 
- Sometimes the implicit layering also causes problems if we want an entity to draw itself before or after its children (or in the middle)
- Custom Entity.draw() and Group.draw() means we can't take advantage of the special draw methods in the extended Group classes. 
  - Is it possible to reformulate the structure to accommodate this? 
- If we do entity.kill(), it propagates to all child entities (e.g. projectiles). We don't necessarily want this. Can also be a good thing though. 
