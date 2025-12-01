def get_cpu_temp():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp_str = f.read().strip()
    return int(temp_str) / 1000.0

def is_overheat(alert_temp=60.0):
    temp = get_cpu_temp()
    if temp >= alert_temp:
        print(f"アラート！温度が {temp:.2f} ℃ です")
        return True
    else:
        print(f"現在の温度: {temp:.2f} ℃")
        return False