# todo: 
- events
  - event timers (`pygame.time.set_timer(event_id: int, countdown: int)`)
  - use events to trigger stuff like screen shake where the object creating the event doesn't necessarily have access to the object that implements the event behaviour.
  - integrate events in stuff like KeyHandler to reduce the overhead in their read /update actions?
  - Have EventQueue manage 
    - adding new events (to a separate list)
    - reading current events from pygame.events queue
    - update (moving all events from pygame's queue to EH's queue)
- dirty rect blitting (only updating parts of the screen that have changed) 
- Colorkey / alpha / `.convert()`
  - get a MWE using `.convert()` with as little extra guff as possible
- pymunk physics