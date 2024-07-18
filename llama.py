# from ctransformers import AutoModelForCausalLM
# from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
# import time
# import re
# import os
# from dotenv import load_dotenv

# nv_path = os.path.join(os.path.dirname(__file__), 'config', '.env')
# load_dotenv(dotenv_path=nv_path)

# class llm:
#     def __init__(self,model='',version=''):
#         self.model = model
#         self.version = version 
#         self.llm = ''
#         self.template = '''[INST] You are a professional SQL developer. Understand the question asked and return the most suitable query
#                             supported by SQLSERVER using the table : ""{schema}"". Always write sql server standard queries.
#                             Always wrap your code answer using ```. question: {prompt} [/INST]'''
        
#     def load_model(self):
#         try:
#             print(self.model, self.version) 
#             if self.model and self.version:
#                 self.llm = AutoModelForCausalLM.from_pretrained("chavinlo/alpaca-native", device_map='auto', load_in_8bit=True)

#             elif self.model:
#                 self.llm = AutoModelForCausalLM.from_pretrained("chavinlo/alpaca-native", device_map='auto', load_in_8bit=True)
#             else:
#                 raise Exception("You don't have a local model")
#             return llm_model
#         except Exception as e:
#             try:
#                 if self.model and self.version:
#                     print(e)
#                     llm_model = AutoModelForCausalLM.from_pretrained("chavinlo/alpaca-native", device_map='auto', load_in_8bit=True)
#                 elif self.model:
#                     llm_model = AutoModelForCausalLM.from_pretrained("chavinlo/alpaca-native", device_map='auto', load_in_8bit=True)
#                 self.llm = llm_model
#             except Exception as e:
#                 return f'Unable to find a local model. When tried to install, below error occurred\n{e}'
            

#     def response_capturer(self,schema,prompt):
#         try:
#             start_time=time.time()
#             template = self.template.replace("{schema}",schema).replace("{prompt}",prompt)
#             if self.llm:
#                 model = self.llm
#                 print(model)

#             else:
#                  model = self.load_model()
#                  print(model)
#                  if type(model)==str:
#                      raise Exception(model) 
#             sql_query = model(template)
#             try:
#                 sql_query = re.findall(r'```([\s\S]*?)```',sql_query, re.DOTALL)[0]
#             except:
#                 pass
#             end_time = time.time() 
#             return sql_query, (end_time-start_time)
#         except Exception as e:
#             return f'Error in loading the response\n {e}',0
import os
import time 
from dotenv import load_dotenv
import ollama

# class LLM:
#     def __init__(self):
#         # Assuming your ollama configuration does not need explicit model loading
#         # as shown in your second code snippet.
#         self.template = '''[INST] You are a professional SQL developer. Understand the question asked and return the most suitable query
#                              supported by SQLSERVER using the table : ""{schema}"". Always write sql server standard queries.
#                              Always wrap your code answer using ```. question: {prompt} [/INST]'''
#         nv_path = os.path.join(os.path.dirname(__file__), 'config', '.env')
#         load_dotenv(dotenv_path=nv_path)

#     def generate_query(self, schema, query):
#         template = self.template.replace("{schema}",schema).replace("{prompt}",query)
#         start_time=time.time()
#         stream = ollama.chat(
#             model='sql_generator_codellama',
#             messages=[{'role': 'user', 'content': template}],
#             stream=True
#         )
#         response = ""
#         for chunk in stream:
#             response += chunk['message']['content']
#         end_time = time.time() 
#         return response, abs(start_time-end_time) 


class LLM:
    def __init__(self):
        self.template = '''[INST] Given an input question:
1. In the first line, provide the user’s natural language query input as the output

2. Analyze the user's input and the provided database schema to generate a corresponding SQL query. Make sure to construct the query considering the best practices for database querying and security, especially focusing on preventing SQL injection risks.

3. If the user's input is ambiguous or if you cannot generate a precise SQL query with high confidence, prompt the user with specific questions to clarify their intent. Ensure these questions are directly related to refining the user's input for a more accurate SQL translation.

4. Produce the SQL query as the output. Do not provide any explanations or additional information beyond the SQL query itself. If further input from the user is needed, only output the necessary clarifying questions. 
You are a professional SQL developer. Understand the question asked and return only relevent SQLSERVER answer using the table : "{schema}". Always write sql server standard queries.
Always wrap your code answer using ```. question: {prompt}.  [/INST]'''
        nv_path = os.path.join(os.path.dirname(__file__), 'config', '.env')
        load_dotenv(dotenv_path=nv_path)

    def generate_query(self, schema, query, history):
        template = self.template.replace("{schema}", schema).replace("{prompt}", query)
        start_time = time.time()
        messages = [{'role': 'system', 'content': history}] if history else []
        messages.append({'role': 'user', 'content': template})
        stream = ollama.chat(
            model='sql_generator_codellama',
            messages=messages,
            stream=True
        )
        response = ""
        for chunk in stream:
            response += chunk['message']['content']
        end_time = time.time()
        return response, abs(start_time - end_time)