#
#       developed by kitteh :)
#!/usr/bin/env python2.7

import time, subprocess


COLOR = {
        "RED"       :   "0 0 {0}\n",
        "BLUE"      :   "{0} 0 0\n",
        "GREEN"     :   "0 {0} 0\n",
        "CYAN"      :   "{0} {0} 0\n",
        "MAGENTA"   :   "{0} 0 {0}\n",
        "WHITE"     :   "{0} {0} {0}\n",
        "YELLOW"    :   "0 {0} {0}\n"
        }

led = subprocess.Popen("sudo ../bin/catlight cat", 
                       stdin=subprocess.PIPE, 
                       stdout=subprocess.PIPE, 
                       shell = True) 

def fade_new(color, step=8, start=1, end=255, flag=True):
    for x in range(start,end,step):
        led.stdin.write(color.format(x) )
        time.sleep(0.00001)
    if(flag):
        fade_new(color, -step, end, start, False)

           
for item in COLOR:
    fade_new(COLOR[item],step=8)


led.stdin.close()
