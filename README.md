
HELP:
`./run.py -h`

CONFIG cexio:
edit `run.py` and change:
`
api_key="<CEXIO-APIKEY>",
api_secret="<CEXIO-APISECRET>",
username="<CEXIO-USERNAME>", 
`

EXAMPLES:
 - cex.io, using 10% of total balance, spread across 3 steps, using 0.1% threshold for buying and profit (0.001)
`./run.py -e cexio -t 0.001 -u 0.1 -s 3 -y -yy > tmp/cexio.log`

 - cex.io, using 50% of total balance, spread across 5 steps, using 0.3% threshold for buying and profit (0.001)
`./run.py -e cexio -t 0.003 -u 0.5 -s 5 -y -yy > tmp/cexio.log`