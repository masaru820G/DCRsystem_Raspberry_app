import RPi.GPIO as GPIO
import time
#import alert
import threading

class MotorController:
    """
    モーターの制御ロジック（ハードウェア、スレッド、状態）をすべてカプセル化（ひとまとめに）するクラス。
    ※ _motor_loopのようなアンダーバーで始まる関数は、このクラス内部だけで扱う、Flaskからは直接呼ばないでという目印
    """
    def __init__(self):
        # --- GPIO設定 ---
        # ピン番号の割当方式を「コネクタのピン番号」に設定
        # BCM ：コネクタのピン番号を使用
        # BOARD：物理的なピン番号を使用
        GPIO.setmode(GPIO.BCM)

        #GPIOピン設定
        self.PUL_pin = 14
        self.DIR_pin = 15
        self.ENA_pin = 18

        GPIO.setup(self.PUL_pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.DIR_pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.ENA_pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.output(self.DIR_pin, 0) # DIR=LOW -> 反時計回り

        # --- 状態管理変数 ---
        # パルスの幅を指定。値が小さいほど高速回転
        # self.motor_delay = 0.0004  # 速い
        # self.motor_delay = 0.0006  # 普通
        self.motor_delay = 0.0008  # 遅い
        '''
        1パルスあたりの時間[s](t) = delay * 2
        1回転あたりのパルス数[回](cnt) = (ratio = 1) * (360 / 1.8) * MICRO_status
        1回転あたりにかかる時間[s](T) = t * cnt
        '''
        self.is_running = False    # モーターの「停止フラグ」 回転を継続中かどうか
        self.motor_thread = None   # スレッドを格納する変数

        print("MotorController: 初期化完了。")

    def _motor_enable(self, enable=True):   #デフォルト引数: 引数を何も指定せずに呼び出したらenable=Trueとする
        GPIO.output(self.ENA_pin, GPIO.HIGH if enable else GPIO.LOW)

    def _one_step(self):
        GPIO.output(self.PUL_pin, GPIO.LOW)
        time.sleep(self.motor_delay)
        GPIO.output(self.PUL_pin, GPIO.HIGH)
        time.sleep(self.motor_delay)

    def _motor_loop(self):
        """
        [スレッド専用] is_runningフラグがTrueの間、回転し続ける
        """
        print("【MotorThread】: 開始。モーターを有効化します。")
        self._motor_enable(True)

        # self.is_running が True の間だけループ(停止フラグ)
        while self.is_running:
            #if alert.is_overheat(alert_temp=60.0):
            #    print("【MotorThread】: 高温のため自動停止します。")
            #    break

            self._one_step()

        print("【MotorThread】: 終了。モーターを無効化します。")
        self._motor_enable(False)

        self.is_running = False  # 絶対に is_running を False に戻す


    # --- Flaskから呼び出される「公開」関数 ---
    def start_rotation(self):
        """モーターの回転を開始する"""
        if self.is_running: # TrueやFalseといったbool値は ==Trueを省略するのが一般的
            print("MotorController: 既に回転中です。")
            return False # 既に動いているという報告をするだけ

        print("MotorController: 回転スレッドを開始します。")
        self.is_running = True # 停止フラグを True に
        self.motor_thread = threading.Thread(target=self._motor_loop)
        self.motor_thread.start()
        return True

    def stop_rotation(self):
        """モーターの回転を停止させる"""
        if not self.is_running: # TrueやFalseといったbool値は notをつけるのが一般的
            print("MotorController: 既に停止しています。")
            return

        print("MotorController: 停止フラグを立てます。")
        self.is_running = False # 停止フラグを False に
        self.motor_thread.join() # スレッドの終了を待つ

    def set_speed(self, delay):
        '''モーター速度を設定'''
        self.motor_delay = delay
        print(f"MotorController: 速度を {delay} に変更しました。")

    def get_status(self):
        """現在の状態を辞書で返す"""
        #temp = alert.get_cpu_temp()
        return {
            "motor_is_running": self.is_running,
            "current_speed_delay": self.motor_delay,
            #"cpu_temp": f"{temp:.2f}"
        }

    def cleanup(self):
        """GPIOをクリーンアップする"""
        print("MotorController: クリーンアップを実行します。")
        self.stop_rotation() # 念のためモーターを止める
        time.sleep(0.1) # スレッドが止まるのを少し待つ
        GPIO.cleanup()