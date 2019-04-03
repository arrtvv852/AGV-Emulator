# -*- coding: utf-8 -*-
"""
Created on Thu May 3 16:32:10 2018

@author: CIMlab徐孟維
"""
import simpy
import ShopFloor as SF
import numpy as np
import socket as SK
import pickle
from socketserver import BaseRequestHandler, ThreadingTCPServer

class Handler(BaseRequestHandler):
    def handle(self):
        global FMS, env
        self.request.send("Welcome!!".encode())
        Type = self.request.recv(1024).decode()
        if Type == "Center":
            print("Center Connect to Server!!")
            self.env = simpy. Environment()
            env = self.env
            np.random.seed(124)
            self.FMS = SF.FMS(self.env, x=16, y=16, WS_num=12, connect=self.request)
            FMS = self.FMS
            self.env.run(until = 10000)
        elif Type == "AGV":
            print("AGV Connect to Server!!")
            self.FMS = FMS
            self.env = env
            ID = len(self.FMS.AGVs)+1
            self.FMS.newID = ID
            #Vehicle = SF.Vehicle(self.env, self.FMS, self.FMS.mesh, ID, 0, 10, self.request)
            while True:
                if len(self.FMS.AGVs) >= ID:
                    msg = pickle.dumps([ID, self.FMS.AGVs[ID-1].Electricity])
                    self.FMS.AGVs[ID-1].connect = self.request
                    self.request.send(msg)
                    ID = 10000
                elif False:
                    self.request.send(msg)
                    break

if __name__ == "__main__":
    s = SK.socket(SK.AF_INET, SK.SOCK_STREAM)
    host = "192.168.0.3"
    port = 1000
    FMS = 0
    env = 0
    '''
    s.bind((host, port))
    s.listen(10)
    
    c, addr = s.accept()
    c.send("Welcome!!".encode())
    print("Center connecting!")
    env = simpy. Environment()
    np.random.seed(124)
    FMS = SF.FMS(env, x=16, y=16, WS_num=12, connect=c)
    '''
    server = ThreadingTCPServer((host, port),Handler)
    server.serve_forever()
    '''
    env.run(until = 10000)
    FMS.window.destroy()'''
    
    

