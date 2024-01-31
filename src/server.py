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
    def __init__(self, window) -> None:
        # bluetooth
        self.target_name = "ESP32-PatPat"
        self.target_address = None
        
        # OSC
        self.window = window
        self.running = True
        self.reset()
        threading.Thread(target=self._connect_osc, args=()).start()
        threading.Thread(target=self._update_loop, args=()).start()
        threading.Thread(target=self._connect, args=()).start()
        
        
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

            self.window.set_vrchat_status(time.time() < self.keepAliveTimeout)
        
        
    def _connect_osc(self):
        def _hit_collider_right(_, value):
            currentTime = time.time()
            if currentTime > self.last_time_right:
                self.strength_right = abs(self.prev_right_value-value)/(currentTime-self.last_time_right)
                self.prev_right_value = value
                self.last_time_right = currentTime

        def _hit_collider_left(_, value):
            currentTime = time.time()
            if currentTime > self.last_time_left:
                self.strength_left = abs(self.prev_left_value-value)/(currentTime-self.last_time_left)
                self.prev_left_value = value
                self.last_time_left = currentTime

        def _recv_packet(_, value):
            self.keepAliveTimeout = time.time() + 2

        dispatcher = Dispatcher()
        dispatcher.map("/avatar/parameters/pat_right", _hit_collider_right)
        dispatcher.map("/avatar/parameters/pat_left", _hit_collider_left)
        dispatcher.map("/avatar/parameters/*", _recv_packet)

        self.osc = BlockingOSCUDPServer(("127.0.0.1", 9002), dispatcher)
        print("OSC serving on {}".format(self.osc.server_address)) # While server is active, receive messages
        self.osc.serve_forever()



    ##############################
    # Bluetooth
    def _connect(self) -> None:
        print(f"searching for {self.target_name} bluetooth device") 
        nearby_devices = bluetooth.discover_devices(lookup_names=True, lookup_class=True)
        for btaddr, btname, btclass in nearby_devices:
            if self.target_name == btname:
                self.target_address = btaddr
                break
        if self.target_address is not None:
            print("found target {} bluetooth device with address {} ".format(self.target_name, self.target_address))
            try:
                self._connect_socket()
            except TimeoutError:
                print("could not connect to target bluetooth device")
                self.window.set_patstrap_status(False)
                self._connect()
        else:
            print("could not find target bluetooth device nearby")
            self.window.set_patstrap_status(False)
        
        #loop to make sure we stay connected
        while self.running:
            # if we reiceve a k every second we are still connected
            self.set_pat(0, 0)
            try:
                self.socket.send(b'k')
                connection = True
                for i in range(0, 5):
                    recv = self.socket.recv(1)
                    if recv.rstrip() == b'k' or not self.running:
                        break
                    self.window.set_patstrap_status(True)
                if not connection and self.running:
                    print("connection lost")
                    self.window.set_patstrap_status(False)
                    self._connect()
            except:
                print("connection lost")
                self.window.set_patstrap_status(False)
                self._connect()
                
            time.sleep(1)
            
        
    def _connect_socket(self) -> None:
        serverMACAddress = self.target_address
        port = 1
        self.socket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        self.socket.connect((serverMACAddress,port))
        print("connected to {}".format(self.target_name))
        self.window.set_patstrap_status(True)
        
    def _send(self, text) -> None:
        self.socket.send(bytes(text, 'UTF-8'))
            
    def _receive(self) -> str:
        data = self.socket.recv(1024)
        print(data.decode("utf-8").rstrip(), end="")
        return data.decode("utf-8").rstrip()
            
    def _close(self):
        self.socket.close()