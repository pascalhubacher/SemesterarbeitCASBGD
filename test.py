from datetime import datetime, timedelta

date_time_str = '2018-06-29 08:15:00'
date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')
print(date_time_obj)

date_time_str2 = int('20000')/1000

timedelta1 = timedelta(seconds=int('20000')/1000)

print(timedelta1)
#date_time_obj2 = datetime.datetime.fromtimestamp(date_time_str2)

date_time_obj += timedelta1
print(date_time_obj.strftime("%Y.%m.%d %H:%M:%S.%f"))



#print(date_time_obj + date_time_obj2)

#date_time_obj = datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')