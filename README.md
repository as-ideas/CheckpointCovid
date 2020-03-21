# Checkpoint Covid

## Description
Checkpoint Covid is a prototype for a server-client mobile application which allows the clients to 
build a history of real-world encounters, which is used by the clients to check if they came in contact with users who tested positive for the virus.

The server stores no positional information, but notifies the client when
there are other users in the same area.<br>
With this information clients then build a local history of contacts.<br>

The information stored on the server is a list of infected users, while locally the clients store an anonymous time-series of encounters.

Currently this is done by mapping the position of the users
to tiles on a map, future steps of the project include a proximity signal, so the clients will independently build the contact history
 by scanning their environments 
 
 ## How does it work

While running, the client app sends its current location (x,y) to the server.<br>
The server maps these location to a tile on the map (ideally only streets).<br>
The server discards the location information when new is available, so it does NOT store any location history.

The server checks if multiple users are in the same tile at the same time (gropuby tile, count users)
 and builds a list of tiles containing multiple users:<br>
```
 [int: tile_n, list: user_ids]
 e.g.
 [[tile1, [user1, user2, user8]], 
  [tile18, [user3, user42],
  ...
 ]
``` 

The server then sends the list of user_ids to the users involved.<br>


The users, on their local device, build a list of "encounters" (contacts) as
```[(user1, time1), (user2, time1), (user14, time5), ...]```

When a user is tested positive, the users send a message to the server, which maintains a list of positives with timestamps.

When the clients update their contact history, or when the infected list is updated on the server,
 the clients locally scan their contact history to find any (time-stamped) overlap with the list of positives on the server and send a response to the server, which then updates, or not, the list of positive users.