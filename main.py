from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import MySQLdb as mysql

CHROME_PATH = './chromedriver'
URL = 'http://tereshkova.test.kavichki.com/'
HOST_DB = 'localhost'
USER_DB = 'USER'
PASSWD_US = 'PASSWORD'
NAME_DB = 'test'
TABLE_NM = 'test_table'

def create_table(cur, TABLE_NM):
	result_table = cur.execute('SELECT table_name FROM information_schema.tables WHERE table_schema = "' + NAME_DB + '" AND table_name = "'+ TABLE_NM +'";')
	value = header[0] +' varchar(250), ' + header[1] + ' int , ' + header[2] +' int );'
	if result_table == 0:
		cur.execute('CREATE TABLE IF NOT EXISTS ' + TABLE_NM + '( ' + value)
		return 0
	else:
		cur.execute('DROP TABLE '+TABLE_NM+';')
		create_table(cur, TABLE_NM)

def web_table(driver):
	tbody = driver.find_elements_by_xpath('//tbody/tr/td')
	table_new= []
	i=1
	for x in range(len(tbody)):
		if (i%4) != 0 or x==0: 
			table_new.append(tbody[x].text)
			i+=1 
		else:
			i+=1
	return (table_new)

def insert_value(tbody, TABLE_NM):
	k = 1
	while k<len(tbody):
		cur.execute("INSERT INTO "+ TABLE_NM + " VALUES (' " + tbody[k-1] +"',"+tbody[k] +","+tbody[k+1]  + " );")
		k+=3
	conn.commit()
	return 1

def add_site(test_value, driver):
	button_open = driver.find_element(By.XPATH, '//a[@id="open"]')
	button_open.click()
	name_item = driver.find_element(By.XPATH, '//input[@id="name"]')
	count_item = driver.find_element(By.XPATH, '//input[@id="count"]')
	price_item = driver.find_element(By.XPATH, '//input[@id="price"]')
	i = 0
	for x in range(int(len(test_value)/3)):
		name_item.clear()
		count_item.clear()
		price_item.clear()
		name_item.send_keys(test_value[i]);
		count_item.send_keys(test_value[i+1]);
		price_item.send_keys(test_value[i+2]);
		button_add = driver.find_element(By.XPATH, '//input[@id="add"]')
		button_add.click()
		i+=3

driver = webdriver.Chrome(CHROME_PATH )

driver.get(URL)

# create head for table
header = driver.find_elements_by_class_name("header")
for items in range(len(header)):
	header[items] = header[items].text
	header[items] = header[items].replace(' ' , '_')
	header[items] = header[items].replace(',', '')


# create database and table
conn = mysql.connect(HOST_DB, USER_DB, PASSWD_US) 
cur = conn.cursor()

sql = 'CREATE DATABASE IF NOT EXISTS '+ NAME_DB
cur.execute(sql)

cur.execute('use ' + NAME_DB)
conn.set_character_set('utf8')
create_table(cur, TABLE_NM)
table_value = web_table(driver)
test_value = ('Чашечки для век', '20', '100', 'Новое масло', '50', '300')
table_value.extend(test_value)
insert_value(table_value, TABLE_NM)

#add values in site
add_site(test_value, driver)

# insert new values in table
create_table(cur, TABLE_NM+'2')
table_value = web_table(driver)
insert_value(table_value, TABLE_NM+'2')
driver.quit()

query = ('select * from '+ TABLE_NM 
	+' natural left join '+ TABLE_NM +'2 '
	+ ' where ' + TABLE_NM+'2.'+header[0] + " is NULL" 
	+ ' union select * from ' + TABLE_NM 
	+' natural right join '+ TABLE_NM + '2 '
	+ ' where '+ TABLE_NM + '.'+ header[0] + ' is null;')
cur.execute(query)
output = cur.fetchall()

for row in output:
 	print (row)

# close db 
cur.close()
conn.close()
