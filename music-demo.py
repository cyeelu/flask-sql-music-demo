from flask import Flask,render_template,request
import mysql.connector

app = Flask(__name__)

#輸入頁
@app.route('/')
def index():
	return render_template('index.html')

#執行輸出
@app.route('/output',methods = ['POST','GET'])
def output():
	if request.method == 'POST':
		print(select_sql(request.form))
		sql_result = select_sql(request.form)  
		
		#以下output.html未完成，要用jinja2把拿到的list變成變數丟到output.html中
		return render_template('output.html',html_show=sql_result)  

#表單輸入內容轉為sql指令
def select_sql(conditiondic):
	mydb = mysql.connector.connect(
		user="user", password="password",
		host="localhost", database="dbname"
		)
	#user、password、database改為本地的mysql資料

	mycursor = mydb.cursor()

	condition_query = []
	for key, value in conditiondic.items():
		if value:
			condition_query.append(f'{key}="{value}"')
	if condition_query:
		condition_query = "WHERE " + ' AND '.join(condition_query)
	else:
		condition_query = ''
	
	postgres_select_query = f"""SELECT * FROM pyproject.py_demo {condition_query} ORDER BY task_id;"""
	#pyproject.py_demoe改為本地的mysql_db名稱

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