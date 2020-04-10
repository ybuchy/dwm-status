#!/usr/bin/env python3
from subprocess import run
from re import search, sub
from ast import literal_eval
from datetime import datetime
from time import sleep
from threading import Thread


class StatusBar:
    def __init__(self, vol, temp, usage, layout, wifi, bat, cal):
        self.vol = vol
        self.temp = temp
        self.usage = usage
        self.layout = layout
        self.wifi = wifi
        self.bat = bat
        self.cal = cal

    def volume(self):
        vol_animation = ["婢", "奄", "奔", "墳"]
        cur_vol = run(["amixer", "get", "Master"], capture_output=True)
        output = cur_vol.stdout.decode("UTF-8")
        if "off" in output:
            self.vol = f"{vol_animation[0]} MUTED"
            return self.vol
        cur_vol = search(r"\[[0-9]+%\]", output)
        cur_vol = int(sub(r"[\[\]%]", "", cur_vol.group()))
        if cur_vol == 0:
            self.vol = f"{vol_animation[0]} MUTED"
        elif cur_vol in range(1, 21):
            self.vol = f"{vol_animation[1]} {cur_vol}%"
        elif cur_vol in range(21, 70):
            self.vol = f"{vol_animation[2]} {cur_vol}%"
        else:
            self.vol = f"{vol_animation[3]} {cur_vol}%"
        return self.vol

    def temperature(self):
        temp_animation = ["", "", "", "", ""]
        sensors = run(["sensors", "-j"], capture_output=True)
        sensors = sensors.stdout.decode("UTF-8").replace("\n", "")
        sensors_json = literal_eval(sensors)
        cur_temp = int(
            sensors_json["coretemp-isa-0000"]["Package id 0"]["temp1_input"])
        anim_index = cur_temp // 10 - 3
        if anim_index < 0:
            anim_index = 0
        elif anim_index > 4:
            anim_index = 4
        self.temp = f"{temp_animation[anim_index]} {cur_temp}°C"
        return self.temp

    def fsUsage(self):
        fsSymbol = ""
        usage = run(["df", "-h", "--output=avail", "-t", "ext4"],
                    capture_output=True)
        usage = usage.stdout.decode("UTF-8").replace(" ", "").split("\n")
        usage.remove("Avail")
        usage.pop()
        self.usage = f"{fsSymbol} root {usage[0]} | {fsSymbol} home {usage[1]}"
        return self.usage

    def kbLayout(self):
        loSymbol = ""
        layout = run(["setxkbmap", "-query"], capture_output=True)
        if "intl" in layout.stdout.decode("UTF-8"):
            self.layout = f"{loSymbol} US - INTL"
        else:
            self.layout = f"{loSymbol} US"
        return self.layout

    def wifiCon(self):
        wifiSymbols = ["睊", "直"]
        wifi = run(["nmcli", "connection", "show"], capture_output=True)
        wifi = wifi.stdout.decode("UTF-8")
        if "wlp0s20f3" not in wifi:
            self.wifi = f"{wifiSymbols[0]} not connected"
            return self.wifi
        for line in wifi.split("\n"):
            if "wlp0s20f3" in line:
                wifi = line.split(" ")[0]
        self.wifi = f"{wifiSymbols[1]} {wifi}"
        return self.wifi

    def battery(self):
        batterySymbols = [
            "", "", "", "", "", "", "", "", "", "", ""
        ]
        with open("/sys/class/power_supply/BAT0/capacity", "r") as f:
            capacity = int(f.read())
        if capacity > 96:
            capacity = 100
        with open("/sys/class/power_supply/BAT0/status", "r") as f:
            status = f.read()
        anim_index = capacity // 10
        if "Discharging" not in status:
            symbols = f"{batterySymbols[anim_index]}"
        if capacity == 100:
            capacity = "FULL"
        else:
            capacity = f"{capacity}%"
        self.bat = f"{symbols} {capacity}"
        return self.bat

    def calendar(self):
        calendarSymbol = ""
        now = datetime.now()
        t = now.strftime("%a, %D %I:%M%p")
        self.cal = f"{calendarSymbol} {t}"
        return self.cal

    def refresh(self):
        run([
            "xsetroot", "-name",
            f" {self.vol} | {self.temp} | {self.usage} | {self.layout} | {self.wifi} | {self.bat} | {self.cal}"
        ])


class FnctThread(Thread):
    def __init__(self, fnct, delay):
        super().__init__()
        self.fnct = fnct
        self.delay = delay

    def run(self):
        while True:
            self.fnct()
            sleep(self.delay)


def main():
    bar = StatusBar("", "", "", "", "", "", "")
    # vol temp fsUsage layout wifi bat cal
    delays = [.5, 5, 5, .5, 1, 1, 5]
    volThread = FnctThread(bar.volume, delays[0])
    tempThread = FnctThread(bar.temperature, delays[1])
    fsUsageThread = FnctThread(bar.fsUsage, delays[2])
    layoutThread = FnctThread(bar.kbLayout, delays[3])
    wifiThread = FnctThread(bar.wifiCon, delays[4])
    batteryThread = FnctThread(bar.battery, delays[5])
    calendarThread = FnctThread(bar.calendar, delays[6])
    refreshThread = FnctThread(bar.refresh, min(delays))
    volThread.start()
    tempThread.start()
    fsUsageThread.start()
    layoutThread.start()
    wifiThread.start()
    batteryThread.start()
    calendarThread.start()
    refreshThread.start()


if __name__ == "__main__":
    main()
