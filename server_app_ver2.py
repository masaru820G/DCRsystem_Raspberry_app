# app.py
import signal
import sys
import subprocess
from flask import Flask, jsonify
from turntable_control import MotorController

app = Flask(__name__)
motor = MotorController()

# --- 終了シグナルを受け取る関数 ---
def sigterm_handler(signal, frame):
    """
    Systemdやkillコマンドから停止命令が来た時に呼ばれる
    """
    print("終了シグナル(SIGTERM)を受信しました。")
    motor.cleanup()
    sys.exit(0)

# SIGTERM（Systemdからの停止命令）を監視する設定
signal.signal(signal.SIGTERM, sigterm_handler)


# --- [/rotate] モータを回転させる命令 ---
@app.route('/rotate')
def handle_rotate():
    success = motor.start_rotation()
    if success:
        return "OK: モーターを開始しました。", 200
    return "Error: 既に回転中です。", 400

# --- [/stop] モータを停止させる命令 ---
@app.route('/stop')
def handle_stop():
    motor.stop_rotation()
    return "OK: モーターを停止します。", 200

# --- [/status] モータの状況を確認させる命令 ---
@app.route('/status')
def handle_status():
    return jsonify(motor.get_status())

# --- 【/system_shutdown】ラズパイ自体をシャットダウンする命令 ---
@app.route('/system_shutdown')
def handle_system_shutdown():
    try:
        motor.cleanup()
        print("システムシャットダウンを開始します...")
        subprocess.run(["sudo", "shutdown", "-h", "now"])
        return "OK: ラズパイをシャットダウンします。", 200
    except Exception as e:
        return f"Error: シャットダウンに失敗しました。{str(e)}", 500

# --- サーバー起動 ---
if __name__ == '__main__':
    try:
        print("Flaskサーバーを起動します... (Ctrl+Cで終了)")
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\nサーバーを停止します。")
    finally:
        # サーバーが終了する時に、モーターのクリーンアップを呼び出す
        motor.cleanup()
        print("サーバーを終了しました。")