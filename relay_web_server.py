#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#import RPi.GPIO as GPIO
from flask import Flask, render_template, jsonify, request
import time
import threading

app = Flask(__name__)

# Gate valve pin configuration (BCM mode)
RELAY_PINS = [27, 17]  # GV Upstream, GV Downstream
RELAY_NAMES = ["GV Upstream", "GV Downstream"]

# Gate valve state storage (True = Open, False = Close)
relay_states = [False, False]

# Gate valve lock state storage (True = locked, False = unlocked)
relay_locks = [False, False]

# GPIO initialization
def init_gpio():
    """Initialize GPIO"""
    #GPIO.setmode(GPIO.BCM)
    #GPIO.setwarnings(False)

    # Set gate valve pins as output
    for pin in RELAY_PINS:
        #GPIO.setup(pin, GPIO.OUT)
        #GPIO.output(pin, GPIO.HIGH)  # Gate valve module activates on LOW, so initialize with HIGH
        pass

def set_relay_state(relay_num, state):
    """Set gate valve state"""
    if 0 <= relay_num < len(RELAY_PINS):
        relay_states[relay_num] = state
        # Gate valve module activates on LOW
        #GPIO.output(RELAY_PINS[relay_num], GPIO.LOW if state else GPIO.HIGH)
        return True
    return False

def get_relay_state(relay_num):
    """Get gate valve state"""
    if 0 <= relay_num < len(RELAY_PINS):
        return relay_states[relay_num]
    return None

def set_relay_lock(relay_num, locked):
    """Set gate valve lock state"""
    if 0 <= relay_num < len(RELAY_PINS):
        relay_locks[relay_num] = locked
        return True
    return False

def get_relay_lock(relay_num):
    """Get gate valve lock state"""
    if 0 <= relay_num < len(RELAY_PINS):
        return relay_locks[relay_num]
    return None

def is_relay_locked(relay_num):
    """Check if gate valve is locked"""
    if 0 <= relay_num < len(RELAY_PINS):
        return relay_locks[relay_num]
    return False

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html',
                         relay_names=RELAY_NAMES,
                         relay_states=relay_states,
                         relay_locks=relay_locks)

@app.route('/api/relay/<int:relay_num>/toggle', methods=['POST'])
def toggle_relay(relay_num):
    """Toggle gate valve"""
    if 0 <= relay_num < len(RELAY_PINS):
        # Check lock state
        if is_relay_locked(relay_num):
            return jsonify({
                'success': False,
                'message': f'{RELAY_NAMES[relay_num]} is locked and cannot be controlled.'
            }), 403

        current_state = relay_states[relay_num]
        new_state = not current_state
        set_relay_state(relay_num, new_state)

        return jsonify({
            'success': True,
            'relay_num': relay_num,
            'state': new_state,
            'message': f'{RELAY_NAMES[relay_num]} {"Open" if new_state else "Close"}'
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Invalid gate valve number.'
        }), 400

@app.route('/api/relay/<int:relay_num>/set', methods=['POST'])
def set_relay(relay_num):
    """Set gate valve state directly"""
    data = request.get_json()
    state = data.get('state')

    if state is None:
        return jsonify({
            'success': False,
            'message': 'State value is required.'
        }), 400

    if 0 <= relay_num < len(RELAY_PINS):
        # Check lock state
        if is_relay_locked(relay_num):
            return jsonify({
                'success': False,
                'message': f'{RELAY_NAMES[relay_num]} is locked and cannot be controlled.'
            }), 403

        set_relay_state(relay_num, state)
        return jsonify({
            'success': True,
            'relay_num': relay_num,
            'state': state,
            'message': f'{RELAY_NAMES[relay_num]} {"Open" if state else "Close"}'
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Invalid gate valve number.'
        }), 400

@app.route('/api/relay/status')
def get_relay_status():
    """Get all gate valve status"""
    status = []
    for i in range(len(RELAY_PINS)):
        status.append({
            'relay_num': i,
            'name': RELAY_NAMES[i],
            'state': relay_states[i],
            'locked': relay_locks[i],
            'status_text': "Open" if relay_states[i] else "Close"
        })

    return jsonify({
        'success': True,
        'relays': status
    })

@app.route('/api/relay/all/off', methods=['POST'])
def turn_off_all():
    """Turn off all gate valves"""
    locked_relays = []
    for i in range(len(RELAY_PINS)):
        if not is_relay_locked(i):
            set_relay_state(i, False)
        else:
            locked_relays.append(RELAY_NAMES[i])

    message = 'All gate valves are Close.'
    if locked_relays:
        message += f' (Locked gate valves: {", ".join(locked_relays)})'

    return jsonify({
        'success': True,
        'message': message
    })

@app.route('/api/relay/all/on', methods=['POST'])
def turn_on_all():
    """Turn on all gate valves"""
    locked_relays = []
    for i in range(len(RELAY_PINS)):
        if not is_relay_locked(i):
            set_relay_state(i, True)
        else:
            locked_relays.append(RELAY_NAMES[i])

    message = 'All gate valves are Open.'
    if locked_relays:
        message += f' (Locked gate valves: {", ".join(locked_relays)})'

    return jsonify({
        'success': True,
        'message': message
    })

@app.route('/api/relay/<int:relay_num>/lock', methods=['POST'])
def toggle_relay_lock(relay_num):
    """Toggle gate valve lock state"""
    if 0 <= relay_num < len(RELAY_PINS):
        current_lock = relay_locks[relay_num]
        new_lock = not current_lock
        set_relay_lock(relay_num, new_lock)

        lock_text = "Locked" if new_lock else "Unlocked"
        return jsonify({
            'success': True,
            'relay_num': relay_num,
            'locked': new_lock,
            'message': f'{RELAY_NAMES[relay_num]} {lock_text}'
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Invalid gate valve number.'
        }), 400

if __name__ == '__main__':
    try:
        # Initialize GPIO
        init_gpio()
        print("Gate valve web server is starting...")
        print("Access http://RASPBERRY_PI_IP:3000 in your web browser")

        # Run Flask server (accessible from all network interfaces)
        app.run(host='0.0.0.0', port=3000, debug=True)

    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        # Cleanup GPIO
        #GPIO.cleanup()
        print("GPIO cleanup complete")
