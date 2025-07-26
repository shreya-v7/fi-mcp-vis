import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import os

DATA_DIR = 'test_data_dir'
JSON_FILES = [
    ('Bank Transactions', 'fetch_bank_transactions.json'),
    ('Credit Report', 'fetch_credit_report.json'),
    ('Mutual Fund Transactions', 'fetch_mf_transactions.json'),
    ('EPF Details', 'fetch_epf_details.json'),
    ('Net Worth', 'fetch_net_worth.json'),
    ('Stock Transactions', 'fetch_stock_transactions.json')
]

def list_account_numbers(data_dir=DATA_DIR):
    return [name for name in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, name))]

def load_json_for_account(account_number, filename, data_dir=DATA_DIR):
    file_path = os.path.join(data_dir, account_number, filename)
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'r') as f:
        return json.load(f)

def visualize_bank_transactions(data):
    st.subheader("Bank Transactions")
    for bank in data.get('bankTransactions', []):
        st.write(f"**{bank['bank']}**")
        df = pd.DataFrame(bank['txns'], columns=['Amount', 'Narration', 'Date', 'Type', 'Mode', 'Current Balance'])
        st.dataframe(df)
        df['Type'] = df['Type'].map({1: 'Credit', 2: 'Debit'})
        st.bar_chart(df.groupby('Type')['Amount'].sum())

def visualize_credit_report(data):
    st.subheader("Credit Report")
    cr = data.get('creditReports', [{}])[0].get('creditReportData', {})
    user_msg = cr.get('userMessage', {}).get('userMessageText', '')
    st.write(user_msg)
    summary = cr.get('creditAccount', {}).get('creditAccountSummary', {}).get('account', {})
    st.dataframe(pd.DataFrame([summary]))
    details = cr.get('creditAccount', {}).get('creditAccountDetails', [])
    balances = [int(acc.get('currentBalance', 0)) for acc in details]
    names = [acc.get('subscriberName', '') for acc in details]
    if balances and names:
        fig, ax = plt.subplots()
        ax.pie(balances, labels=names, autopct='%1.1f%%')
        st.pyplot(fig)

def visualize_mf_transactions(data):
    st.subheader("Mutual Fund Transactions")
    for scheme in data.get('mfTransactions', []):
        st.write(f"**{scheme['schemeName']}**")
        df = pd.DataFrame(scheme['txns'], columns=['Type', 'Date', 'Price', 'Units', 'Amount'])
        df['Type'] = df['Type'].map({1: 'Buy', 2: 'Sell'})
        st.dataframe(df)
        st.bar_chart(df.groupby('Type')['Amount'].sum())

def visualize_epf_details(data):
    st.subheader("EPF Details")
    for account in data.get('uanAccounts', []):
        ests = account.get('rawDetails', {}).get('est_details', [])
        df = pd.DataFrame(ests)
        st.dataframe(df)
        balances = [int(est.get('pf_balance', {}).get('net_balance', 0)) for est in ests]
        names = [est.get('est_name', '') for est in ests]
        if balances and names:
            fig, ax = plt.subplots()
            ax.bar(names, balances)
            st.pyplot(fig)

def visualize_net_worth(data):
    st.subheader("Net Worth")
    nw = data.get('netWorthResponse', {})
    assets = nw.get('assetValues', [])
    liabilities = nw.get('liabilityValues', [])
    asset_df = pd.DataFrame(assets)
    liability_df = pd.DataFrame(liabilities)
    st.write("Assets")
    st.dataframe(asset_df)
    st.write("Liabilities")
    st.dataframe(liability_df)
    if assets:
        fig, ax = plt.subplots()
        ax.pie([float(a['value']['units']) for a in assets], labels=[a['netWorthAttribute'] for a in assets], autopct='%1.1f%%')
        st.pyplot(fig)

def visualize_stock_transactions(data):
    st.subheader("Stock Transactions")
    for stock in data.get('stockTransactions', []):
        st.write(f"**ISIN: {stock['isin']}**")
        txns = stock['txns']
        # Always pad to 4 columns
        padded_txns = [t + [None] * (4 - len(t)) for t in txns]
        cols = ['Type', 'Date', 'Quantity', 'NAV']
        df = pd.DataFrame(padded_txns, columns=cols)
        df['Type'] = df['Type'].map({1: 'Buy', 2: 'Sell', 3: 'Bonus', 4: 'Split'})
        st.dataframe(df)
        st.bar_chart(df.groupby('Type')['Quantity'].sum())

def main():
    st.title("Account Overview")
    accounts = list_account_numbers()
    st.sidebar.header("Select Account")
    selected_account = st.sidebar.selectbox("Account", accounts)
    st.header(f"Account: {selected_account}")
    tab_names = [name for name, _ in JSON_FILES]
    tabs = st.tabs(tab_names)
    for i, (tab_name, json_file) in enumerate(JSON_FILES):
        with tabs[i]:
            data = load_json_for_account(selected_account, json_file)
            if data is None:
                st.info(f"No data found for {tab_name}")
                continue
            if json_file == 'fetch_bank_transactions.json':
                visualize_bank_transactions(data)
            elif json_file == 'fetch_credit_report.json':
                visualize_credit_report(data)
            elif json_file == 'fetch_mf_transactions.json':
                visualize_mf_transactions(data)
            elif json_file == 'fetch_epf_details.json':
                visualize_epf_details(data)
            elif json_file == 'fetch_net_worth.json':
                visualize_net_worth(data)
            elif json_file == 'fetch_stock_transactions.json':
                visualize_stock_transactions(data)

if __name__ == "__main__":
    main()