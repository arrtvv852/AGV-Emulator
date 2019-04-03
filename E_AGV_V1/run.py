# -*- coding: utf-8 -*-
"""
Created on Thu May 3 16:32:10 2018

@author: CIMlab徐孟維
"""
import ShopFloor as SF
import socket as SK
import pickle
import threading as td
import tkinter as tk
import time

def Display(Vehicle):
    time.sleep(1)
    window = tk.Tk()
    window.title("AGV Agent")
    window.geometry("{}x{}".format(1000, 200))
    canvas = tk.Canvas(bg = "white", height = 200, width = 1000)
    canvas.pack()
    canvas.create_text(100, 70, text = "AGV"+str(Vehicle.ID), font = ("arial", 20), fill = "blue")
    canvas.create_text(400, 70, text = "Target job:", font = ("arial", 20), fill = "blue")
    canvas.create_text(700, 70, text = "Load:", font = ("arial", 20), fill = "blue")
    Target = canvas.create_text(500, 70, text = "", font = ("arial", 20), fill = "red")
    Load = canvas.create_text(800, 70, text = "Empty", font = ("arial", 20), fill = "red")
    Disp = canvas.create_text(200, 70, text = "IDLE", font = ("arial", 20), fill = "red")
    disp = canvas.create_text(500, 140, text = "[]", font = ("arial", 15), fill = "black")
    while True:
        task = []
        for i in Vehicle.status:
            if len(task) > 10:
                break
            if i == 1:
                task.append("UP")
            elif i == 2:
                task.append("DOWN")
            elif i == 3:
                task.append("LEFT")
            elif i == 4:
                task.append("RIGHT")
            elif i == 5:
                task.append("DROP")
            elif i == 6:
                task.append("PICK")
        canvas.update()
        time.sleep(0.5)
        canvas.delete(disp)
        canvas.delete(Disp)
        canvas.delete(Target)
        canvas.delete(Load)
        if Vehicle.Goal >= 0:
            target = "Job"+str(Vehicle.Goal)
        else:
            target = ""
        if Vehicle.content != 0:
            load = "Job"+str(Vehicle.content)
        else:
            load = "Empty"
        if task == []:
            cur = "IDLE"
        else:
            cur = task.pop(0)
        Disp = canvas.create_text(200, 70, text = cur, font = ("arial", 20), fill = "red")
        Target = canvas.create_text(500, 70, text = target, font = ("arial", 20), fill = "red")
        Load = canvas.create_text(800, 70, text = load, font = ("arial", 20), fill = "red")
        disp = canvas.create_text(500, 140, text = str(task), font = ("arial", 15), fill = "black")


def Connect_Center(Vehicle, center, s):
    print(center.recv(1000).decode())
    center.send("AGV".encode())
    while Vehicle.ID == 0:
        True
    msg = pickle.dumps([Vehicle.ID, Vehicle.Electricity])
    center.send(msg)
    while True:
        msg = pickle.loads(center.recv(1024))
        print("Center:", msg[1])
        Type = msg[1]
        if Type == "New":
            Vehicle.Center_New(msg[2], msg[3], msg[4])
        elif Type == "S_New":
            Vehicle.Center_S_New(msg[2])
        elif Type == "Park":
            Vehicle.Center_Park()
        elif Type == "Resolve":
            Vehicle.Center_Resolve(msg[2], s)
        elif Type == "StartIdle":
            Vehicle.Center_StartIdle()
            
def Connect_Env(Vehicle, s):
    '''
    s = SK.socket(SK.AF_INET, SK.SOCK_STREAM)
    host =  "192.168.0.3"
    port = 1000
    s.connect((host, port))
    '''
    print(s.recv(1000).decode())
    s.send("AGV".encode())
    msg = pickle.loads(s.recv(1024))
    Vehicle.ID = msg[0]
    Vehicle.Electricity = msg[1]
    
    while True:
        msg = pickle.loads(s.recv(1024))
        ID, Type = msg[0], msg[1]
        access = ["Idle", "Charge", "Pick", "Drop", "Move", "Block", "Task", "LowPower", "Start"]
        print(msg)
        if ID == Vehicle.ID and Type in access:
            if Type == "Idle":
                Vehicle.FMS_Idle()
            elif Type == "Charge":
                Vehicle.FMS_Charge()
            elif Type == "Pick":
                Vehicle.FMS_Pick(s)
            elif Type == "Drop":
                Vehicle.FMS_Drop()
            elif Type == "Move":
                Vehicle.FMS_Move()
            elif Type == "Block":
                Vehicle.FMS_Block(msg[2])
            elif Type == "Task":
                Vehicle.FMS_Task(s)
            elif Type == "LowPower":
                Vehicle.FMS_LowPower()
            elif Type == "Start":
                Vehicle.FMS_Start(s)

if __name__ == "__main__":
    Vehicle = SF.Vehicle(0, 0, 0)
    
    center = SK.socket(SK.AF_INET, SK.SOCK_STREAM)
    host = "192.168.0.2"
    port  = 1001
    center.connect((host, port))
    Vehicle.connect = center
    
    s = SK.socket(SK.AF_INET, SK.SOCK_STREAM)
    host =  "192.168.0.3"
    port = 1000
    s.connect((host, port))
    
    P1 = td.Thread(target = Connect_Env, args = (Vehicle, s))
    P2 = td.Thread(target = Connect_Center, args = (Vehicle, center, s))
    P3 = td.Thread(target = Display, args = (Vehicle, ))
    P1.start()
    P2.start()
    P3.start()
    P1.join()
    P2.join()
    P3.join()