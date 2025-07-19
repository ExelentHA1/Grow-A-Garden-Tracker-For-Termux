import time
import datetime
import os
import json
import requests

# Log file names
LOG_FILE = "events.log"
ITEM_LOG = "item.log"

# Keep track of last-triggered times to prevent duplicates
last_triggered = {}
last_update_data = " "
last_update_shopt = None

def update_shops(last_update_data,last_update_time):
    r = None
    retry = 0
    if last_update_time != datetime.datetime.now().strftime("%H:%M"):
        while True:
            try:
                r = requests.get("https://api.joshlei.com/v2/growagarden/stock")
                r.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(e)
                return None
            if last_update_data != r.text:
                print("Shops Updated..")
                break
            if retry >= 5:
                print("Shop hasnt update..")
                return None
            retry += 1
            print(f"No shop update. Retrying({retry}/5)..")
            time.sleep(3)
        return r
    return last_update_data

def get_seed(data):
    if data == None:
        return
    print("Seed in the Shop:")
    parsed_data=data.json()
    for seed in parsed_data['seed_stock']:
        print(f"\tName: {seed['display_name']}\n\t\tQuantity: {seed['quantity']}")
        log_item(seed["display_name"], seed["quantity"])
        important_items = ["Ember Lily", "Sugar Apple", "Giant Pine Seed", "Burning Bud", "Beanstalk"] 
        if seed["display_name"] in important_items:
            play_alarm()

def get_gear(data):
    if data == None:
        return
    print("Gear in the Shop:")
    parsed_data=data.json()
    for gear in parsed_data['gear_stock']:
        print(f"\tName: {gear['display_name']}\n\t\tQuantity: {gear['quantity']}")
        log_item(gear["display_name"], gear["quantity"])
        important_items = ["Medium Treat", "Levelup Lolipop", "Godly Sprinkler", "Master Sprinkler"] 
        if gear["display_name"] in important_items:
            play_alarm()

def get_egg(data):
    if data == None:
        return
    print("Egg in the Shop:")
    parsed_data=data.json()
    for egg in parsed_data['egg_stock']:
        print(f"\tName: {egg['display_name']}\n\t\tQuantity: {egg['quantity']}")
        log_item(egg["display_name"], egg["quantity"])
        important_items = ["Paradise Egg", "Bug Egg", "Mythical Egg", "Rare Summer Egg"] 
        if egg["display_name"] in important_items:
            play_alarm()


def get_cosmetic(data):
    if data == None:
        return
    print("Cosmetic in the Shop:")
    parsed_data=data.json()
    for cosmetic in parsed_data['cosmetic_stock']:
        print(f"\tName: {cosmetic['display_name']}\n\t\tQuantity: {cosmetic['quantity']}")
        log_item(cosmetic["display_name"], cosmetic["quantity"])

def play_alarm():
    # os.system("termux-media-player play alarm.mp3 > /dev/null")
    os.system("termux-vibrate -d 3000")

def log_event(message):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{now}] {message}"
    print(entry)  # Show in terminal
    with open(LOG_FILE, "a") as f:
        f.write(entry + "\n")  # Append to log file

def log_item(item_name, quantity):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{now}] Item Name: {item_name}, Quantity: {quantity}"
        with open(ITEM_LOG, "a") as f:
            f.write(entry + "\n")


def trigger(event,e_type):
    global last_update_data
    global last_update_shopt
    now = datetime.datetime.now().strftime("%H:%M")
    last_event = last_triggered.get(event)
    if last_event != now:
        s = update_shops(last_update_data, last_update_shopt)
        last_update_data = s
        last_update_shopt = now
        last_triggered[event] = now
        log_event(f"🔔 {event}")
        if e_type == "seed_gear":
            get_seed(s)
            get_gear(s)
        if e_type == "egg":
            get_egg(s)
        if e_type == "cosmetic":
            get_cosmetic(s)

def main():
    while True:
        now = datetime.datetime.now()
        minute = now.minute
        hour = now.hour
        if minute % 5 == 0:
            trigger("Seed & Gear Restock","seed_gear")
        if minute % 30 == 0:
            trigger("Egg Restock","egg")
        if hour % 4 == 0 and minute < 2:
            trigger("Cosmetic Restock","cosmetic")
        time.sleep(5)

if __name__ == "__main__":
    print("""
        ╔═╗┬─┐┌─┐┬ ┬  ╔═╗  ╔═╗┌─┐┬─┐┌┬┐┌─┐┌┐┌
        ║ ╦├┬┘│ ││││  ╠═╣  ║ ╦├─┤├┬┘ ││├┤ │││
        ╚═╝┴└─└─┘└┴┘  ╩ ╩  ╚═╝┴ ┴┴└──┴┘└─┘┘└┘
                Tracker for Termux
""")
    log_event("Script Started")
    print("Logfiles:\n\t\t-> event.log\n\t\t-> item.log")
    main()
