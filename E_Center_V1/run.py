# -*- coding: utf-8 -*-
"""
Created on Thu May 3 16:32:10 2018

@author: CIMlab徐孟維
"""
import ShopFloor as SF
import numpy as np
import socket as SK
import pickle
#import Learn as Le
import threading as td
from socketserver import BaseRequestHandler, ThreadingTCPServer
import tkinter as tk
'''
le = []
le.append(Le.SVM("rbf", 2**-1, 2**0, 10))
le.append(Le.SVM("rbf", 2**-3, 2**0, 10))

data1 = pd.read_csv("V7.csv").iloc[: ,1:]
dataA = pd.read_csv("W7.csv").iloc[: ,1:]

le[0].Load_samples(data1)
le[1].Load_samples(dataA)

le[0].Learn_all()
le[1].Learn_all()
'''
def Display(Center):
    Center.window = tk.Tk()
    Center.window.title("Center Controll Agent")
    Center.window.geometry("{}x{}".format(1000, 400))
    tk.Label(text = "Dispatching", bg = "orange", font=('Arial', 12), width = 15, height = 1).pack()
    Center.Disp = tk.Text(width=50, height=8, font=("Helvetica", 14))
    Center.Disp.pack()
    tk.Label(text = "Path Planning", bg = "orange", font=('Arial', 12), width = 15, height = 1).pack()
    Center.Path = tk.Text(width=50, height=8, font=("Helvetica", 14))
    Center.Path.pack()
    Center.window.mainloop()


class Handler(BaseRequestHandler):
    def handle(self):
        global Center
        self.Center = Center
        self.request.send("Welcome!!".encode())
        Type = self.request.recv(1024).decode()
        if Type == "AGV":
            print("AGV Connect to Server!!")
            msg = self.request.recv(1024)
            msg = pickle.loads(msg)
            Vehicle = SF.Vehicle(self.Center, msg[0], 0, 10, self.request)
            while True:
                msg = self.request.recv(1024)
                msg = pickle.loads(msg)
                Type = msg[1]
                print("AGV", msg)
                if Type == "Charge":
                    Vehicle.AGV_Charge()
                elif Type == "LowPower":
                    Vehicle.AGV_LowPower()
                elif Type == "Pick":
                    Vehicle.AGV_Pick()
                elif Type == "Drop":
                    Vehicle.AGV_Drop(msg[2])
                elif Type == "Move":
                    Vehicle.AGV_Move(msg[2])
                elif Type == "Block":
                    Vehicle.AGV_Block(msg[2])
                elif Type == "Start":
                    Vehicle.AGV_Start()
                    
                    
def AGV_Listener():
    host = "192.168.0.2"
    port = 1001
    server = ThreadingTCPServer((host, port), Handler)
    server.serve_forever()
    
def Connect_Env():
    global Center
    s = SK.socket(SK.AF_INET, SK.SOCK_STREAM)
    host = "192.168.0.3"
    port = 1000
    s.connect((host, port))
    print(s.recv(1000).decode())
    s.send("Center".encode())
    
    while True:
        msg = pickle.loads(s.recv(1000))
        ID, Type = msg[0], msg[1]
        if Type == "TimeCount":
            print(msg)
            Center.FMS_TimeCount(msg[2])
        else:
            print("Job", msg)
            if Type == "Arrive":
                Center.Job_Arrive(ID, msg[2])
            else:
                for i in Center.sysJob:
                    if i.ID == ID:
                        if Type == "Finish":
                            finish = i.Finish(msg[2])
                            finish = pickle.dumps(finish)
                            s.send(finish)
                        elif Type == "Drop":
                            seq = i.Drop()
                            s.send(str(int(seq)).encode())
                        elif Type == "Process":
                            pt = i.Process()
                            s.send(str(pt).encode())

if __name__ == "__main__":    
    np.random.seed(124)
    Center = SF.Center(x=16, y=16, routRule=1, WS_num=12, AGV_disRuleV=0, AGV_disRuleW=0)
    Center.Period = 500
    Center.Warmup = 2000
    
    P1 = td.Thread(target = Connect_Env)
    P2 = td.Thread(target = AGV_Listener)
    P3 = td.Thread(target = Display, args = (Center, ))
    
    P1.start()
    P2.start()
    P3.start()
    P1.join()
    P2.join()
    P3.join()
                        

