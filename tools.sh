#!/bin/sh

pip install pwntools, editorconfig

cd /usr/share
git clone https://github.com/pwndbg/pwndbg
cd pwndbg
./setup.sh

# install steghide
apt-get install steghide -y

#Installing veil-evasion
pip install pyinstaller
cd /usr/share
apt-get -y install git
git clone https://github.com/Veil-Framework/Veil-Evasion.git
cd Veil-Evasion/
cd setup
setup.sh -c

#Install fuzzbunch
cd ~
apt-get install wine winetricks winbind  -y
dpkg --add-architecture i386 && apt-get update && apt-get install wine32
WINEPREFIX="$HOME/.wine-fuzzbunch" WINEARCH=win32 wine wineboot
WINEPREFIX="$HOME/.wine-fuzzbunch" winetricks python26
export WINEPREFIX=$HOME/.wine-fuzzbunch
cd $HOME/.wine-fuzzbunch/drive_c && git clone https://github.com/mdiazcl/fuzzbunch-debian
cat <<'EOF' >> /usr/local/bin/fuzzbunch
export WINEPREFIX=$HOME/.wine-fuzzbunch
cd $HOME/.wine-fuzzbunch/drive_c/fuzzbunch-debian/windows
wine ../../Python26/python.exe fb.py
EOF
chmod +x /usr/local/bin/fuzzbunch

#Installing RsaCtfTool
cd /usr/share
git clone https://github.com/hellman/libnum
cd libnum
python setup.py install
cd /usr/share
git clone https://github.com/Ganapati/RsaCtfTool
cd RsaCtfTool
apt-get install libgmp3-dev, python-dev -y
pip install -r "/usr/share/RsaCtfTool/requirements.txt"
pip install SageMath
ln -s /usr/share/RsaCtfTool/RsaCtfTool.py /usr/local/bin/rsactftool

#Installing Empire
cd /usr/share
git clone https://github.com/powershellempire/empire
empire/setup/install.sh
ln -s /usr/share/empire/empire /usr/local/bin/empire

cd /usr/share
git clone https://github.com/superkojiman/onetwopunch
ln -s /usr/share/onetwopunch/onetwopunch /usr/local/bin/onetwopunch.sh

cd /usr/share
git clone https://github.com/rebootuser/LinEnum

cd /usr/share
git clone https://github.com/SecWiki/linux-kernel-exploits
git clone https://github.com/SecWiki/windows-kernel-exploits

cd /usr/share
git clone https://github.com/danielmiessler/SecLists

cd /usr/share
wget https://raw.githubusercontent.com/haco1971/codes/master/linux-exploit-suggester.sh

cd /usr/share
wget https://raw.githubusercontent.com/haco1971/codes/master/irk-code.py

