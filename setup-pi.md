# Setup the pi!

## step 1

Image an sd card with Raspbian - Jessie at time of writing, if not Jessie, expect pain and misery! :(  
Expand the image give space. You can do this with `sudo raspi-config` on the pi to expand to the full size, however this can cause issues with backing up and re-imaging cards.  
Othewise use `gparted` in ubunutu to expand to a little under the full size which will make images easier to handle.

*Tip:* Open terminal with Ctrl+Alt+Fn+F1, Close terminal with Ctrl+Alt+Fn+F7

Setup the wifi on the pi by editing the `/etc/wpa_supplicant/wpa_supplicant.conf` as root. add the following:
```
network={
    ssid="{Network Name}"
    psk="{wifi password}"
}
```

Then run the following commands:
```
sudo ifdown wlan0
sudo ifup wlan0
```

## step 2

Update the pi
```
sudo apt-get update
sudo apt-get upgrade -y
sudo rpi-update
```

```
sudo apt-get install git
sudo apt-get install python3

git clone https://github.com/Kitt-AI/snowboy.git

sudo apt-get install swig3.0 build-essential
sudo apt-get install python3-dev python3-pip
sudo apt-get install python3-pyaudio sox
sudo apt-get install libatlas-base-dev
sudo apt-get install portaudio19-dev


sudo apt-get install libpcre3-dev




```

create `~/.asoundrc`
```
pcm.!default {
  type asym
   playback.pcm {
     type plug
     slave.pcm "hw:0,1"
   }
   capture.pcm {
     type plug
     slave.pcm "hw:1,0"
   }
}
```

```
amixer sset 'PCM' 100%

pip3 install wheel
pip3 install -r requirements.txt
```
