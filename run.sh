set +v;
export LD_LIBRARY_PATH=/usr/local/lib;
while true; do
    python3.5 cow.py
    sleep 2
    git pull
    python3.5 -m pip install --upgrade discord.py
    python3.5 -m pip install --upgrade youtube-dl
    sleep 1
done
