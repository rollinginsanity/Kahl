cd /kahl
nohup redis-server </dev/null >/dev/null 2>&1 & #
nohup python3 /kahl/worker.py </dev/null >/dev/null 2>&1 & #
python3 /kahl/run.py
