#connect to the OSC server to send and receive data
from zeroconf import Zeroconf
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.dispatcher import Dispatcher

import threading
import struct
import socket
import time
import bluetooth

class Server():
    """Server class to handle the communication between the GUI and the patstrap"""
    def __init__(self, window) -> None:
        # bluetooth
        self.target_name = "ESP32-PatPat"
        self.target_address = None
        
        # OSC
        self.window = window
        self.running = True
        self.connected = False
        self.reset()
        
        # start the different threads
        threading.Thread(target=self._connect_osc, args=()).start() # handle the OSC communication
        threading.Thread(target=self._update_loop, args=()).start() # update the patstrap every few miliseconds
        threading.Thread(target=self._connect, args=()).start() # ensure the bluetooth connection stays alive
        
        
    def shutdown(self) -> None:
        """Shutdown the server"""
        self.running = False
        self.osc.shutdown()
        self._close()
        
    def reset(self) -> None:
        """Reset the server to the default values"""
        self.strength_right = 0
        self.strength_left = 0
        self.prev_right_value = 0
        self.prev_left_value = 0
        self.prev_right = 0
        self.prev_left = 0
        self.last_time_right = time.time()
        self.last_time_left = time.time()
        self.keepAliveTimeout = time.time()
        
    def set_pat(self, left: float, right: float) -> None:
        """Send the pat intensity to the patstrap"""
        # transform the intensity to a value between 0 and 255 then send "v 0x0f 0x0f"
        left = int(left * 255)
        right = int(right * 255)
        # convert to hex
        left = hex(left)
        right = hex(right)
        # remove the 0x
        left = left[2:]
        right = right[2:]
        # add a 0 if the value is only 1 character long
        if len(left) == 1:
            left = "0" + left
        if len(right) == 1:
            right = "0" + right
        
        if left == self.prev_left and right == self.prev_right:
            return # Don't send the same data twice
        
        # Save the values for the next time
        self.prev_left = left
        self.prev_right = right
        
        # Send the data to the patstrap
        try:
            self._send("v " + left + " " + right)
            print("Left > " + left + " Right > " + right, end="\r")
        except:
            self.window.set_patstrap_status(False)
            print("connection lost")
        
    def _update_loop(self) -> None:
        """Update the server every few miliseconds"""
        while self.running:
            # Get the intensity from the gui
            intensity = self.window.get_intensity()
            
            # Decrease the intensity over time
            self.strength_right = max(0, min(1, self.strength_right-0.1))
            self.strength_left = max(0, min(1, self.strength_left-0.1))

            # Send the intensity to the patstrap
            self.set_pat(self.strength_left * intensity, self.strength_right * intensity)
            time.sleep(.1)

            # Update the status of osc connection
            self.window.set_vrchat_status(time.time() < self.keepAliveTimeout)
        
    def _connect_osc(self):
        """Connect to the OSC server to send and receive data"""
        def _hit_collider_right(_, value):
            """Callback function to handle the right pat"""
            currentTime = time.time()
            if currentTime > self.last_time_right:
                self.strength_right = abs(self.prev_right_value-value)/(currentTime-self.last_time_right)
                self.prev_right_value = value
                self.last_time_right = currentTime

        def _hit_collider_left(_, value):
            """Callback function to handle the left pat"""
            currentTime = time.time()
            if currentTime > self.last_time_left:
                self.strength_left = abs(self.prev_left_value-value)/(currentTime-self.last_time_left)
                self.prev_left_value = value
                self.last_time_left = currentTime

        def _recv_packet(_, value):
            """Callback function to handle the received packets"""
            self.keepAliveTimeout = time.time() + 2

        # register the different callback functions
        dispatcher = Dispatcher()
        dispatcher.map("/avatar/parameters/pat_right", _hit_collider_right)
        dispatcher.map("/avatar/parameters/pat_left", _hit_collider_left)
        dispatcher.map("/avatar/parameters/*", _recv_packet)

        # start the OSC server
        self.osc = BlockingOSCUDPServer(("127.0.0.1", 9002), dispatcher)
        print("OSC serving on {}".format(self.osc.server_address)) # While server is active, receive messages
        self.osc.serve_forever()

    ##############################
    # Bluetooth part
    def _connect(self) -> None:
        """Connect to the bluetooth device and start the communication loop"""
        if not self.running:
            return # Don't connect if the server is shutting down
        
        while self.running:
            # update the status of the bluetooth connection
            self.window.set_patstrap_status(self.connected)
            
            if not self.connected:
                # search for the target bluetooth device
                print(f"searching for {self.target_name} bluetooth device", end="\r") 
                nearby_devices = bluetooth.discover_devices(lookup_names=True, lookup_class=True)
                for btaddr, btname, btclass in nearby_devices:
                    if self.target_name == btname:
                        self.target_address = btaddr
                        break

                if not self.running: return # Don't connect if the server is shutting down

                # connect to the target bluetooth device
                if self.target_address is not None:
                    print("found target {} bluetooth device with address {} ".format(self.target_name, self.target_address), end="\r")
                    try:
                        self._connect_socket()
                        self.connected = True
                        print("connected to {}".format(self.target_name))
                    except TimeoutError:
                        print("could not connect to target bluetooth device    ", end="\r")
                        self.target_address = None
                else:
                    print("could not find target bluetooth device nearby    ", end="\r")
        
            #loop to make sure we stay connected
            # if we reiceve a k every second we are still connected
            while self.connected and self.running:
                if not self.running: return # Don't connect if the server is shutting down
                # update the status of the bluetooth connection
                self.window.set_patstrap_status(self.connected)
                # set the patstrap to 0 by default
                self.set_pat(0, 0) 
                
                try:
                    self.socket.send(b'k')
                    connection = False
                    for i in range(0, 3):
                        recv = self.socket.recv(1)
                        if recv.rstrip() == b'k':
                            connection = True
                            break # only exit the for loop
                    if not connection:
                        print("connection lost      ")
                        self.connected = False
                        break
                except:
                    # if something goes wrong we assume the connection is lost
                    print("connection lost      ")
                    self.connected = False
                    break
                
                # wait a second before checking again
                if self.connected: time.sleep(1)
            # if we are not connected wait a second before trying again
            if self.running: time.sleep(1)
            
        
    def _connect_socket(self) -> None:
        """Connect to the bluetooth device"""
        serverMACAddress = self.target_address
        port = 1
        self.socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        self.socket.connect((serverMACAddress,port))
        print("connected to {}".format(self.target_name), end="\r")
        self.window.set_patstrap_status(True)
        
    def _send(self, text) -> None:
        """Send the data to the bluetooth device"""
        self.socket.send(bytes(text, 'UTF-8'))
            
    def _receive(self) -> str:
        """Receive the data from the bluetooth device"""
        data = self.socket.recv(1024)
        return data.decode("utf-8").rstrip()
            
    def _close(self):
        """Close the bluetooth connection"""
        self.socket.close()