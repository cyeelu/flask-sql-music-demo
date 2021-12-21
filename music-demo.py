from flask import Flask,render_template,request
from pandas.core.indexes.api import union_indexes
import mysql.connector
import pandas as pd

app = Flask(__name__)

#輸入頁
@app.route('/')
def index():
	uniques = get_unique()
	return render_template('index.html',uniques = uniques)

#執行輸出
@app.route('/output',methods = ['POST','GET'])
def output():
	if request.method == 'POST':
		#偷看得到的條件內容
		print(request.form)
		#偷看得到的結果
		print(select_sql(request.form)) 

		#以下是要把得到的結果轉成output.html_未完成
		input_data = select_sql(request.form)
		raw_data = {"卡司符合數": [input_data[x][0] for x in range(len(input_data))],"音樂祭名稱": [input_data[x][1] for x in range(len(input_data))], 
					"開演日期": [input_data[x][2] for x in range(len(input_data))], 
					"地區": [input_data[x][3] for x in range(len(input_data))], 
					"票價": [input_data[x][4] for x in range(len(input_data))], 
					"售票系統": [input_data[x][5] for x in range(len(input_data))]}
		my_dataframe = pd.DataFrame(raw_data)
		output.html = pd.DataFrame.to_html(my_dataframe, index=False)
		return render_template('output.html')  

#獲得所有樂團名稱
def get_unique():
	mydb = mysql.connector.connect(
		user="root", password="Ccclub_2021_testmysql",
		host="localhost", database="pyproject")

	mycursor = mydb.cursor()

	mycursor.execute("SELECT * FROM pyproject.py_demo")
	myresult = mycursor.fetchall()
    
	unique_name=[]
	for i in range(len(myresult)):
		unique_name.append((myresult[i])[2])
    
	return sorted(set(unique_name))

#表單輸入內容轉為sql指令
def select_sql(conditiondic):
	mydb = mysql.connector.connect(
		user="user", password="password",
		host="localhost", database="dbname"
		)
	#user、password、database改為本地的mysql資料

	mycursor = mydb.cursor()

	condition_query = []
	condition_query_player = []
	for key, value in conditiondic.items():
		for i in ['player_name0','player_name1','player_name2','player_name3','player_name4']:
			if key == i and value:
				condition_query_player.append(f'player_name={value}')
		if key == 'date_1' and value :
			condition_query.append(f'start_date>="{value}"')
		if key == 'date_2' and value :
			condition_query.append(f'start_date <="{value}"')
		if key == 'price' and value != 'default' :
			if value == '1000' :
				condition_query.append(f'price <= 1000')
			if value == '2000' :
				condition_query.append(f'price >= 1000 AND price <= 3000 ')
			if value == '3000' :
				condition_query.append(f'price >= 3000')
		if key == 'area':
			if value and value != 'default':
				condition_query.append(f'{key}="{value}"')
	if condition_query and condition_query_player :
		condition_query_player = ' or '.join(condition_query_player)
		condition_query_player = "(" + condition_query_player + ")"
		condition_query = "WHERE " + ' AND '.join(condition_query) + ' AND ' + str(condition_query_player)
	elif condition_query :
		condition_query = "WHERE " + ' AND '.join(condition_query)
	elif condition_query_player :
		condition_query_player = ' or '.join(condition_query_player)
		condition_query_player = "(" + condition_query_player + ")"
		condition_query = "WHERE " + str(condition_query_player)
	else:
		condition_query = ''

	postgres_select_query = f"""SELECT * FROM pyproject.py_demo {condition_query} ORDER BY task_id;"""
	print(postgres_select_query)
	mycursor.execute(postgres_select_query)

	table = []
	while True:
		temp = mycursor.fetchall()

		if temp:
			table.extend(temp)
		else:
			break
	mycursor.close()
	return table


        
if __name__ == '__main__':
	app.run(host='0.0.0.0', port='7000', debug=True)
