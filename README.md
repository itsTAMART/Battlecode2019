# Battlecode2019

### USEFUL COMMANDS
to join all the code of a bot use:


        python3 compile_bot.py "bots/YOUR_BOT_NAME"
        
        %run compile_bot.py "bots/first_bot"
        
        bc19run -b bots/exampy -r bots/first_bot_to_compile --chi 1000 > log.txt

        
### Last changes

Pushing bc19 v0.4.0, with post-sprint changes.  This will be the last major change to specs or game rules.  A changelog is below.
1. Drop crusaders to 15 karbonite. Also, buff vision to 49 r^2 .
2. Castles now have 200 health, and 10 attack in an r^2 of 64. Churches are buffed to 100 health.
3. Robots can now see the origin location of signals.
4. Signaling costs fuel proportional to radius, not r^2.  The API still accepts r^2, but the fuel cost will be calculated at Math.ceil(Math.sqrt(r^2)).

### Who to scrim?

try scrim vs big red battlecode, oak's last disciple, vvvvv, knights of cowmelot, deus vult, panda lovers

