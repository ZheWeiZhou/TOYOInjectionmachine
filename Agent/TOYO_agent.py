from pprint import pprint
import os
import json
import time
class toyoagent:
    def __init__(self,spc_path):
        self.previous_count = -1
        self.spc_path       = spc_path
    def send_monitor_command(self):
        os.system('copy "SESS0000.REQ" "Session\SESS0000.REQ"')
    def get_machine_data(self):
        data = {
                    "date":'',
                    "time":'',
                    "Actmach":'',
                    "Ijv_set1":'',
                    "Ijv_set2":'',
                    "Ijv_set3":'',
                    "Ijv_set4":'',
                    "Ijv_set5":'',
                    "Ijv_set6":'',
                    "Ijv_set7":'',
                    "IJPressure_set":'',
                    "VP_pos_set":'',
                    "Act_VP_pressure":'',
                    "Act_VP_pos":'',
                    "Act_filling_time":'',
                    "IJ_pos_set1":'',
                    "IJ_pos_set2":'',
                    "IJ_pos_set3":'',
                    "IJ_pos_set4":'',
                    "IJ_pos_set5":'',
                    "IJ_pos_set6":'',
                    "Barrel_temp_set1":'',
                    "Barrel_temp_set2":'',
                    "Barrel_temp_set3":'',
                    "Barrel_temp_set4":'',
                    "Barrel_temp_set5":'',
                    "Barrel_temp_set16":'',
                    "Act_Barrel_temp1":'',
                    "Act_Barrel_temp2":'',
                    "Act_Barrel_temp3":'',
                    "Act_Barrel_temp4":'',
                    "Act_Barrel_temp5":'',
                    "Act_Barrel_temp6":'',
                    "Act_Cushion_pos":'',
                    "Ij_Start_pos":'',
                    "Clamping_force_set":'',
                    "Cooling_time_set":'',
                    "Max_ij_pressure":'',
                    "Max_ij_speed":'',
                    "Holding_time_set1":'',
                    "Holding_time_set2":'',
                    "Holding_time_set3":'',
                    "Holding_time_set4":'',
                    "Holding_time_set5":'',
                    "Holding_time_set6":'',
                    "Holding_pressure_set1":'',
                    "Holding_pressure_set2":'',
                    "Holding_pressure_set3":'',
                    "Holding_pressure_set4":'',
                    "Holding_pressure_set5":'',
                    "Holding_pressure_set6":'',
                    "Act_ij_speed1":'',
                    "Act_ij_speed2":'',
                    "Act_ij_speed3":'',
                    "Act_ij_speed4":'',
                    "Act_ij_speed5":'',
                    "Act_ij_speed6":'',
                    "Act_ij_speed7":'',
                    "Act_ij_pressure1":'',
                    "Act_ij_pressure2":'',
                    "Act_ij_pressure3":'',
                    "Act_ij_pressure4":'',
                    "Act_ij_pressure5":'',
                    "Act_ij_pressure6":'',
                    "Act_ij_pressure7":'',
                    "Min_ij_pressure":'',
                    "Min_ij_speed":'',
                    "cycle_count":'',
                }
        try:
            content = 0
            with open(self.spc_path,'r') as file:
                content     = file.readlines()
                lastline    = content[-1].strip()
                machinedata = [s.strip() for s in lastline.split(',') ]
                keylist  = list(data.keys())
                for i in range(len(machinedata)):
                    keyname       = keylist[i]
                    data[keyname] = machinedata[i]
            vpset = float(data["VP_pos_set"])
            origin_pos_set = [float(data["Ij_Start_pos"]),float(data["IJ_pos_set1"]),float(data["IJ_pos_set2"]),float(data["IJ_pos_set3"]),float(data["IJ_pos_set4"]),float(data["IJ_pos_set5"]),float(data["IJ_pos_set6"])]
            origin_ijv_set = [float(data["Ijv_set1"]),float(data["Ijv_set2"]),float(data["Ijv_set3"]),float(data["Ijv_set4"]),float(data["Ijv_set5"]),float(data["Ijv_set6"]),float(data["Ijv_set7"]),]
            segcount =0
            def mask_array(arr,index,value):
                return [arr[i] if i <index else value for i in range(len(arr))]
            for i in range(len(origin_pos_set)):
                if origin_pos_set[i] == vpset:
                    segcount = i
            newpos = mask_array(origin_pos_set,segcount,origin_pos_set[segcount])
            new_ijv_set = mask_array(origin_ijv_set,segcount,0)
            data["IJ_pos_set1"] = newpos[1]
            data["IJ_pos_set2"] = newpos[2]
            data["IJ_pos_set3"] = newpos[3]
            data["IJ_pos_set4"] = newpos[4]
            data["IJ_pos_set5"] = newpos[5]
            data["IJ_pos_set6"] = newpos[6]
            data["Ijv_set1"]    = new_ijv_set[0]
            data["Ijv_set2"]    = new_ijv_set[1]
            data["Ijv_set3"]    = new_ijv_set[2]
            data["Ijv_set4"]    = new_ijv_set[3]
            data["Ijv_set5"]    = new_ijv_set[4]
            data["Ijv_set6"]    = new_ijv_set[5]
            data["Ijv_set7"]    = new_ijv_set[6]

            # Clean spc.dat per hour
            if len(content) > 3600:
                print("[Message] Detect SPC file row number exceed maximunm limit")
                os.remove(self.spc_path)
                time.sleep(2)
        except Exception as e:
            print(f"[Error] Get Data Fail Reason : {e}")
            pass
        return data
    def collectdata(self):

        machinedata = self.get_machine_data()
        pprint(machinedata)
        try:
            currentcount = int(machinedata['cycle_count'])
            # upload machine real-time data to redis
            print("[Message] Upload realtime data to redis ... ")
            packing_machinedata = json.dumps(machinedata)
            if self.previous_count < 0:
                self.previous_count = int(machinedata['cycle_count'])
            else:
                # Determine whether data needs to be uploaded to the database.
                if self.previous_count != currentcount:
                    print("[Message] Detect machine completed the process, Start to upload data to db ... ")
                    self.previous_count=currentcount
        except Exception as e:
            print(f"[Error] Collect data process crash ... Reason {e}")
            pass
            
if __name__ == "__main__":
    agent       = toyoagent('data/spc.dat')
    agent.send_monitor_command()
    while True:
        agent.collectdata()
        time.sleep(1)
