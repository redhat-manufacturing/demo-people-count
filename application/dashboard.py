import json
import pandas as pd
import datetime
import time
from sqlitedb import DataBase

class DashboardData:
    def __init__(self):
        DB = DataBase() 
        conn = DB.create_connection(DB.DBFILE)
        self.data=DB.get_data(conn,DB.TABLE)
        self.data_df=self.convert_json_to_pandas(self.data)
        self.today_date = datetime.datetime.now().date()
        self.yday_date = ((datetime.datetime.now() - datetime.timedelta(days=1))).date()
        self.today_data=self.get_x_day_data(self.data_df,self.today_date)
        self.yday_data=self.get_x_day_data(self.data_df,self.yday_date)
        self.week={0:"mon",1:"tue",2:"wed",3:"thu",4:"fri",5:"sat",6:"sun"}
        self.today_day= self.which_day(self.today_date)

    def convert_json_to_pandas(self,data):
        df={
            "enter":[],
            "leave":[],
            "timestamp":[],
            "tracker_id":[],
            "people_enter_ids":[],
            "people_leave_ids":[]
        }
        for d in data:
            if "people_enter_ids" not in d:
                continue
            df["enter"].append(d["people_count"]["enter"])
            df["leave"].append(d["people_count"]["leave"])
            df["timestamp"].append(d["timestamp"])
            df["tracker_id"].append(d["tracker IDS"])
            df["people_enter_ids"].append(d["people_enter_ids"])
            df["people_leave_ids"].append(d["people_leave_ids"])

        data_df = pd.DataFrame(df)
        data_df["timestamp"] = pd.to_datetime(data_df["timestamp"])
        data_df["enter_count"]=data_df["people_enter_ids"].apply(len)
        data_df["leave_count"]=data_df["people_leave_ids"].apply(len)
        return data_df


    def which_day(self,date):
      return date.weekday()

    def last_x_day_data(self,data_df,x):
        last_x_days_data_df=data_df[data_df["timestamp"].dt.date >= (datetime.datetime.now().date() - datetime.timedelta(days=x))]
        last_x_days_data_df=last_x_days_data_df[last_x_days_data_df["timestamp"].dt.date != datetime.datetime.now().date() ]
        return last_x_days_data_df


    def get_x_day_data(self,data_df,date):
        day_data=data_df[data_df["timestamp"].dt.date.apply(str)==str(date)]
        return day_data

    def hourly_average(self,x_day_data):
        day_hourly_group=x_day_data.groupby([x_day_data["timestamp"].dt.hour,x_day_data["timestamp"].dt.date])[["enter_count","leave_count"]].sum()
        day_hourly_group_avg=day_hourly_group.groupby(["timestamp"]).mean()
        return day_hourly_group_avg
    
    def hourly_count(self,x_day_data):
        day_hourly_group_count=x_day_data.groupby([x_day_data["timestamp"].dt.hour])[["enter_count","leave_count"]].sum()
        return day_hourly_group_count

    def add_missing_hours(self,hourly_avg):
        data_dict={}
        for i in range(24):
            if i not in hourly_avg.index:
                data_dict[i]={}
                data_dict[i]["enter_count"]=0
                data_dict[i]["leave_count"]=0
            else:
                data_dict[i]={}
                data_dict[i]["enter_count"]=hourly_avg.loc[i]["enter_count"]
                data_dict[i]["leave_count"]=hourly_avg.loc[i]["leave_count"]

        total_hourly_avg = pd.DataFrame.from_dict(data_dict,orient="index")
        return total_hourly_avg

    def last_x_days_lineplot(self):
        last_day_data=self.last_x_day_data(self.data_df,1)
        last_7_day_data=self.last_x_day_data(self.data_df,7)
        last_30_day_data=self.last_x_day_data(self.data_df,30)

        last_day_hourly_average=self.hourly_average(last_day_data)
        last_7_day_hourly_average=self.hourly_average(last_7_day_data)
        last_30_day_hourly_average=self.hourly_average(last_30_day_data)

        last_day_total_hourly_avg = self.add_missing_hours(last_day_hourly_average)
        last_7_day_total_hourly_avg = self.add_missing_hours(last_day_hourly_average)
        last_30_day_total_hourly_avg = self.add_missing_hours(last_day_hourly_average)
        
        data_dict_lineplot={
            "yesterday": {
                "labels" : list(last_day_total_hourly_avg.index),
                "data":[
                {"name":"Enter count","data": list(last_day_total_hourly_avg["enter_count"].astype("int"))},
                {"name":"Exit count","data": list(last_day_total_hourly_avg["leave_count"].astype("int"))}
                ],
            },
            "last_7_days": {
                "labels" : list(last_7_day_total_hourly_avg.index),
                "data":[
                {"name":"Enter count","data": list(last_7_day_total_hourly_avg["enter_count"].astype("int"))},
                {"name":"Exit count","data": list(last_7_day_total_hourly_avg["leave_count"].astype("int"))}
                ],
            },
            "last_30_days": {
                "labels" : list(last_30_day_total_hourly_avg.index),
                "data":[
                {"name":"Enter count","data": list(last_30_day_total_hourly_avg["enter_count"].astype("int"))},
                {"name":"Exit count","data": list(last_30_day_total_hourly_avg["leave_count"].astype("int"))}
                ],
            }
        }
        return data_dict_lineplot

    def yday_today_barplot(self):
        today_hourly_count_data = self.add_missing_hours(self.hourly_count(self.today_data))
        yday_hourly_count_data = self.add_missing_hours(self.hourly_count(self.yday_data))
        
        today_hourly_count = list(today_hourly_count_data["enter_count"].astype("int"))
        yday_hourly_count = list(yday_hourly_count_data["enter_count"].astype("int"))
        data_dict_barplot={
            "data":[{"data": today_hourly_count,"name":"Today"},
                    {"data":yday_hourly_count,"name":"Yesterday"}],
            "labels":list(range(0,24)),
            
        }
        return data_dict_barplot
    
    def busy_day(self):
        last_7_day_data=self.last_x_day_data(self.data_df,7)
        busy_day = last_7_day_data.groupby([last_7_day_data["timestamp"].dt.date])[["enter_count"]].sum()   
        busy_day_sorted=busy_day.sort_values(by=['enter_count'],ascending=False)
        week = {0:"Monday",1:"Tuesday",2:"Wednesday",3:"Thursday",4:"Friday",5:"Saturday",6:"Sunday"}
        busy_day = week[busy_day_sorted.index[0].weekday()]
        busy_day_val = busy_day_sorted['enter_count'][0]
        return busy_day,busy_day_val

    def week_trend(self):
        last_7_day_data=self.data_df[self.data_df["timestamp"].dt.date > (datetime.datetime.now().date() - datetime.timedelta(days=7))]
        # last_7_day_data=self.last_x_day_data(self.data_df,7)
        last_7_group = last_7_day_data.groupby([last_7_day_data["timestamp"].dt.date,last_7_day_data["timestamp"].dt.hour])["enter_count"].sum()
        weekly_trends={}
        for _,i in self.week.items():
            weekly_trends[i]={}

        for i in last_7_group.index:
            week_day=i[0].weekday()
            weekly_trends[self.week[week_day]][i[1]]=last_7_group.loc[i]
        
        weekly_trends_dict={}
        for _,w in self.week.items():
            if w not in weekly_trends:
                weekly_trends_dict[w]={
                    "data":[{"data": [0 for _ in range(0,24)],"name":"Enter Count"}],
                    "labels":list(range(1,13))+list(range(1,13))
                }
            else:
                week_data_list=[]
                for h in range(24):
                    if h in weekly_trends[w]:
                        week_data_list.append(int(weekly_trends[w][h]))
                    else:
                        week_data_list.append(0)
                
                weekly_trends_dict[w]={
                    "data":[{"data": week_data_list,"name":"Enter Count"}],
                    "labels":list(range(1,13))+list(range(1,13))
                }
        return weekly_trends_dict

    def stats(self):
        total_in=self.today_data["enter_count"].sum()
        total_out=self.today_data["leave_count"].sum()
        yday_total_in=self.yday_data["enter_count"].sum()
        yday_total_out=self.yday_data["leave_count"].sum()
        in_diff=total_in-yday_total_in
        out_diff=total_out-yday_total_out
        stats_list=[]
        if in_diff>0:
          stats_list.append({"id":"IN",
                            "changes":int(in_diff),
                            "status":"POSITIVE",
                              "title":"COUNT (IN)",
                            "value":int(total_in)})
        else:
          stats_list.append({"id":"IN",
                            "changes":int(in_diff),
                            "status":"NEGATIVE",
                              "title":"COUNT (IN)",
                            "value":int(total_in)})

        if out_diff>0:
          stats_list.append({"id":"OUT",
                            "changes":int(out_diff),
                            "status":"POSITIVE",
                              "title":"COUNT (OUT)",
                            "value":int(total_out)})
        else:
          stats_list.append({"id":"OUT","changes":int(out_diff),
                            "status":"NEGATIVE",
                              "title":"COUNT (OUT)",
                            "value":int(total_out)})

        return stats_list

    def trend(self):
        sort_data = self.hourly_count(self.yday_data).sort_values(by=["enter_count"])
        peak_hour = int(sort_data.index[-1])
        low_hour = int(sort_data.index[0])
        if peak_hour==low_hour:
            low_hour='n/a'
        if peak_hour==0: 
            peak_hour=24
        
        peak_hour = f"{peak_hour:02d}:00"
        if low_hour!='n/a':
            low_hour=f"{low_hour:02d}:00"

        busy_day,busy_day_val = self.busy_day()
        trend_list=[]
        trend_list.append({"title":"PEAK HOURS","value" : peak_hour})
        trend_list.append({"title":"lOWEST HOURS","value":low_hour})
        trend_list.append({"title":"BUSY DAY","value":str(busy_day),"data":int(busy_day_val)})
        return trend_list

    def output(self):
        output_chart_dict = {}
        output_chart_dict["barchart"]=self.yday_today_barplot()
        output_chart_dict["linechart"]=self.last_x_days_lineplot()
        output_dict = {}
        output_dict["stats"] = self.stats()
        output_dict["trends"] = self.trend()
        output_dict["chart"] = output_chart_dict
        output_dict["weekly_trend"]=self.week_trend()
        return output_dict

    