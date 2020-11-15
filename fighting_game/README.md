```mermaid
graph TD
inputs --> objects
groups --Group--> objects
groups --Level--> levels
groups --Scene--> scenes
objects --Entity--> particles
particles --Plume--> levels
particles --JumpRing--> characters
levels --Battlefield--> scenes
scenes --Sandbox--> game
objects --Character--> characters
objects --Hitbox--> characters
characters --Falco--> scenes
inputs --> scenes
```

