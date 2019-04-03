"""
Created on Thu May 3 16:32:10 2018

@author: CIMlab徐孟維
"""
import simpy
import tkinter as tk
import numpy as np
import time
import pickle

#unit = 50
#Hight = 7
#Width = 7
#Origin = [1, 1]


class Job(object):
    def __init__(self, env, fms, ID, connect):
        self.env = env
        self.fms = fms
        self.ID = ID
        self.position = fms.stations[0]
        self.fms.Jobs.append(self)
        self.Queue = self.env.event()
        self.position.out_queue.append(self)
        self.env.process(self.flow())
        
        self.connect = connect
            
    def flow(self):
        yield self.env.timeout(0)
        msg = pickle.dumps([self.ID, "Arrive", self.env.now])
        self.connect.send(msg)
        self.out_req = self.fms.stations[0].out_buffer.request()
        while True:
            yield self.Queue
            msg = pickle.dumps([self.ID, "Drop"])
            print("Dropping send")
            self.connect.send(msg)
            self.Queue = self.env.event()
            yield self.env.timeout(0)
            st = self.connect.recv(1000)
            st = int(st.decode())
            station = self.fms.stations[st]
            self.position = station
            req = station.resource.request()
            station.in_queue.append(self)
            
            if station.ID < 11:
                station.del_show(ID = station.ID)
                station.Create_show(ID = station.ID, Work = True)
            
            
            yield req
            station.in_queue.remove(self)
            if station.ID < 11:
                station.del_show(ID = station.ID)
                station.Create_show(ID = station.ID, Work = True)
            
            msg = pickle.dumps([self.ID, "Process"])
            self.connect.send(msg)
            station.processing = self
            pt = self.connect.recv(1000)
            print("ProcessTime", pt)
            pt = float(pt.decode())
            yield self.env.timeout(pt)
            
            station.processing = 0
            
            self.out_req = station.out_buffer.request()
            yield self.out_req
            msg = pickle.dumps([self.ID, "Finish", self.env.now])
            self.connect.send(msg)
            station.out_queue.append(self)
            
            if station.ID < 11:
                station.del_show(ID = station.ID)
                station.Create_show(ID = station.ID, Work = False)
                
            station.resource.release(req)
            finish = self.connect.recv(1000)
            finish = pickle.loads(finish)
            if finish:
                break
            
            
            
