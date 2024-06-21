adb devices
adb root
adb shell "echo 1708800 > /sys/devices/system/cpu/cpufreq/policy0/scaling_max_freq"
adb shell "echo 1708800 > /sys/devices/system/cpu/cpufreq/policy0/scaling_min_freq"
adb shell "cat /sys/devices/system/cpu/cpufreq/policy0/cpuinfo_cur_freq"

adb shell "echo 4 > /sys/devices/system/cpu/cpu0/core_ctl/max_cpus"
adb shell "echo 4 > /sys/devices/system/cpu/cpu0/core_ctl/min_cpus"

adb shell "cat /sys/devices/system/cpu/cpu0/core_ctl/active_cpus"



adb shell "echo 1010 > /sys/kernel/gpu/gpu_max_clock"
adb shell "echo 1010 > /sys/kernel/gpu/gpu_min_clock"

adb shell "cat /sys/kernel/gpu/gpu_clock"


adb shell "echo 7980 > /sys/class/devfreq/soc:qcom,cpu-cpu-ddr-bw/max_freq"
adb shell "echo 7980 > /sys/class/devfreq/soc:qcom,cpu-cpu-ddr-bw/min_freq"

adb shell "cat /sys/class/devfreq/soc:qcom,cpu-cpu-ddr-bw/cur_freq"

adb shell "stop scLogServ"
adb shell "stop logd"
