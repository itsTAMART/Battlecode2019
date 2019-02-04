# Battlecode2019

### What is this?

Battlecode is an MIT's programming competition around a real-time strategy game, for which the teams will write an AI player.  In Battlecode, two teams of virtual robots roam the screen managing resources and executing different offensive strategies against each other.  The AI players will need to strategically manage their robot armies and control how their robots work together to defeat the enemy team.

The contestants will need to use artificial intelligence, pathfinding, distributed algorithms, and network communications to make their players as competitive as possible. Teams are given the Battlecode software and a specification of the game rules in early January. 

Throughout the month, they will write their players, and compete in scrimmages and tournaments against each other.  At the end of the month, the Final Tournament is played out in front of a live audience in MIT's Ray and Maria Stata Center, with the top teams receiving cash prizes. The total prize pool is over $50,000.

 

### My Bot

It is one of the few bots written in Python (due to the problems of transpiling to JS, python had some problems with iterables and importing modules). The advantages were that i felt way more comfortable in python than in JS or Java, and as I was one man team I needed all the speed writing I could have. But the disadvantages were that it was slower running and that the compatibility problems and the dynamic typing made it hard to debug because of the occlusion of error messages when playing matches.



The strategy I tried to implement was to rush in small maps and close castles, and in larger ones play economy and harass different resource points in the map and only engage in winning fights. The main problem of this contest is the short time to write and test everything, and as a solo player I couldn't implement all the features I wanted to the extent I had thought of them.



My bot implemented several useful features:

- Castle communication and synchronization to know the positions of our own castles and if any of them were rushing.
- Church synchronization with the castles so that all the resources of the map were assigned to one of the deposits (Castles and Churches).
- Map analysis and custom build orders, to switch the strategy depending on the type of map. This was an ambitious feature that couldn't be implemented to the extent I wanted. It would have been a key component to be a successful bot.
- A* targeted navigation, with control for timeout errors. Once debugged It worked way better than I expected.
- Standard Micro for all units: pilgrims mined and avoided being hit by enemy military, crusaders, prophets and preachers waited outside the enemy attack range to attack first and win the engagement.
- Different Targeting options that included targeting castles, civilian units or units that can be killed in one turn.

- Defensive Lattices around enemy objectives. Instead of placing military units around my structures I tried to place them around enemy objectives, that way I could gain more map control and reduce their advance. This feature wasn't as polished as I wanted and it would have been another key component to become a successful bot. 

- Engagement evaluation, before a fight I tried to assess if I could win it. This way I could just move to another objective if I was heavily outnumbered or win easy fights. I would have wanted to develop this feature more but time was short.



Some other things I had to do for the bot were:

- a Python script that joined all my files into one, because the imports would not work as intended and broke constantly.
- a python script to pre-calculate the ranges and rings of tiles so that my bot had them in memory and didn't have to calculate them on runtime.
- Implement a sorting algorithm and associated data structures because one of the biggest bugs in transpiled python was that the sorted() function sorted as if the elements were strings (e.g. 100, 11, 111 instead of 11, 100, 111 ) and that caused me a lot of delay and associated bugs that were hard to spot.



The modular bot can be found in the folder `.bots/first_bot ` and the file joined in one in  `.bots/first_bot_to_compile`  , this file had 5669 lines.  



### USEFUL COMMANDS
to join all the code of a bot use:


        python3 compile_bot.py "bots/YOUR_BOT_NAME"
        
        %run compile_bot.py "bots/first_bot"
        
        bc19run -b bots/exampy -r bots/first_bot_to_compile --chi 1000 > log.txt


​        
### Last changes

Pushing bc19 v0.4.0, with post-sprint changes.  This will be the last major change to specs or game rules.  A changelog is below.
1. Drop crusaders to 15 karbonite. Also, buff vision to 49 r^2 .
2. Castles now have 200 health, and 10 attack in an r^2 of 64. Churches are buffed to 100 health.
3. Robots can now see the origin location of signals.
4. Signaling costs fuel proportional to radius, not r^2.  The API still accepts r^2, but the fuel cost will be calculated at Math.ceil(Math.sqrt(r^2)).

### Who to scrim?

scrim all the international teams with old bot

scrim US with new one

**International**

`Useless Bot, Please Ignore ,
NP-cgw,
Codelympians,
Justice of the War,
DOS,
Dogma,
BetteredCod,
Team Barcode`

**US**

`Smite,
Panda Lovers,
Knights of Cowmelot,
Oak’s Last Disciple,
Standard Technology,
Flying Soba Monster,
CitricSky,
Big Red Battlecode,
Kodle,
Unlimited,
`

**Highschool**

`Useless Bot, Please Ignore, 
CitricSky,
Kryptonite,
Codelympians,
Knights of Cowmelot,
Deus Vult,
Unlimited`


### Deadlines to upload

**US and International Qualifying Tournaments:** This year, to allow adequate time for international finalists to plan travel to the US for the Final Tournament, there will be separate qualifying tournaments for US and international teams. These tournaments determine the contestants going into the Final Tournament, and showcase the final strategies of all the competitors. The top 8 teams from the US Qualifying Tournament and the top 8 teams from the International Qualifying Tournament will qualify for the Final Tournament.

Tournament Schedule

The submission deadline for all tournaments, except the Newbie, High School, and Final Tournaments, will be at 8pm EST the night before the tournament. Unlike in past years, finalists for these tournaments will be able to submit code after the Qualifying Tournament, up until Wednesday, January 31st at 8pm.

- Wednesday, January 16th - Sprint Tournament
- Monday, January 21nd - Seeding Tournament
- Friday, January 25th - International Qualifying Tournament
- Monday, January 28th - US Qualifying Tournament
- Wednesday, January 30st - Final Tournament submission deadline @ 8pm
- Friday, February 1st - Finalist’s Celebration
- Saturday, February 2nd - Newbie, High School, and Final Tournaments

The Final Tournament will occur on Saturday, February 2nd. Doors open at 6PM in MIT's Kresge Auditorium. The competition and stream begin at 7PM. 