class Station(object):
    def __init__(self, env, fms, id):
        self.env = env
        self.fms = fms
        self.ID = id
        self.in_queue = []
        self.out_queue = []
        self.out_cap = 5
        
        self.processing = []
        self.location(id)
        self.Create_show(ID = self.ID)
        
        if self.ID != 0 and self.ID != 11:
            self.resource = simpy.Resource(self.env, 1)
            self.out_buffer = simpy.Resource(self.env, self.out_cap)
        else:
            self.resource = simpy.Resource(self.env, 1000)
            self.out_buffer = simpy.Resource(self.env, 1000)
            
        self.fms.stations.append(self)
        
    def location(self, ID):
        if ID == 0:
            self.x = 0
            self.y = 2
        elif ID == 1:
            self.x = 9
            self.y = 8
        elif ID == 2:
            self.x = 5
            self.y = 2
        elif ID == 3:
            self.x = 8
            self.y = 2
        elif ID == 4:
            self.x = 13
            self.y = 4
        elif ID == 5:
            self.x = 13
            self.y = 7
        elif ID == 6:
            self.x = 13
            self.y = 10
        elif ID == 7:
            self.x = 3
            self.y = 13
        elif ID == 8:
            self.x = 6
            self.y = 13
        elif ID == 9:
            self.x = 9
            self.y = 13
        elif ID == 10:
            self.x = 4
            self.y = 8
        elif ID == 11:
            self.x = 0
            self.y = 1
            
    def Create_show(self, ID = 0, Work = False):
        if 0 < ID < 11:
            PD = [self.x, self.y]
            if ID == 1 or ID == 2 or ID == 3 or ID == 10:
                PD[1] -= 1.5
            elif ID == 4 or ID == 5 or ID == 6:
                PD[0] += 1.5
            else:
                PD[1] += 1.5
    
            p = [(self.fms.Origin[0]+PD[0])*self.fms.unit, (self.fms.Origin[1]\
                 +self.fms.Hight-PD[1])*self.fms.unit]
            if ID == 4 or ID == 5 or ID == 6:
                p1 = [(self.fms.Origin[0]+PD[0]-1)*self.fms.unit, (self.fms.Origin[1]\
                      +self.fms.Hight-PD[1]-1.5)\
                      *self.fms.unit]
                p2 = [(self.fms.Origin[0]+PD[0]+1)*self.fms.unit, (self.fms.Origin[1]\
                      +self.fms.Hight-PD[1]+1.5)\
                      *self.fms.unit]
            else:
                p1 = [(self.fms.Origin[0]+PD[0]-1.5)*self.fms.unit, (self.fms.Origin[1]\
                      +self.fms.Hight-PD[1]-1)\
                      *self.fms.unit]
                p2 = [(self.fms.Origin[0]+PD[0]+1.5)*self.fms.unit, (self.fms.Origin[1]\
                      +self.fms.Hight-PD[1]+1)\
                      *self.fms.unit]
            if Work:
                self.Show = self.fms.canvas.create_rectangle(p1[0], p1[1], p2[0], p2[1]\
                                             , fill = "pink")
            else:
                self.Show = self.fms.canvas.create_rectangle(p1[0], p1[1], p2[0], p2[1]\
                                             , fill = "orange")
            self.show = self.fms.canvas.create_text(p[0], p[1], text = "W"+str(ID)\
                                        , font = ("arial", 15), fill = "blue")
            self.IN_show = self.fms.canvas.create_text(p[0], p[1]-0.5*self.fms.unit, text = "IN:"\
                                        , font = ("arial", 15), fill = "black")
            self.OUT_show = self.fms.canvas.create_text(p[0], p[1]+0.5*self.fms.unit, text = "OUT:"\
                                        , font = ("arial", 15), fill = "black")
            self.in_show = self.fms.canvas.create_text(p[0]+0.8*self.fms.unit, p[1]-0.5*self.fms.unit, text = str(len(self.in_queue))\
                                        , font = ("arial", 15), fill = "black")
            self.out_show = self.fms.canvas.create_text(p[0]+0.8*self.fms.unit, p[1]+0.5*self.fms.unit, text = str(len(self.out_queue))\
                                        , font = ("arial", 15), fill = "black")
            
    def del_show(self, ID):
        if 0 < ID < 11:
            self.fms.canvas.delete(self.Show)
            self.fms.canvas.delete(self.show)
            self.fms.canvas.delete(self.IN_show)
            self.fms.canvas.delete(self.OUT_show)
            self.fms.canvas.delete(self.in_show)
            self.fms.canvas.delete(self.out_show)
            


