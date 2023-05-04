import sqlite3
from sqlite3 import Error
# from datetime import datetime

import datetime as dt
import json
import pickle
import base64
import time



class DataBase():

	def __init__(self):
		# self.user_auth_table = "user_auth"
		self.last_tstamp=dt.datetime.now()
		self.DBFILE = "application/pythonsqlite.db"
		self.TABLE='test'
		self.DASHBOARD_TABLE='dashborad'
		self.LOG_TABLE = "logs"
		# self.create_auth_table()
		return

	
	def create_connection(self,db_file):
		""" create a database connection to a SQLite database 
		"""

		conn = None
		try:
			conn = sqlite3.connect(db_file)
		except Error as e:
			print(e)
		
		self.db_file=db_file
		
		return conn


	def create_table_data(self,conn,tbl):
		""" create a table from the create_table_sql statement
		:param conn: Connection object
		:param create_table_sql: a CREATE TABLE statement
		:return:
		"""
		try:

			create_table_sql = """ CREATE TABLE IF NOT EXISTS {} (
										data text,
										timestamp datetime PRIMARY KEY
									); """.format(tbl)

			c = conn.cursor()
			c.execute(create_table_sql)
			self.tbl=tbl

		except Error as e:
			print(e)


	def insert_data(self,conn,data_raw,timestamp,tbl,encode=True):
		"""
		:param conn:
		:param data:
		:return:
		"""

		# self.last_tstamp=timestamp

		# print("innsert_data>>",data_raw, tbl)
		if(encode):
			data=base64.urlsafe_b64encode(json.dumps(data_raw).encode()).decode()#encode so it is not readable to some third party, and only accesible to us after decoding
		else:
			data=data_raw

		
		sql = ''' INSERT INTO {}(data,timestamp)
				VALUES(?,?) '''.format(tbl)
		cur = conn.cursor()
		# print(sql)
		# print("times tamp", timestamp)
		cur.execute(sql, (data,timestamp))
		conn.commit()
		# lstrow=
		# self.last_tstamp=timestamp
		return timestamp
	
	def get_data(self,conn,tbl,all_data=True,encode=True):
		"""
		:param conn:
		:param all_data:
		:return:
		"""
		# print("time: ",self.last_tstamp)

		sql = """SELECT data,timestamp FROM {} ORDER BY timestamp DESC""".format(tbl)
		

		# if(all_data):
		#     sql = """SELECT data,timestamp FROM {} ORDER BY timestamp DESC""".format(self.tbl)
		# else:
		#     sql = """SELECT data,timestamp FROM {} where timestamp >= ? ORDER BY timestamp DESC""".format(self.tbl)
		#     print(self.last_tstamp)
		# print(sql)
		# print(str(self.last_tstamp))
		cur = conn.cursor()
		d = cur.execute(sql)
		r = d.fetchall()#[0][0]
		data_filtered=[]
		if(len(r)>0):
			
			if len(r) > 0:
				for i in range(len(r)):
					# print(r[i])
					if(not all_data):
						# if(dt.datetime.strptime(r[i][1], '%Y-%M-%d %H:%M:%S %d %Y %I:%M%p')>self.last_tstamp):
						# s = 'datetime.datetime(2021, 9, 10, 10, 15, 0, 250362)'
						# dt = datetime.strptime(s,'datetime.datetime(%Y, %m, %d, %H, %M, %S, %f)')
						# print(dt)

						if self.last_tstamp!=None and (dt.datetime.strptime(r[i][1],'%Y-%m-%d %H:%M:%S.%f')>self.last_tstamp):
							if(encode):
								ret_data=json.loads(base64.urlsafe_b64decode(r[i][0].encode()).decode())
								ret_data["timestamp"]=r[i][1]
								data_filtered.append(ret_data)
							else:
								ret_data=r[i][0]
								ret_data["timestamp"]=r[i][1]
								data_filtered.append(ret_data)
					else:
						if(encode):
							try:
								ret_data=json.loads(base64.urlsafe_b64decode(r[i][0].encode()).decode())
								ret_data["timestamp"]=r[i][1]
								data_filtered.append(ret_data)
								# data_filtered.append(json.loads(base64.urlsafe_b64decode(r[i][0].encode()).decode()))
							except Exception as e:
								print("get data error msg: ",e)
						else:
							ret_data=r[i][0]
							ret_data["timestamp"]=r[i][1]
							data_filtered.append(ret_data)
				

			else:
				# print("No data found")
				data_filtered = 0
		else:
			# print("No data found")
			data_filtered=0

		try:
			self.last_tstamp=dt.datetime.strptime(r[0][1],'%Y-%m-%d %H:%M:%S.%f')
		except:
			pass

		return data_filtered
	
	def delete_data(self,conn,days=None,vacuum=True):
		"""
		conn(obj) : connection object to the db
		tbl(str) : name of the table to insert data to
		days(int) : number of days old data that needs to be deleted
		vacuum(bool,default=True) : set to run a vacuum command as well 
		"""

		if(days is not None):
			today = dt.date.today()
			ndays_ago = today - dt.timedelta(days=days)
			sql="""DELETE FROM {} WHERE timestamp LIKE \"{}%%\" """.format(self.tbl,ndays_ago)
		else:
			sql="""DELETE FROM {} """.format(self.tbl)
		
		print(sql)
		cur = conn.cursor()
		d = cur.execute(sql)
		conn.commit()
		if(vacuum):
			self.vacuum_db(conn)
		return

	def vacuum_db(self,conn):

		sql="""VACUUM"""
		# print(sql)
		conn.execute(sql)

		return

	