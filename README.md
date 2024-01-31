# PatPatHaptic - Haptic Feedback for VRChat with an ESP32 using Bluetooth
This is a project to add haptic feedback to VRChat using an ESP32 and a few other components. It is based on the [Patstrap](https://github.com/danielfvm/Patstrap) project by [danielfvm](https://github.com/danielfvm).

THIS IS STILL IN DEVELOPMENT ! Update will come soon regarding the documentation on how to setup the project.

## Why?
I tried to use the Patstrap project, but I had some issues with it. So I decided to make my own version of it.  
Problems I had with the Patstrap project:
- The latency was too high (on my wifi I had between 1s and 10sec of latency) so the experience was not good.
- The python server was taking 12% off my CPU for no reason so not good when playing VRC.

### So what's different?
- Instead of using a wifi connection, I use a bluetooth connection. This allows me to have a latency of 0.1s to 0.5s. on local and 0.5s to 1s. on VRChat.
- I modified the python server to work with bluetooth while keeping the same UI.

## How to use it?
### What you need:
To test this project you will need:
- An ESP32 (I used a [ESP32 30PIN](https://fr.aliexpress.com/item/1005005970816555.html))
- A breadboard
- 2x ???kΩ resistors
- 2x Transistors (I used 2N2222 )
- 2x vibrating motors
- A computer with bluetooth
- VRCOSC (optional)

### How to setup:
- Use Vscode and Platform.io to make a project and upload the code to the ESP32.
- Connect the circuit to the ESP32 (see the circuit diagram below) <img src="https://raw.githubusercontent.com/kikookraft/HapticPatPat/main/circuit.png" alt="Circuit diagram" style="zoom:40%;" />
- Run the python server that will connect to the ESP32 and VRC OSC or VRCOSC program.
- Setup your avatar in VRChat and add contact to make the interaction work.
- Enjoy!

### How to build the executable:
You have two way of compiling the python server:
- Using the build.bat file (Windows only)
- Using the command line (pyinstaller):
``` bash
pyinstaller -F -n PatPatHaptic -i icon.png --collect-submodules zeroconf --noconsole src/main.py
```