class Vehicle(object):
    def __init__(self, env, fms, mesh, id, x, y, connect):
        self.ID = id
        self.x = x
        self.y = y
        self.task = 0
        self.env = env
        self.fms = fms
        self.create_show()
        self.mesh = mesh
        self.env.process(self.nevigation())
        self.content = 0
        self.Electricity = np.random.uniform(0.5, 1)
        self.fms.AGVs.append(self)
        self.connect = connect
        
        
    def nevigation(self):
        self.req_ori = self.mesh[self.x][self.y].request()
        self.req_tar = 0
        msg = pickle.dumps([self.ID, "Start"])
        self.connect.send(msg)
        print(self.connect.recv(1024).decode())
        while True:
            msg = pickle.dumps([self.ID, "Task"])
            self.connect.send(msg)
            print(pickle.loads(msg))
            msg = self.connect.recv(1000)
            msg = int(msg.decode())
            self.task = msg
            print(self.task)
            if 4 >= self.task > 0:
                if self.task == 1:
                    nextpos = [self.x, self.y+1]
                elif self.task == 2:
                    nextpos = [self.x, self.y-1]
                elif self.task == 3:
                    nextpos = [self.x-1, self.y]
                elif self.task == 4:
                    nextpos = [self.x+1, self.y]
                if self.detect(self.mesh[nextpos[0]][nextpos[1]].users):
                    next
                        
                self.req_tar = self.mesh[nextpos[0]][nextpos[1]].request()
                
                yield self.req_tar
                
                    
                for i in range(self.fms.split):
                
                    yield self.env.timeout(1/self.fms.split)
                    if self.task != []:
                        self.moving(self.task)
                self.mesh[self.x][self.y].release(self.req_ori)
                self.x = nextpos[0]
                self.y = nextpos[1]
                self.req_ori = self.req_tar
                msg = pickle.dumps([self.ID, "Move"])
                self.connect.send(msg)
                self.task = 0
            
            #AGV load job
            elif self.task == 5:
                self.fms.canvas.delete(self.Show)
                self.fms.canvas.delete(self.show)
                self.create_show(2)
                yield self.env.timeout(5)
                msg = pickle.dumps([self.ID, "Pick"])
                self.connect.send(msg)
                k = self.connect.recv(1000)
                k = int(k.decode())-1
                self.content = self.fms.Jobs[k]
                self.content.position.out_buffer.release(self.content.out_req)
                self.content.position.out_queue.remove(self.content)
                
                if self.content.position.ID < 11:
                    self.content.position.del_show(ID = self.content.position.ID)
                    self.content.position.Create_show(ID = self.content.position.ID, Work = False)
                
                self.content.position = self
                self.task = 0
                
                self.fms.canvas.delete(self.Show)
                self.fms.canvas.delete(self.show)
                self.create_show(1)
            
            #AGV Unload job
            elif self.task == 6:
                self.fms.canvas.delete(self.Show)
                self.fms.canvas.delete(self.show)
                self.create_show(2)
                yield self.env.timeout(5)
                self.content.Queue.succeed()
                msg = pickle.dumps([self.ID, "Drop"])
                self.connect.send(msg)
                self.content = 0
                
                self.fms.canvas.delete(self.Show)
                self.fms.canvas.delete(self.show)
                self.create_show()
            #Charging
            elif self.task == 7:
                yield self.env.timeout(300)
                self.Electricity = 1
                msg = pickle.dumps([self.ID, "Charge"])
                self.connect.send(msg)
            #Parking
            elif self.task == 8:
                msg = pickle.dumps([self.ID, "Parking"])
                self.connect.send(msg)
            
            else:
                yield self.env.timeout(1)
                if self.Electricity >= 1/20:
                    msg = pickle.dumps([self.ID, "Idle"])
                    self.connect.send(msg)
                else:
                    msg = pickle.dumps([self.ID, "LowPower"])
                    self.connect.send(msg)
                
            self.Electricity -= 1/7200

                
    def detect(self, req):
        sensor = False
        print(self.ID, "DETECTing")
        if req != []:
            for i in range(len(self.fms.AGVs)):
                if self.fms.AGVs[i].req_ori == req[0] or self.fms.AGVs[i].req_tar == req[0]:
                     V2 = self.fms.AGVs[i]
                     msg = pickle.dumps([self.ID, "Block", V2.ID])
                     print("SENT BLOCK TO AGV")
                     self.connect.send(msg)
            print(self.ID, "CONFLICT")
            #self.connect.recv(1024)
            sensor = True
        return sensor
        
                
    def create_show(self, Full = 0):
        #AGVs
        p = [(self.fms.Origin[0]+self.x)*self.fms.unit, (self.fms.Origin[1]+self.fms.Hight-self.y)*self.fms.unit]
        p1 = [(self.fms.Origin[0]-0.4+self.x)*self.fms.unit, (self.fms.Origin[1]+self.fms.Hight-0.4-self.y)*self.fms.unit]
        p2 = [(self.fms.Origin[0]+0.4+self.x)*self.fms.unit, (self.fms.Origin[1]+self.fms.Hight+0.4-self.y)*self.fms.unit]
        
        if Full == 1:
            self.Show = self.fms.canvas.create_oval(p1[0], p1[1], p2[0], p2[1], fill = "red")
        elif Full == 2:
            self.Show = self.fms.canvas.create_oval(p1[0], p1[1], p2[0], p2[1], fill = "green")
        else:
            self.Show = self.fms.canvas.create_oval(p1[0], p1[1], p2[0], p2[1], fill = "purple")
        self.show = self.fms.canvas.create_text(p[0], p[1], text = "A" + str(self.ID), font = ("arial", 10), fill = "yellow")
        
    def moving(self, action):
        base_action = [0, 0]
        if action == 1:
            base_action = [0, -1]
        elif action == 2:
            base_action = [0, 1]
        elif action == 3:
            base_action = [-1, 0]
        elif action == 4:
            base_action = [1, 0]
        dist = self.fms.unit/self.fms.split
        self.fms.canvas.move(self.Show, base_action[0]*dist
                             , base_action[1]*dist)
        self.fms.canvas.move(self.show, base_action[0]*dist
                             , base_action[1]*dist)
        self.fms.window.update()
                

        
        
