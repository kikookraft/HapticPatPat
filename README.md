# Bluetooth PatStrap - Haptic Feedback for VRChat
This is a project to add haptic feedback to VRChat using an ESP32 and a few other components. It is based on the [Patstrap](https://github.com/danielfvm/Patstrap) project by [danielfvm](https://github.com/danielfvm).

Ce fichier README est également disponible en [français](https://github.com/kikookraft/HapticPatPat/blob/main/README_FR.md).

## What is this project?
This project (like the Patstrap project) is an open project that allows you to add haptic head pat feedpack for VR players in VRChat.  
Here is how the project works:
- Someone pat you on the head and thanks to contact on your avatar it send a OSC message to the python server.
- The python server reiceve the OSC message and send a bluetooth message to the ESP32.
- The ESP32 receive the bluetooth message and activate the motors based on the message (head pat left, right or both).

### Why making another version of the Patstrap project?
I tried to use the Patstrap project, but I had some issues with it. So I decided to make my own version of it.  
Problems I had with the Patstrap project:
- The latency was too high (on my wifi I had between 1s and 10sec of latency) so the experience was not good.
- The python server was taking 12% off my CPU for no reason so not good when playing VRC (maybe I did something wrong??).

### So what's different?
- Instead of using a wifi connection, I use a bluetooth connection.   
This allows me to keep a very low latency
 (way less than a second between the head pat and the motors activation)
- I modified the python server to work with bluetooth while keeping the same UI of the original project.
- I added a compiled version of the python server so you don't need to install python and all the dependencies to run the server.

## Hardware parts
To make this project you will need:
- ESP32, I used a [ESP32 30PIN](https://aliexpress.com/item/1005005970816555.html) but any equivalent with bluetooth support should work.  
If you use a different ESP32, you may need to change the pins in the code.
- 2x [330Ω resistors](https://aliexpress.com/item/1005006362959267.html)
- 2x [Transistors](https://aliexpress.com/item/1005005755402536.html) (I used BC547)
- 2x [vibrating motors](https://aliexpress.com/item/1005001446097852.html)
- A [pcb board](https://aliexpress.com/item/1005006365975004.html) (or something to put the circuit on)
- If using a pcb board, it will be better to have [Dupont sockets](https://amzn.eu/d/i0pZoIV) to connect the ESP32 to the pcb
- 2x [Diodes](https://aliexpress.com/item/1005006054373731.html) (Only needed if using a battery)
- [battery](https://www.amazon.com/dp/B0B7N2T1TD?psc=1&ref=ppx_yo2ov_dt_b_product_details) (I used a 3.7V 2000mAh battery)
- [battery charger](https://aliexpress.com/item/1005006274938832.html) (I used a TP4056)
- [on/off switch](https://aliexpress.com/item/1005003938856402.html) (Only needed if using a battery)
- computer with **bluetooth**   
 
Here is the simplified circuit:  
![](https://raw.githubusercontent.com/kikookraft/HapticPatPat/main/img/final_circuit.png)

And there is the final circuit on a pcb:
![](https://raw.githubusercontent.com/kikookraft/HapticPatPat/main/img/geek_sandwich.JPG)

## Software
### Firmware
The code for the ESP32 was developed using [PlatformIO](https://platformio.org/platformio-ide) and [Visual Studio Code](https://code.visualstudio.com/).
Everything is placed in the `/firmware` folder.
You may need to change the pins used in the code if you use a different ESP32, do this in the `/firmware/src/main.cpp` file.

After the editing, you can compile and upload the code to your ESP32 using PlatformIO button in Visual Studio Code.
![](https://raw.githubusercontent.com/kikookraft/HapticPatPat/main/img/vsc.png)

When not connected to bluetooth, the ESP32 will blink the onboard LED. When connected, the LED will stay off.

### Server
[Here](https://github.com/kikookraft/HapticPatPat/releases) you can download the compiled version of the python server.
You just need to launch it when you want to use the haptic feedback.  
![](https://raw.githubusercontent.com/kikookraft/HapticPatPat/main/img/UI.png)

If you are using VRCOSC, you can automatically launch the server when you launch VRChat by adding the server to the VRCOSC settings. 
![](https://raw.githubusercontent.com/kikookraft/HapticPatPat/main/img/vrcosc.png)

The server is essential to make the project work. It is used to receive the OSC messages from VRChat and send the bluetooth messages to the ESP32.
The UI is the same as the original project, but the code implemented is different since I had to change the way the server works to use bluetooth instead of wifi.

You can compile the server yourself using the `/server/build.bat` file or using the following command:
``` bash
pyinstaller -F -n PatPatHaptic -i icon.png --collect-submodules zeroconf --noconsole .\server\main.py
```
### VRChat & OSC
You can follow the original [Patstrap](https://github.com/danielfvm/Patstrap?tab=readme-ov-file#vrchat) documentation to setup VRChat and OSC.
