# todo: 
- events
  - event timers (`pygame.time.set_timer(event_id: int, countdown: int)`)
  - use events to trigger stuff like screen shake where the object creating the event doesn't necessarily have access to the object that implements the event behaviour.
  - integrate events in stuff like KeyHandler to reduce the overhead in their read /update actions?
- dirty rect blitting (only updating parts of the screen that have changed) 
  - Group.clear() can remove sprites from the screen (overwrite them with BG image). 
  - Then just need to re-blit the sprites to screen; updating only the parts of the screen under their rects.
- pymunk physics