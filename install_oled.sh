sudo apt install python3.11-venv
sudo python -m venv /home/pi/rpi_oled_stats/oled/oled_venv --system-site-packages
source $HOME/rpi_oled_stats/oled/oled_venv/bin/activate
cd oled/oled_venv
sudo mkdir blinka
cd blinka
pip3 install --upgrade adafruit-python-shell
pip3 install adafruit-circuitpython-ssd1306
pip install pillow
sudo wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py
yes N | sudo -E env PATH=$PATH python3 raspi-blinka.py
cd ..
cd ..
python blinkatest.py
#/home/pi/oled/oled_venv/bin/python oled_stats.py
sudo cp oled.service /lib/systemd/system/

sudo chmod 644 /lib/systemd/system/oled.service
sudo chmod +x $HOME/rpi_oled_stats/oled/oled_stats.py
sudo chmod +x $HOME/rpi_oled_stats/oled/CascadiaCode.ttf
sudo systemctl daemon-reload
sudo systemctl enable oled.service
sudo systemctl start oled.service