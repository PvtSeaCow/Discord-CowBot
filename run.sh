set +v;
export LD_LIBRARY_PATH=/usr/local/lib;
while true; do
    python3.5 cow.py
    sleep 2
done
