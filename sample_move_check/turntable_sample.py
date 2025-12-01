import RPi.GPIO as GPIO
import time
import alert  # 温度監視モジュールをインポート

#　ピン番号の割当方式を「コネクタのピン番号」に設定
#BCM ：コネクタのピン番号を使用
#BOARD：物理的なピン番号を使用
GPIO.setmode(GPIO.BCM)

#　GPIOピン設定
DIR_pin = 15
PUL_pin = 17
ENA_pin = 18

#　15,17,18番ピンを出力ピンに設定し、初期出力をローレベルにする
GPIO.setup(DIR_pin, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(PUL_pin, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(ENA_pin, GPIO.OUT, initial=GPIO.LOW)

#　DIR=HIGHで時計回り、DIR=LOWで半時計回り。
DIR_status = 0
GPIO.output(DIR_pin, DIR_status)

#　パルスの幅を指定。値を小さくする程高速で回転する。
#delay = 0.0004  # パルス間隔
#delay = 0.0006 # 普通の回転
delay = 0.0008  # 遅い回転
ratio = 1
MICRO_status = 32

#　1回の回転あたりのパルス数
ang = 360
cnt = int(ratio * (ang / 1.8) * MICRO_status)

# モーター有効化 #ENA=HIGHでトルク発生、ENA=LOWではトルクが発生しない。
def motor_enable(enable=True):
    GPIO.output(ENA_pin, GPIO.HIGH if enable else GPIO.LOW)

# 1パルス動作
def one_step():
    GPIO.output(PUL_pin, GPIO.LOW)
    time.sleep(delay)
    GPIO.output(PUL_pin, GPIO.HIGH)
    time.sleep(delay)

try:
    print("モータ停止 → Ctrl+Cで終了\n")
    motor_enable(True)  # 最初にモーターON
    last_temp_print = time.time()

    while True:
        # 10秒ごとに温度を表示
        if time.time() - last_temp_print >= 10.0:
            temp = alert.get_cpu_temp()
            print(f"現在の温度: {temp:.2f} ℃\n")
            last_temp_print = time.time()

        # 温度監視してモーター制御
        if alert.is_overheat(alert_temp=60.0):
            # 温度超えたらモーター停止
            break
        else:
            # 温度が基準以下なら回転し続ける
            motor_enable(True)
            one_step()  # 1パルス回す

except KeyboardInterrupt:
    print("\nプログラムを停止します")

finally:
    motor_enable(False)
    GPIO.cleanup()