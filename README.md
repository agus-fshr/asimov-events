# Events Viewer for Asimov Cup
### See and manage upcoming events for Asimov Cup.

features:
    - [x] color coded events cards
    - [x] login & sessions for admins
    - [x] sockets so events update without refreshing
    - [ ] filter events
    - [ ] brackets view

how do i deploy this thing:
    1. run the `setup_database.py` script
    2. run `app.py`
    3. use ngrok to tunnel that port to the internet
    4. profit

i did this with:
    - flask for the server-side
    - a singular python script and a sqlite3 db
    - barebones html and bootstrap css

its kinda trash but doing this could make it better:
    - [ ] rewrite in react
    - [ ] use a better db like mongo
    - [ ] write better server-side code
