"""
Created on Thu May 3 16:32:10 2018

@author: CIMlab徐孟維
"""
import pickle

class Vehicle(object):
    def __init__(self, connect, Elec, ID):
        self.ID = ID
        self.connect = connect
        self.Electricity = Elec
        
        self.content = 0
        self.Charging = False
        self.Parking = False
        #
        self.status = []
        self.path = 0
        self.nextpath = 0
        self.Goal = -1
        
        #Stats
        self.IdleTime = 0
        self.Idling = 0
        
    
    def FMS_Start(self, fms):
        msg = pickle.dumps([self.ID, "Start"])
        self.connect.send(msg)
        fms.send("Finish_Start".encode())
        
        
    def FMS_Idle(self):
        self.Electricity -= 1/7200
        self.IdleTime += 1
        self.Idling += 1
        
    def FMS_Charge(self):
        self.Electricity = 1
        self.Charging = False
        msg = pickle.dumps([self.ID, "Charge"])
        self.connect.send(msg)
        
    def FMS_LowPower(self):
        self.Electricity -= 1/7200
        self.Charging = True
        msg = pickle.dumps([self.ID, "LowPower"])
        self.connect.send(msg)
        
    def FMS_Drop(self):
        self.Electricity -= 1/7200
        self.content = 0
        if self.Electricity < 1/20:
            self.Charging = True
            charge = True
        else:
            charge = False
        msg = pickle.dumps([self.ID, "Drop", charge])
        self.connect.send(msg)
            
    def FMS_Pick(self, fms):
        self.Electricity -= 1/7200
        self.content = self.Goal
        self.path = self.nextpath
        self.status = self.path.direct
        self.nextpath = 0
        msg = pickle.dumps([self.ID, "Pick"])
        self.connect.send(msg)
        fms.send(str(self.Goal).encode())
        self.Goal = -1
        
    def FMS_Move(self):
        self.Electricity -= 1/7200
        direct = self.status.pop(0)
        msg = pickle.dumps([self.ID, "Move", direct])
        self.connect.send(msg)
        
    def FMS_Block(self, V2):
        self.Electricity -= 1/7200
        msg = pickle.dumps([self.ID, "Block", V2])
        self.connect.send(msg)
        
    def FMS_Task(self, fms):
        if self.status != []:
            msg = self.status[0]
        elif self.nextpath != 0:
            msg = 5
        elif self.content > 0:
            msg = 6
        elif self.Charging:
            msg = 7
        elif self.Parking:
            self.Parking = False
            msg = 8
        else:
            msg = 0
        msg = str(msg).encode()
        fms.send(msg)
        
    def Center_New(self, path, nextpath, Goal):
        self.path = path
        self.status = path.direct
        self.nextpath = nextpath
        self.Goal = Goal
        
    def Center_S_New(self, path):
        self.path = path
        self.status = path.direct
        
    def Center_Park(self):
        self.Parking = True
        
    def Center_Resolve(self, path, fms):
        self.path = path
        self.status = path.direct
        #msg = "FinishResolve".encode()
        #fms.send(msg)
        
    def Center_StartIdle(self):
        self.Idling = 0
        
