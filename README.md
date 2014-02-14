
HELP:
`./run.py -h`

CONFIG:
copy `config.example.py` to `config.py` (creating a new file :D).  
edit `config.py` and fill in the information.

EXAMPLES:
 - cex.io, using 10% of total balance, spread across 3 steps, using 0.1% threshold for buying and profit (0.001)
`./run.py -e cexio -t 0.001 -u 0.1 -s 3 -y -yy > tmp/cexio.log`

 - cex.io, using 50% of total balance, spread across 5 steps, using 0.3% threshold for buying and profit (0.003)
`./run.py -e cexio -t 0.003 -u 0.5 -s 5 -y -yy > tmp/cexio.log`

 - cex.io, using 0.04 BTC, spread across 7 steps, using 0.3% threshold for buying and profit (0.003)
`./run.py -e cexio -t 0.003 -ue 0.04 -s 7 -y -yy`