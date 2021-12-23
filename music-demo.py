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
		#偷看得到的條件內容_正式要刪掉
		print(request.form)
		
		#偷看sql得到的結果_正式要刪掉
		print(select_sql(request.form))
		
		#偷看要傳到output的東西_正式要刪掉
		print(sql_turn_out(select_sql(request.form)))
		#例如條件輸入=1976,9m88,Crispy脆樂團,滅火器，輸出為下(可以用來當測資)
		#[[['9m88', 'Crispy脆樂團', '1976'], '貴人散步', datetime.date(2021, 11, 25), 688, '南部', '台南', 'kktix', ''], 
		[['滅火器', '9m88'], '大港開唱', datetime.date(2021, 3, 27), 2500, '南部', '高雄', 'indievox', ''], 
		[['滅火器', '1976'], '爛泥發芽', datetime.date(2022, 1, 1), 800, '北部', '台北', 'indievox', '']]
		
		#以下是要把得到的結果output_data輸出到output.html_未完成
		output_data = sql_turn_out(select_sql(request.form))

		return render_template('output.html')

#獲得所有表演者名稱,傳到前端表演者選擇欄位
def get_unique():
	mydb = mysql.connector.connect(
		user="user", password="password",
		host="localhost", database="dbname"
		)
	#user、password、database改為本地的mysql資料

	mycursor = mydb.cursor()

	mycursor.execute("SELECT * FROM pyproject.py_demo") #pyproject.py_demo改成本地mysql的db名稱
	myresult = mycursor.fetchall()
    
	unique_name=[]
	for i in range(len(myresult)):
		unique_name.append((myresult[i])[2])
    
	return sorted(set(unique_name))

#表單輸入內容轉為sql指令+輸出選擇結果
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
	#pyproject.py_demo改成本地mysql的db名稱
	
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

#sql選擇結果轉成輸出結果
def sql_turn_out(lst):
	lst_new = [1]
	lst_clear = []
	fes_player_dic = dict()
	for i in lst:
		i = list(i)
		if i[1] in fes_player_dic:
			fes_player_dic[i[1]].append(i[2])
		else:
			fes_player_dic[i[1]] = [i[2]]
		i.pop(0)
		i.pop(1)
		lst_new.append(i)
	for i in range(len(lst_new)) :
		if lst_new[i] == lst_new[i-1] :
			lst_clear = lst_clear
		else:
			lst_clear.append(lst_new[i])
	lst_clear.pop(0)
	for i in lst_clear:
		i.insert(0,fes_player_dic[i[0]])
	return sorted(lst_clear,reverse=True,key = lambda i:(len(i[0]),i[3]))

        
if __name__ == '__main__':
	app.run(host='0.0.0.0', port='7000', debug=True)
