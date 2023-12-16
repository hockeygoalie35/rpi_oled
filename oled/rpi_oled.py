import argparse
import time
import threading
from PIL import Image, ImageDraw, ImageFont
import subprocess
import time
from datetime import datetime
import os
import psutil
import socket
if os.name != 'nt':
    import board
    import digitalio
    import adafruit_ssd1306





class ssd1306_display():
    def __init__(self,width,height,font_path):
        self.max_autosize = 64
        self.border = 6 # makes sure there's no text run-off
        self.current_y = 0
        self.screen_width = width
        self.screen_height = height
        self.oled = None
        self.font_path = font_path
        self.header_font = ImageFont.truetype(self.font_path, size=10)
        #info_font = ImageFont.truetype("/home/pi/rpi_oled_stats/oled/CascadiaCode.ttf", size=11)
        self.init_screen()


    def init_screen(self):
        # Creats OLED object and blanks screen
        i2c = board.I2C()
        self.oled = adafruit_ssd1306.SSD1306_I2C(self.screen_width, self.screen_height, i2c, addr=0x3C)
        # Clear display.
        self.clear_buffer()
    def calculate_font_size(self, text, font_object):
        # calculate the font size to use based on text length, no larger than 16
        # Initial conditions
        length = 0
        font_size = 1

        while length < self.screen_width-(2*self.border): # Iterate thru sizes until too big
            font_object = ImageFont.truetype(self.font_path, size=float(font_size))
            length = font_object.getlength(text)
            font_size += 1
            #print(length)
        if font_size > self.max_autosize:
            font_size = self.max_autosize  # Remember, no larger than 128. got other info to fit
        font_size = font_size-1# so it still fits on the screen
        # TODO: Scale the reduction value based on len or font size?
        font_object = ImageFont.truetype(self.font_path, size=float(font_size))  # sets the calculated font_size
        #print(font_size)
        return font_object
    def write_line(self, text,start_x=0, start_y='auto', font_size=10, center=False,auto_size=False):
        font = ImageFont.truetype(self.font_path, size=font_size)


        if start_y == 'auto':
            start_y = self.current_y

        if auto_size is True:
            font = self.calculate_font_size(text, font)

        textboxval = self.draw.textbbox((0, 0), text, font=font)  # textbbox returns tuple

        if center is True:
            start_x = float((self.screen_width - textboxval[2]) / 2)
            #print(textboxval)
        self.draw.text((start_x, start_y), str(text), font=font,fill=255)
        self.current_y += textboxval[3]
        #print(f'current y is now {self.current_y}')

    def clear_buffer(self):
        self.current_y = 0
        self.oled.fill(0)
        #self.oled.show()
        self.image = Image.new("1", (self.oled.width, self.oled.height))  # Create blank image for drawing.
        self.draw = ImageDraw.Draw(self.image)

    def clear_display(self):
        self.clear_buffer()
        self.oled.fill(0)
        self.oled.show()
    def commit(self):

        self.oled.image(self.image)
        self.oled.show()
        self.clear_buffer()


class pi_oled():
    def __init__(self):
        self.oled_display = ssd1306_display(128,64,"/home/pi/rpi_oled_stats/oled/CascadiaCode.ttf")
        #self.argument_parsing()

        self.init_stat_page()

        self.stop_loop = False

        self.set_page(self.stat_page)



    def init_stat_page(self):
        def get_hostname():
            hostname = socket.gethostname()
            return hostname

        def get_IP():
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            return ip_address

        def get_cpu():
            if os.name == 'nt':
                load1, load5, load15 = psutil.getloadavg()
            else:
                load1, load5, load15 = os.getloadavg()
            cpu_usage = round((load1 / os.cpu_count()) * 100, 3)
            return cpu_usage

        def get_ram():
            byte_to_gigabyte = 1000000000
            ram = psutil.virtual_memory()
            used_ram = round(ram.used / byte_to_gigabyte, 2)
            total_ram = int(ram.total / byte_to_gigabyte)
            percentage = ram.percent
            return used_ram, total_ram, percentage

        def get_disk():
            byte_to_gigabyte = 1000000000
            total_disk, used_disk, free_disk, percentage = psutil.disk_usage('/')
            used_disk = int(used_disk / byte_to_gigabyte)
            total_disk = int(total_disk / byte_to_gigabyte)
            percentage = int(percentage)
            return used_disk, total_disk, percentage

        # page object
        self.stat_page = Page(self.oled_display)
        self.oled_display.max_autosize = 15

        hostname_display = Line(line_format="{}", function=get_hostname, auto_size=True,center=True)
        ip_address_display = Line(line_format='IP: {}', function=get_IP, font_size=12)
        cpu_usage = Line(line_format = "CPU Load: {}%",function=get_cpu, font_size=12)
        ram_usage = Line(line_format="RAM: {}/{} {}%",function=get_ram, font_size=12)
        disk_usage = Line(line_format="DSK: {}/{}GB {}%",function=get_disk, font_size=12)
        self.stat_page.lines = [hostname_display, ip_address_display, cpu_usage, ram_usage, disk_usage]

    def set_page(self,page):
        while self.stop_loop is False:
            page.refresh()
            time.sleep(5)




class Page():
    def __init__(self,ssd1306_display_instance):
        self.lines = []
        self.displayInstance = ssd1306_display_instance



    def refresh(self):
        #self.displayInstance.clear_display()
        self.displayInstance.clear_buffer()
        for line in self.lines:
            line.update_text()
        print("updated lines")

        for line in self.lines:
            #print(line.line_text)
            self.displayInstance.write_line(line.line_text,center=line.center,auto_size=line.auto_size,font_size=line.font_size)
        self.displayInstance.commit()
        print("updated screen")


class Line():
    def __init__(self, line_format, function=None, center=False, auto_size=False, font_size=10):
        self.center = center
        self.auto_size = auto_size
        self.font_size = font_size
        self.line_format = line_format
        self.line_text = None
        self.function = function

    def update_text(self):
        print(self.function())
        try:
            self.line_text = self.line_format.format(self.function())
        except:
            self.line_text = self.line_format.format(*self.function())

        print(self.line_text)





class Command():
    def __init__(self,cliText:str):
        self.cliText = cliText
        self.output = None
        self.update()
        print(self.output)


    def update(self):
        self.output = subprocess.check_output(self.cliText, shell=True).decode('utf-8').replace('\n', '')
        return str(self.output)

    def __str__(self):
        return str(self.output)



if __name__ == '__main__':
    pi = pi_oled()