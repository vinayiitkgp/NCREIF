import openai
import json
import pandas as pd
import requests
import streamlit as st
import os

os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

def ncreif_api(url):
    print(url)
    r = requests.get(url)
    return pd.DataFrame(r.json()['NewDataSet']['Result1']) #r.json() #df


def run_conversation(prompt):
    
    # Step 1: send the conversation and available functions to GPT
    #prompt = input("What is your query?: ")
    messages = [{"role": "user", "content": f"{prompt}"},
                {"role": "system", "content": """
                 Take a deep breath and go step-by-step.
                 1. You are running queries against an API. 
                 2. If the user asks about returns then exclude the 'select' parameter from the function
                 / api request and use KPI=Returns instead; otherwise create the select parameter as defined. 
                   Where and Group by clauses should not end with 'and'.
                 3. Take the input parameters provided.
                 4. Map any synonyms to their respective API terms using the provided dictionary.
                 5. Construct the select statement in SQL style; however, any parameters in the group statement should not be in the select statement.
                 6.When 'as of' is used it refers to a where statement for YYYYQ. 
                 7.YYYYQ is numeric and should not have quotes. 
                 Here are example prompts and the URL that should be passed to the function. Be sure to include all where statements as appropriate.
                Prompt: Give me historical returns by property type?
                Answer: http://www.ncreif-api.com/API.aspx?KPI=Returns&Where=NPI=1&GroupBy=PropertyType,YYYYQ&Format=json&UserName=sdunphy@metlife.com&password=password
                
                Prompt: What are historical returns by property type?
                Answer: http://www.ncreif-api.com/API.aspx?KPI=Returns&Where=NPI=1&GroupBy=PropertyType,YYYYQ&Format=json&UserName=sdunphy@metlife.com&password=password
                
                Prompt: Calculate property returns in the Phoenix market by property type?
                Answer: http://www.ncreif-api.com/API.aspx?KPI=Returns&Where=NPI=1%20and%20CBSAName=%27AZ-Phoenix-Mesa-Scottsdale%27&GroupBy=PropertyType,YYYYQ&Format=json&UserName=sdunphy@metlife.com&password=password
                
                Prompt: What are returns in the phoenix market by property type as of 2Q 2023?
                Answer: http://www.ncreif-api.com/API.aspx?KPI=Returns&Where=NPI=1%20and%20CBSAName=%27AZ-Phoenix-Mesa-Scottsdale%27%20and%20YYYYQ=20232&GroupBy=PropertyType&Format=json&UserName=sdunphy@metlife.com&password=password
                
                Prompt: Calculate apartment property returns in the Phoenix market.
                Answer: http://www.ncreif-api.com/API.aspx?KPI=Returns&Where=NPI=1%20and%20CBSAName=%27AZ-Phoenix-Mesa-Scottsdale%27%20and%20[PropertyType]=%27A%27&GroupBy=YYYYQ&Format=json&UserName=sdunphy@metlife.com&password=password
                
                Prompt: What are historical apartment returns in the Phoenix market?
                Answer: http://www.ncreif-api.com/API.aspx?KPI=Returns&Where=NPI=1%20and%20CBSAName=%27AZ-Phoenix-Mesa-Scottsdale%27%20and%20[PropertyType]=%27A%27&GroupBy=YYYYQ&Format=json&UserName=sdunphy@metlife.com&password=password
                
                Prompt: What are historical retail returns in the Phoenix market?
                Answer: http://www.ncreif-api.com/API.aspx?KPI=Returns&Where=NPI=1%20and%20CBSAName=%27AZ-Phoenix-Mesa-Scottsdale%27%20and%20[PropertyType]=%27R%27&GroupBy=YYYYQ&Format=json&UserName=sdunphy@metlife.com&password=password
                
                Prompt: Show me office returns by market as of 2Q 2023.
                Answer: http://www.ncreif-api.com/API.aspx?KPI=Returns&Where=NPI=1%20and%20[PropertyType]=%27O%27%20and%20YYYYQ=20232&GroupBy=CBSAName&Format=json&UserName=sdunphy@metlife.com&password=password
                
                Prompt: Calculate market value and net operating income by property type.
                Answer: http://www.ncreif-api.com/API.aspx?SELECT=sum(NOI)%20as%20NOI,%20sum(MV)%20as%20MarketValue&Where=NPI=1&GroupBy=YYYYQ,%20PropertyType&Format=JSON&UserName=sdunphy@metlife.com&password=password
                
                Prompt: Calculate the sum of NOI and Market Value and the property count by market and property type as of December 31, 2022.
                Answer: http://www.ncreif-api.com/API.aspx?SELECT=sum(NOI)%20as%20NOI,%20sum(MV)%20as%20MarketValue,%20count(*)%20as%20PropCount&Where=NPI=1%20and%20YYYYQ=20224&GroupBy=CBSAName,%20PropertyType&Format=JSON&UserName=sdunphy@metlife.com&password=password
                
                Prompt: Calculate the volatility of property type returns between 1Q 2010 and 4Q 2020.
                Answer: http://www.ncreif-api.com/API.aspx?SELECT=stdev(IncRet)%20as%20IncomeReturnVol,%20stdev(AppRet)%20as%20AppReturnVol,%20stdev(TotRet)%20as%20TotalRetVol&Where=NPI=1%20and%20YYYYQ%20%3E=20101%20and%20YYYYQ%20%3C=%2020204&GroupBy=%20PropertyType&Format=JSON&UserName=sdunphy@metlife.com&password=password
                    
                Prompt: Calculate the sum of NOI, MV, and NRA for apartments by quarter.
                Answer: http://www.ncreif-api.com/API.aspx?SELECT=sum(NOI)%20as%20NOI,%20sum(MV)%20as%20MarketValue,%20sum(NRA)%20as%20NRA&Where=PropertyType=%27A%27&GroupBy=YYYYQ&Format=json&UserName=sdunphy@metlife.com&password=password
                 
                Prompt: Calculate the standard deviation of market total returns between 1Q 2020 and 2Q 2023.
                Answer: http://www.ncreif-api.com/API.aspx?SELECT=stdev(TotRet)%20as%20std_dev&Where=NPI=1 and YYYYQ%20%3E=20201%20and%20YYYYQ%20%3C=%2020232&GroupBy=CBSANameFormat=JSON&UserName=sdunphy@metlife.com&password=password
                    
                Prompt: Summarize office returns by Year Built and quarter.
                Answer: http://www.ncreif-api.com/API.aspx?KPI=Returns&Where=NPI=1%20and%20PropertyType%20=%27O%27%20&GroupBy=YrBuilt,YYYYQ&Format=json&UserName=sdunphy@metlife.com&password=password
                    
                Prompt: What are historical office and retail returns combined?
                Answer: http://www.ncreif-api.com/API.aspx?KPI=Returns&Where=NPI=1%20and%20PropertyType IN (%27R%27, %27O%27)&GroupBy=YYYYQ&Format=json&UserName=sdunphy@metlife.com&password=password
                
                 synonyms = {
                    'Market Value': 'MV',
                    'Net Operating Income':'NOI',
                    'Year Built':'YrBuilt',
                    'Region':'Region',
                    'Capital Expenditures':'CapEx',
                    'CapEx':'CapEx',
                    'Life Cycle':'LifeCycle',
                    'Square Feet':'NRA',
                    'Net Rentable Area':'NRA',
                    'Occupancy':'PercentLeased',
                    'State':'State',
                    'Joint Venture':'JV',
                    'Division':'Division',
                    'Subtype':'PropertySubType',
                    'Fund Type':'FundType',
                    'Fund':'FundType',
                    'ODCE':'D',
                    'Denominator':'denom',
                    'Prior Market Value':'MVLag1',
                    'Capex':'Capex',
                    'Capital Expenditures':'capex',
                    'NOI':'NOI',
                    'Square Feet':'SqFt',
                    'Market':'CBSAName',
                    'Property Type':'PropertyType',
                    'Period':'YYYYQ',
                    'Quarter':'YYYYQ',
                    'Office':'O',
                    'Retail':'R',
                    'Industrial':'I',
                    'Apartments':'A',
                    'Hotels':'H'
                    }
                 """ 
                 
                 }]
    functions = [
        {
            "name": "ncreif_api",
            "description": """ 
                                Generates a URL for the NCREIF API 
                            """,
           "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL for the API call" ,
                    },
                },
                     
            },
        }
    ]
    
    
    response = openai.ChatCompletion.create(
        model="gpt-4-0613",
        temperature = .8,
        messages=messages,
        functions=functions,
        function_call="auto",  # auto is default, but we'll be explicit
    )
    response_message = response["choices"][0]["message"]

    # Step 2: check if GPT wanted to call a function
    if response_message.get("function_call"):
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "ncreif_api": ncreif_api,
        }  # only one function in this example, but you can have multiple
        function_name = response_message["function_call"]["name"]
        fuction_to_call = available_functions[function_name]
        function_args = json.loads(response_message["function_call"]["arguments"])
        function_response = fuction_to_call(
            url=function_args.get("url"),
        )

        # Step 4: send the info on the function call and function response to GPT
        messages.append(response_message)  # extend conversation with assistant's reply
        messages.append(
            {
                "role": "function",
                "name": function_name,
                "content": function_response,
            }
        )  # extend conversation with function response
        #second_response = openai.ChatCompletion.create(
        #    model="gpt-3.5-turbo-0613",
        #    messages=messages,
        #)  # get a new response from GPT where it can see the function response
        return function_response #second_response

st.set_page_config(page_title='AI NCREIF QUERY TOOL')
st.title('AI NCREIF QUERY TOOL')

query_input = st.text_input("Enter your query: ")
write_value = run_conversation(query_input)
st.write(write_value)

