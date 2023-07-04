import os
import openai
from fastapi import FastAPI
import pandas as pd
from openpyxl import load_workbook
import socket
import sqlalchemy as db
from sqlalchemy.sql import text
from datetime import datetime
from sqlalchemy import create_engine, text
import psycopg2

app = FastAPI()


user_host_name = socket.gethostname()
# openai.api_key = os.getenv("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")
openai.api_key = "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"

# dataframe1 = pd.read_excel('Book1.xlsx')
# context=dataframe1
# print(context)
@app.post("/openai_chatgpt/User host name :"+user_host_name+"")
def openai_chatgpt_chat(question):
      workbook = load_workbook('context_to_chatgpt.xlsx')
      worksheet = workbook['common_sense']
      cell_value = worksheet['A1'].value
      context=cell_value
      
      worksheet = workbook['token_cost_cal']
      cell_value1 = worksheet['A2'].value
      last_total_token = (cell_value1)
      
      cell_value2 = worksheet['B2'].value
      last_total_token_cost = (cell_value2)
      #print(context)
      #res = sum(not chr.isspace() for chr in context)
      #print(str(res))
      context_token = (len(context)/3)
      context_token_cost = ((context_token/1000)*0.0015)
      
      response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
            {"role": "assistant", "content": context},
            {"role": "user", "content": question}
        ]
      )
      output_token = (len(response.choices[0].message.content)/3)
      output_token_cost = (((output_token)/1000)*0.002)
      token = (context_token + output_token)
      cost = (context_token_cost + output_token_cost)
      
      last_total_token_final = (last_total_token + token)  
      last_total_token_cost_final = (last_total_token_cost + cost)

      workbook['token_cost_cal']['A2'] = last_total_token_final
      workbook['token_cost_cal']['B2'] = last_total_token_cost_final
      workbook.save('context_to_chatgpt.xlsx')
      dt=datetime.now()
      department = "IT Innovation"
      token1=float(token)
      cost1=float(cost)

      try:
            connection = psycopg2.connect(user="postgres",
                                          password="Postgre_15",
                                          host="localhost",
                                          port="5432",
                                          database="openai_chatgpt")
            cursor = connection.cursor()
      
            postgres_insert_query = """ insert into user_history(date_time,emp_id,c_token,c_cost) Values(%s,%s,%s,%s)"""
            record_to_insert = (dt,user_host_name,token,cost)
            print(postgres_insert_query)
            print(record_to_insert)
            cursor.execute(postgres_insert_query, record_to_insert)
            
            connection.commit()
            count = cursor.rowcount
            print(count, "Record inserted successfully into user_history table")

      except (Exception, psycopg2.Error) as error:
            print("Failed to insert record into user_history table", error)

      finally:
    # closing database connection.
            if connection:
                  cursor.close()
                  connection.close()
                  print("PostgreSQL connection is closed")
      #engine = db.create_engine('postgresql://postgres:Postgre_15@localhost:5432/openai_chatgpt')
      #query = text(f"insert into public.user_history(date_time,emp_id,c_token,c_cost,dept) Values(('{dt}'),('{user_host_name}'),({token}),({cost}),('{department}'))")
      # query = text("insert into public.user_history(date_time,emp_id,c_token,c_cost,dept) Values(:date_time, :emp_id, :c_token, :c_cost, :dept)")
      # params = {
      #      'date_time': dt,
      #      'emp_id': user_host_name,
      #      'c_token': last_total_token_final,
      #      'c_cost': last_total_token_cost_final,
      #      'dept': department
      #}
      #with engine.connect() as conn:
      #      conn.execute(query, params)
      #print(query,params)  
      #with engine.connect() as conn:
      #      conn.execute(query)
      #      print(query)
      return response.choices[0].message.content, 'User id: ', user_host_name, 'Current Tokens: ', token , 'Current Cost in $: ', cost, 'Total Tokens:', (last_total_token_final), 'Total Cost in $ :', (last_total_token_cost_final)

