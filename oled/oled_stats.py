

import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import subprocess
import time
#import geocoder

# Change these
# to the right size for your display!
width = 128
height = 64  # Change to 64 if needed
BORDER = 5
# Use for I2C.
i2c = board.I2C()
oled = adafruit_ssd1306.SSD1306_I2C(width, height, i2c, addr=0x3C)

# Clear display.
oled.fill(0)
oled.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
image = Image.new("1", (oled.width, oled.height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Load default font.
#font = ImageFont.load_default()
header_font = ImageFont.truetype("/home/pi/rpi_oled_stats/oled/CascadiaCode.ttf", size=16)
info_font = ImageFont.truetype("/home/pi/rpi_oled_stats/oled/CascadiaCode.ttf", size=11)
padding = -2
top = padding
bottom = height-padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0
y = 13
offset = 3
try:
    while True:

        # If need IPV6 Info
        # my_ip = geocoder.ip('me')
        # if my_ip.country == "BE":
        #     vpn_status = "Connected"
        # else:
        #     vpn_status = "DISCONECTED"


        # Draw a black filled box to clear the image.
        draw.rectangle((0,0,width,height), outline=0, fill=0)

        # Shell scripts for system monitoring from here : https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
        cmd = "hostname | cut -d\' \' -f1"
        hostname = subprocess.check_output(cmd, shell=True)
        cmd = "hostname -I | cut -d\' \' -f1"
        IP = subprocess.check_output(cmd, shell = True )
        cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f%%\", $(NF-2)}'"
        CPU = subprocess.check_output(cmd, shell = True )
        cmd = "free -m | awk 'NR==2{printf \"Mem: %.2f/%.0fGB %.0f%%\", $3/1000,$2/1000,$3*100/$2 }'"
        MemUsage = subprocess.check_output(cmd, shell = True )
        cmd = "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'"
        Disk = subprocess.check_output(cmd, shell = True )

        # Write lines of text.
        draw.text((16, top), str(hostname.decode('utf-8')+".local").replace("\n",""), font=header_font, fill=255)
        draw.text((x, top+y+offset),       "IP: " + str(IP.decode('utf-8')),  font=info_font, fill=255)
        draw.text((x, top+2*y+offset),     str(CPU.decode('utf-8')), font=info_font, fill=255)
        draw.text((x, top+3*y+offset),    str(MemUsage.decode('utf-8')),  font=info_font, fill=255)
        draw.text((x, top+4*y+offset),    str(Disk.decode('utf-8')),  font=info_font, fill=255,)
        #draw.text((x, top + 33), "VPN: " + str(vpn_status), font=font, fill=255)



        # Display image.
        oled.image(image)
        oled.show()
        time.sleep(1)
finally:
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    oled.image(image)
    oled.show()
    exit(0)