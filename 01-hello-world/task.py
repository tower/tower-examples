import os
import time

# This task does nothing at all, really.
count = 0

friend = os.getenv("friend")
foe = os.getenv("foe")

while count < 5:
    count += 1
    print("Hello, {friend}! Boo to {foe}".format(friend=friend, foe=foe))
    time.sleep(1)
