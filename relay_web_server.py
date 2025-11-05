#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#import RPi.GPIO as GPIO
from flask import Flask, render_template, jsonify, request
import time
import threading

app = Flask(__name__)

# 릴레이 핀 설정 (BCM 모드)
RELAY_PINS = [27, 17]  # 릴레이 1, 릴레이 2
RELAY_NAMES = ["릴레이 1", "릴레이 2"]

# 릴레이 상태 저장 (True = 열림, False = 닫힘)
relay_states = [False, False]

# GPIO 초기화
def init_gpio():
    """GPIO 초기화"""
    #GPIO.setmode(GPIO.BCM)
    #GPIO.setwarnings(False)

    # 릴레이 핀들을 출력으로 설정
    for pin in RELAY_PINS:
        #GPIO.setup(pin, GPIO.OUT)
        #GPIO.output(pin, GPIO.HIGH)  # 릴레이 모듈은 LOW에서 활성화되므로 HIGH로 초기화
        pass

def set_relay_state(relay_num, state):
    """릴레이 상태 설정"""
    if 0 <= relay_num < len(RELAY_PINS):
        relay_states[relay_num] = state
        # 릴레이 모듈은 LOW에서 활성화됨
        #GPIO.output(RELAY_PINS[relay_num], GPIO.LOW if state else GPIO.HIGH)
        return True
    return False

def get_relay_state(relay_num):
    """릴레이 상태 조회"""
    if 0 <= relay_num < len(RELAY_PINS):
        return relay_states[relay_num]
    return None

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html',
                         relay_names=RELAY_NAMES,
                         relay_states=relay_states)

@app.route('/api/relay/<int:relay_num>/toggle', methods=['POST'])
def toggle_relay(relay_num):
    """릴레이 토글"""
    if 0 <= relay_num < len(RELAY_PINS):
        current_state = relay_states[relay_num]
        new_state = not current_state
        set_relay_state(relay_num, new_state)

        return jsonify({
            'success': True,
            'relay_num': relay_num,
            'state': new_state,
            'message': f'{RELAY_NAMES[relay_num]} {"열림" if new_state else "닫힘"}'
        })
    else:
        return jsonify({
            'success': False,
            'message': '잘못된 릴레이 번호입니다.'
        }), 400

@app.route('/api/relay/<int:relay_num>/set', methods=['POST'])
def set_relay(relay_num):
    """릴레이 상태 직접 설정"""
    data = request.get_json()
    state = data.get('state')

    if state is None:
        return jsonify({
            'success': False,
            'message': '상태 값이 필요합니다.'
        }), 400

    if 0 <= relay_num < len(RELAY_PINS):
        set_relay_state(relay_num, state)
        return jsonify({
            'success': True,
            'relay_num': relay_num,
            'state': state,
            'message': f'{RELAY_NAMES[relay_num]} {"열림" if state else "닫힘"}'
        })
    else:
        return jsonify({
            'success': False,
            'message': '잘못된 릴레이 번호입니다.'
        }), 400

@app.route('/api/relay/status')
def get_relay_status():
    """모든 릴레이 상태 조회"""
    status = []
    for i in range(len(RELAY_PINS)):
        status.append({
            'relay_num': i,
            'name': RELAY_NAMES[i],
            'state': relay_states[i],
            'status_text': "열림" if relay_states[i] else "닫힘"
        })

    return jsonify({
        'success': True,
        'relays': status
    })

@app.route('/api/relay/all/off', methods=['POST'])
def turn_off_all():
    """모든 릴레이 끄기"""
    for i in range(len(RELAY_PINS)):
        set_relay_state(i, False)

    return jsonify({
        'success': True,
        'message': '모든 릴레이가 닫혔습니다.'
    })

@app.route('/api/relay/all/on', methods=['POST'])
def turn_on_all():
    """모든 릴레이 켜기"""
    for i in range(len(RELAY_PINS)):
        set_relay_state(i, True)

    return jsonify({
        'success': True,
        'message': '모든 릴레이가 열렸습니다.'
    })

if __name__ == '__main__':
    try:
        # GPIO 초기화
        init_gpio()
        print("릴레이 웹 서버가 시작됩니다...")
        print("웹 브라우저에서 http://라즈베리파이IP:3000 으로 접속하세요")

        # Flask 서버 실행 (모든 네트워크 인터페이스에서 접근 가능)
        app.run(host='0.0.0.0', port=3000, debug=True)

    except KeyboardInterrupt:
        print("\n서버를 종료합니다...")
    finally:
        # GPIO 정리
        #GPIO.cleanup()
        print("GPIO 정리 완료")