class Charging(object):
    def __init__(self, env, fms, x, y):
        self.env = env
        self.fms = fms
        self.x = x
        self.y = y
        #self.resource = simpy.Resource(self.env, 10)
        self.fms.mesh[self.x][self.y]  = simpy.Resource(self.env, 10)
        
        #image
        #'''
        p = [(self.fms.Origin[0]+self.x)*self.fms.unit, (self.fms.Origin[1]+self.fms.Hight-self.y)*self.fms.unit]
        p1 = [(self.fms.Origin[0]-0.7+self.x)*self.fms.unit, (self.fms.Origin[1]+self.fms.Hight-0.7-self.y)*self.fms.unit]
        p2 = [(self.fms.Origin[0]+0.7+self.x)*self.fms.unit, (self.fms.Origin[1]+self.fms.Hight+0.7-self.y)*self.fms.unit]
        self.Show = self.fms.canvas.create_oval(p1[0], p1[1], p2[0], p2[1], fill = "light blue")
        self.show = self.fms.canvas.create_text(p[0], p[1], text = "C", font = ("arial", 10), fill = "purple")
        #'''
        

                
class FMS(object):
    def __init__(self, env, x, y, WS_num, connect):
        self.env = env
        self.connect = connect
        self.Time = 0
        self.AGVs = []
        self.stations = []
        self.Jobs = []
        self.WS_num = WS_num
        self.x = x
        self.y = y
        self.job_cnt = 0
        
        self.newID = 0
        
        PD = [[9, 8], [5, 2], [8, 2], [13, 4], [13, 7], [13, 10], [3, 13], [6, 13], [9, 13], [4, 8]]
        self.BLOCK = []
        for i in range(len(PD)):
            block = PD[i]
            if i == 0 or i == 1 or i == 2 or i == 9:
                block[1] -= 1
                self.BLOCK.append(block)
                self.BLOCK.append([block[0] - 1, block[1] - 1])
                self.BLOCK.append([block[0] - 1, block[1]])
                self.BLOCK.append([block[0], block[1] - 1])
                self.BLOCK.append([block[0] + 1, block[1] - 1])
                self.BLOCK.append([block[0] + 1, block[1]])
            elif i == 6 or i == 7 or i == 8:
                block[1] += 2
                self.BLOCK.append(block)
                self.BLOCK.append([block[0] - 1, block[1] - 1])
                self.BLOCK.append([block[0] - 1, block[1]])
                self.BLOCK.append([block[0], block[1] - 1])
                self.BLOCK.append([block[0] + 1, block[1] - 1])
                self.BLOCK.append([block[0] + 1, block[1]])
            else:
                block[0] += 1
                self.BLOCK.append(block)
                self.BLOCK.append([block[0], block[1] - 1])
                self.BLOCK.append([block[0], block[1] + 1])
                self.BLOCK.append([block[0] + 1, block[1] - 1])
                self.BLOCK.append([block[0] + 1, block[1]])
                self.BLOCK.append([block[0] + 1, block[1] + 1])
        
        
        self.mesh = self.create_path(self.env, x, y, 1, self.BLOCK)
        self.speed = 10
        self.env.process(self.TimeCount())
        self.env.process(self.Job_arrive())
        
        ###
        self.Hight = self.y-1
        self.Width = self.x-1
        self.unit = 40
        self.Origin = [3, 2]
        self.split = 5
        
        self.BuildFloor()
        self.Create_Stations()
        
        self.Cstation = Charging(self.env, self, x=0, y=10)
        

    def create_path(self, env, x, y, Capacity, block):
        mesh = []
        for i in range(y):
            temp = []
            for j in range(x):
                if [i, j] in block:
                    a = simpy.Resource(env, 1)
                    temp.append(a)
                    a.request()
                elif [i, j] in [[9, 8], [5, 2], [8, 2], [13, 4], [13, 7], [13, 10], [3, 13], [6, 13], [9, 13], [4, 8], [0, 1], [0, 2]]:
                    a = simpy.Resource(env, 1)
                    temp.append(a)
                else:
                    temp.append(simpy.Resource(env, Capacity))
            mesh.append(temp)
        return mesh

    
    def TimeCount(self):
        yield self.env.timeout(0)
        self.Time = 0
        while True > 0:
            if round(self.Time) % 100 == 0:
                msg = pickle.dumps([0, "TimeCount", self.Time])
                self.connect.send(msg)
            if self.newID != 0:
                Vehicle(self.env, self, self.mesh, self.newID, 0, 10, self.connect)
                self.newID = 0
            '''
            yield self.env.timeout(1)
            self.Time += 1
            '''
            self.canvas.delete(self.time)
            self.canvas.delete(self.arr_show)
            self.canvas.delete(self.finish_show)
            p = [1.5*self.unit, (self.Origin[1]+self.Hight*3/4+1)*self.unit]
            self.arr_show = self.canvas.create_text(p[0]+0.5*self.unit, p[1]+0.5*self.unit, text = str(len(self.stations[0].out_queue))
                                , font = ("arial", 12), fill = "black")
            self.finish_show = self.canvas.create_text(p[0]+0.5*self.unit, p[1]+self.unit, text = str(len(self.stations[11].out_queue))
                                , font = ("arial", 12), fill = "black")
                
            self.TIME = self.canvas.create_text(self.unit\
                                            , 0.5*self.unit, text = "Time:"\
                                            , font = ("arial", 20)\
                                            , fill = "Blue")
            self.time = self.canvas.create_text(2.5*self.unit\
                                            , 0.5*self.unit, text = str(round(self.Time))\
                                            , font = ("arial", 20)\
                                            , fill = "Blue")
            
            for i in range(self.split):
                    
                yield self.env.timeout(1/self.split)
                self.canvas.update()
                self.Time += 1/self.split
                if self.speed < 50:
                    time.sleep(1/(self.split*self.speed))

    def Create_Stations(self):
        for i in range(self.WS_num):
            Station(self.env, self, i)
            
    def Job_arrive(self):
        
        while True:
            inter_arrival = np.random.exponential(170)
                
            yield self.env.timeout(inter_arrival)
            self.job_cnt += 1
            Job(self.env, self, self.job_cnt, self.connect)
            
    def BuildFloor(self):
        
        self.window = tk.Tk()
        
        self.window.title("Flexible Manufacturing System")
        self.window.geometry("{1}x{1}".format((self.Hight+4)*self.unit
                      , (self.Width+5)*self.unit))
        self.canvas = tk.Canvas(bg = "white", height = (self.Hight+5)\
                *self.unit, width = (self.Width+5)*self.unit)

        #Grid Layout
        for c in range(0, (self.Width*self.unit+1), self.unit):
            x0, y0, x1, y1 = self.Origin[0]*self.unit+c, self.Origin[1]*self.unit\
                    , self.Origin[0]*self.unit+c, (self.Hight+self.Origin[1])\
                    *self.unit
            self.canvas.create_line(x0, y0, x1, y1)

        for r in range(0, (self.Hight*self.unit+1), self.unit):
            x0, y0, x1, y1 = self\
                    .Origin[0]*self.unit, self.Origin[1]*self.unit+r\
                    , (self.Width+self.Origin[0])*self.unit\
                    , self.Origin[1]*self.unit+r
            self.canvas.create_line(x0, y0, x1, y1)

        #Loading Point
        L = [[0, 2]]
        for i in range(len(L)):
            p1 = [(self.Origin[0]+L[i][0])*self.unit-5, (self.Origin[1]+self.Hight-L[i][1])\
                  *self.unit-5]
            p2 = [(self.Origin[0]+L[i][0])*self.unit+5, (self.Origin[1]+self.Hight-L[i][1])\
                  *self.unit+5]
            self.canvas.create_oval(p1[0], p1[1], p2[0], p2[1], fill = "blue")
        #Unloading Point
        U = [[0, 1]]
        for i in range(len(U)):
            p1 = [(self.Origin[0]+U[i][0])*self.unit-5, (self.Origin[1]+self.Hight-U[i][1])\
                  *self.unit-5]
            p2 = [(self.Origin[0]+U[i][0])*self.unit+5, (self.Origin[1]+self.Hight-U[i][1])\
                  *self.unit+5]
            self.canvas.create_oval(p1[0], p1[1], p2[0], p2[1], fill = "green")
            
        #P/D Point
        PD = [[9, 8], [5, 2], [8, 2], [13, 4], [13, 7], [13, 10], [3, 13], [6, 13], [9, 13], [4, 8]]
        for i in range(len(PD)):
            p1 = [(self.Origin[0]+PD[i][0])*self.unit-5, (self.Origin[1]\
                  +self.Hight-PD[i][1])*self.unit-5]
            p2 = [(self.Origin[0]+PD[i][0])*self.unit+5, (self.Origin[1]\
                  +self.Hight-PD[i][1])*self.unit+5]
            self.canvas.create_oval(p1[0], p1[1], p2[0], p2[1], fill = "black")
            

        #AS/RS
        p = [1.5*self.unit, (self.Origin[1]+self.Hight*3/4+1)*self.unit]
        p1 = [2.5*self.unit, (self.Origin[1]+self.Hight*3/4+4)*self.unit]
        p2 = [0.5*self.unit, (self.Origin[1]+self.Hight*3/4-2)*self.unit]
        self.canvas.create_rectangle(p1[0], p1[1], p2[0], p2[1]\
                                     , fill = "yellow")
        self.canvas.create_text(p[0], p[1], text = "AS/RS"
                                , font = ("arial", 12), fill = "black")
        self.canvas.create_text(p[0]-0.4*self.unit, p[1]+0.5*self.unit, text = "Arrive:"
                                , font = ("arial", 12), fill = "black")
        self.canvas.create_text(p[0]-0.4*self.unit, p[1]+self.unit, text = "Finish:"
                                , font = ("arial", 12), fill = "black")
        
        self.arr_show = self.canvas.create_text(p[0]+0.5*self.unit, p[1]+0.5*self.unit, text = str(0)
                                , font = ("arial", 12), fill = "black")
        self.finish_show = self.canvas.create_text(p[0]+0.5*self.unit, p[1]+self.unit, text = str(0)
                                , font = ("arial", 12), fill = "black")

            
        self.time = self.canvas.create_text(2.5*self.unit\
                                            , 0.5*self.unit, text = ""\
                                            , font = ("arial", 20)\
                                            , fill = "Blue")

        
        self.canvas.pack()
        


