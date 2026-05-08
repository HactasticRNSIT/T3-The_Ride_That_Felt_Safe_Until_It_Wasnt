"""
escalation.py — SafeMesh State Machine
States: BOTH_ONLINE | PASSENGER_OFFLINE | DRIVER_OFFLINE | BOTH_OFFLINE
"""

import time
from datetime import datetime
from enum import Enum, auto

class State(Enum):
    BOTH_ONLINE        = auto()
    PASSENGER_OFFLINE  = auto()
    DRIVER_OFFLINE     = auto()
    BOTH_OFFLINE       = auto()

class C:
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    CYAN   = "\033[96m"
    BOLD   = "\033[1m"
    DIM    = "\033[2m"
    RESET  = "\033[0m"

LAST_KNOWN_LOCATION = "12.9716° N, 77.5946° E"
RIDE_ID             = "RIDE-20250508-BLR-4471"
DRIVER_PHONE        = "+91-98765-43210"
PASSENGER_PHONE     = "+91-87221-23585"
EMERGENCY_CONTACT   = "+91-87221-23585"

HEARTBEATS = [
    (True,  True ),
    (True,  True ),
    (True,  False),
    (True,  False),
    (False, False),
]

sos_log = []

def log_sos(msg):
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    entry = f"[{ts}] {msg}"
    sos_log.append(entry)
    print(f"  {C.RED}⚡{C.RESET} {entry}")

def on_enter_passenger_offline():
    print(f"  {C.YELLOW}→ ACTION:{C.RESET} Passenger heartbeat lost — starting 30s grace timer.")
    print(f"  {C.YELLOW}→ ACTION:{C.RESET} Sending in-app ping to passenger.")

def on_enter_driver_offline():
    print(f"  {C.YELLOW}→ ACTION:{C.RESET} Driver heartbeat lost — starting 30s grace timer.")
    print(f"  {C.YELLOW}→ ACTION:{C.RESET} Alerting platform ops dashboard.")

def on_enter_both_offline():
    print(f"\n{C.RED}{C.BOLD}  ██████  SOS ESCALATION TRIGGERED  ██████{C.RESET}")
    _run_sos_escalation()

def _run_sos_escalation():
    log_sos(f"Ride anomaly confirmed for {RIDE_ID}.")
    time.sleep(0.2)
    log_sos(f"Last known GPS locked → {LAST_KNOWN_LOCATION}")
    time.sleep(0.2)
    log_sos("Platform flagged: ride marked ANOMALY in ops console.")
    time.sleep(0.2)
    log_sos(f"Emergency contact notified via SMS → {EMERGENCY_CONTACT}")
    time.sleep(0.2)
    log_sos(f"Coordinates dispatched to emergency contact: {LAST_KNOWN_LOCATION}")
    time.sleep(0.2)
    log_sos(f"Automated voice call initiated → {EMERGENCY_CONTACT}")
    time.sleep(0.2)
    log_sos(f"Driver number flagged for welfare check → {DRIVER_PHONE}")
    time.sleep(0.2)
    log_sos(f"Passenger number flagged for welfare check → {PASSENGER_PHONE}")
    time.sleep(0.2)
    log_sos("Local emergency services packet prepared (pending manual confirm).")
    time.sleep(0.2)
    log_sos("Ride evidence snapshot saved: route, timestamps, heartbeat trace.")

def next_state(current, driver, passenger):
    if driver and passenger:
        return State.BOTH_ONLINE
    if driver and not passenger:
        return State.PASSENGER_OFFLINE
    if not driver and passenger:
        return State.DRIVER_OFFLINE
    return State.BOTH_OFFLINE

STATE_COLOUR = {
    State.BOTH_ONLINE:       C.GREEN,
    State.PASSENGER_OFFLINE: C.YELLOW,
    State.DRIVER_OFFLINE:    C.YELLOW,
    State.BOTH_OFFLINE:      C.RED,
}

ENTRY_ACTIONS = {
    State.PASSENGER_OFFLINE: on_enter_passenger_offline,
    State.DRIVER_OFFLINE:    on_enter_driver_offline,
    State.BOTH_OFFLINE:      on_enter_both_offline,
}

def simulate():
    print(f"\n{C.BOLD}{C.CYAN}{'═'*60}")
    print("  SafeMesh — Ride Safety State Machine")
    print(f"{'═'*60}{C.RESET}\n")
    print(f"  Ride ID : {RIDE_ID}")
    print(f"  Location: {LAST_KNOWN_LOCATION}\n")
    print(f"  {'TICK':<6}  {'DRIVER':<8}  {'PASSENGER':<11}  STATE")
    print(f"  {'─'*50}")

    state = State.BOTH_ONLINE

    for tick, (driver_alive, passenger_alive) in enumerate(HEARTBEATS, start=1):
        new_state = next_state(state, driver_alive, passenger_alive)
        d_sym = f"{C.GREEN}✓{C.RESET}" if driver_alive    else f"{C.RED}✗{C.RESET}"
        p_sym = f"{C.GREEN}✓{C.RESET}" if passenger_alive else f"{C.RED}✗{C.RESET}"
        sc    = STATE_COLOUR[new_state]

        print(f"\n  {C.BOLD}Tick {tick:>2}{C.RESET}   "
              f"Driver={d_sym}   Passenger={p_sym}   "
              f"{sc}{new_state.name}{C.RESET}")

        if new_state != state:
            print(f"  {C.DIM}  ↳ transition: {state.name} → {new_state.name}{C.RESET}")
            if new_state in ENTRY_ACTIONS:
                ENTRY_ACTIONS[new_state]()
            state = new_state

        if state == State.BOTH_OFFLINE:
            break

        time.sleep(0.4)

    if sos_log:
        print(f"\n{C.BOLD}{C.CYAN}{'═'*60}")
        print("  FULL SOS ESCALATION LOG")
        print(f"{'═'*60}{C.RESET}")
        for entry in sos_log:
            print(f"  {entry}")
        print(f"{C.BOLD}{C.CYAN}{'═'*60}{C.RESET}\n")

if __name__ == "__main__":
    simulate()
