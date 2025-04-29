import pandas as pd
import os
import re

import logging
from datetime import datetime

logging.basicConfig(filename='SupportBank.log', filemode='w', level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logging.info('is time we started at')


#get the data
print(os.listdir('data'))

source = f'data/{input('Which file do you want to use?')}'
logging.info('getting the data')
year=re.findall(r'\d+2',source)
if '.csv' in source:
    df = pd.read_csv(source)
elif '.json' in source:
    df = pd.read_json(source,dtype={'Date':str})
    df.rename(columns={'FromAccount': 'From', 'ToAccount': 'To'}, inplace=True)
elif '.xml' in source:
    xml = pd.read_xml('data/Transactions2012.xml', xpath='.//SupportTransaction')
    xml_names = pd.read_xml('data/Transactions2012.xml', xpath='.//Parties')
    df = pd.concat([xml, xml_names], axis=1)
    df.drop(columns=['Parties'], inplace=True)
    df.rename(columns={'Value': 'Amount','Description':'Narrative'}, inplace=True)

else:
    print('Please enter a valid file')


#create dictionary
accounts = {}
logging.info('working on balances per person')
for index, row in df.iterrows():

    sender = row['From']
    recipient = row['To']
    date = row['Date']
    date_format = '%d/%m/%Y'
    date_format_json = '%Y-%m-%d'
    try:
        date = datetime.strptime(date, date_format)
    except:
        try:
            date = datetime.strptime(date, date_format_json)
        except:
            try:
                date =datetime.fromordinal(datetime(1900, 1, 1).toordinal() + date - 2)
                if date.timetuple()[0]==int(year[0]):
                    pass
                else:
                    logging.warning(f'"{row['Date']}" at row {index} ain\'t a valid date')
            except:
                logging.warning(f'"{row['Date']}" at row {index} ain\'t a valid date')

    try:
        amount = round(float(row['Amount']),1)
    except:
        logging.warning(f'Could not convert "{row['Amount']}" to number at row {index}. This will not be included in total.')

    if sender not in accounts:
        accounts[sender] = 0
    if recipient not in accounts:
        accounts[recipient] = 0
    accounts[sender]-=amount
    accounts[recipient]+=amount


#list all people
def list_all():

    for key, value in accounts.items():
        print(f'{key}: {round(value,2)}')


#list all transactions with selected account
def listed(account):
    logging.info(f'working on transactions for {account}')
    if account in df['From'].unique() or account in df['To'].unique():
        for index,row in df.iterrows():

            date = row['Date']
            date_format = '%d/%m/%Y'
            date_format_json = '%Y-%m-%d'
            try:
                date = datetime.strptime(date, date_format).date()
            except:
                try:
                    date = datetime.strptime(date, date_format_json).date()
                except:
                    try:
                        date = datetime.fromordinal(datetime(1900, 1, 1).toordinal() + date - 2).date()
                        if date.timetuple()[0] == int(year[0]):
                            pass
                        else:
                            date ='invalid date'
                            logging.warning(f'"{row['Date']}" at row {index} ain\'t a valid date')
                    except:
                        date = 'invalid date'
                        logging.warning(f'"{row['Date']}" at row {index} ain\'t a valid date')
            try:
                amount = round(float(row['Amount']), 1)
            except:
                amount = 'invalid amount'
                logging.warning(f'Could not convert "{row['Amount']}" to number at row {index}')

            if row['From'] == account:
                print(f'{row['From']} to {row['To']} on {date}: {amount}, {row['Narrative']}')
            elif row['To'] == account:
                print(f'{row['From']} to {row['To']} on {date}: {amount}, {row['Narrative']}')
    else:
        print(f'{account} is not in accounts. Do better')



if __name__ == "__main__":
    while True:
        print("\nOptions:")
        print("1 - List all accounts and balances")
        print("2 - View transactions for an account")
        print("3 - Exit")
        choice = input("Enter your choice (1/2/3): ")

        if choice == '1':
            list_all()
        elif choice == '2':
            name = input("Enter the account name: ")
            listed(name)

        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")