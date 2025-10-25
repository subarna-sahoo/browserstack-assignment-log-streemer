

import argparse
import time 
import random


log_file = "app.log"


messages = [
    "Something happend",
    "Processing request",
    "Data Saved"
]

while True:
    msg = random.choice(messages)
    with open(log_file, "a") as f:
        f.write(msg + "\n")
    print("Wrote: ", msg)
    time.sleep(1)