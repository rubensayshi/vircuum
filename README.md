## IN DEVELOPMENT, NOT READY FOR USAGE!
I'm in progress of rewriting the whole project because the initial version was only giving commmandline output (see branch `v1.0-CLIonly`).  
This new version will run a socketio server to show a status page that live updates in the browser.

There's also a lot of code that I've copied from my previous project into this project that isn't needed anymore ..

## HELP:
`./run.py -h`

## CONFIG:
copy `config.example.py` to `config.py` (creating a new file :D).
edit `config.py` and fill in the information.

## EXAMPLES:
 - cex.io, using 10% of total balance, spread across 3 steps, using 0.1% threshold for buying and profit (0.001)
`./run.py -e cexio -t 0.001 -u 0.1 -s 3 -y -yy`

 - cex.io, using 50% of total balance, spread across 5 steps, using 0.3% threshold for buying and profit (0.003)
`./run.py -e cexio -t 0.003 -u 0.5 -s 5 -y -yy`

 - cex.io, using 0.04 BTC, spread across 7 steps, using 0.3% threshold for buying and profit (0.003)
`./run.py -e bitstamp -t 0.003 -ue 0.04 -s 7 -y -yy`

 - bitstamp, using $50, spread across 7 steps, using 1% threshold for buying and profit (0.01)
`./run.py -e bitstamp -t 0.01 -ue 50 -s 7 -y -yy`
