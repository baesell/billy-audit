#!/usr/bin/env python
# coding: utf-8

# In[379]:


import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import pdfplumber
import re
import dateparser
import plotly.express as px

from supabase import create_client, Client


# In[380]:


# add streamlit webapp title

st.set_page_config(layout="wide")

st.title('BillyAudit')

st.header('Automated freight invoice checks')


# In[381]:


@st.experimental_singleton()

def init_connection():
    url = st.secrets["supabase_url"]
    key = st.secrets["supabase_key"]
    return create_client(url, key)

supabase = init_connection()

rate_data = pd.DataFrame()

for i in range(0, len(rate_data)):
    supabase.table('rate_data').insert({'origin_code':rate_data['origin_code'][i], 'destination_code':rate_data['destination_code'][i], 'transport_mode':int(rate_data['transort_mode'][i]), 'charge_a':float(rate_data['charge_a'][i]), 'charge_b':float(rate_data['charge_b'][i]), 'charge_c':float(rate_data['charge_c'][i])}).execute()


# # Enter Contract Rates

# In[382]:


# add streamlit header

st.header('1. Enter Contract Rates')


# In[383]:


from st_aggrid.shared import GridUpdateMode, DataReturnMode

rate_data = pd.DataFrame(supabase.table('rate_data').select('*').execute().data)

col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11 = st.columns([1,1,1,1,1,1,1,1,1,1,1])

aggrid = GridOptionsBuilder.from_dataframe(rate_data)

aggrid.configure_column("service_provider", header_name='Service Provider', editable=True, suppressMovable=True)
aggrid.configure_column("origin_code", header_name='Origin Code', editable=True, suppressMovable=True)
aggrid.configure_column("destination_code", header_name='Destination Code', editable=True, suppressMovable=True)
aggrid.configure_column("freight_service", header_name='Freight Service', editable=True, suppressMovable=True, cellEditor='agSelectCellEditor', cellEditorParams={'values': ['Air-Economy', 'Air-Premium', 'Air-Priority', 'Sea-FCL-20GP', 'Sea-FCL-20OT', 'Sea-FCL-20RF', 'Sea-FCL-20TK', 'Sea-FCL-40GP', 'Sea-FCL-40HC', 'Sea-FCL-40OT', 'Sea-FCL-40RF', 'Sea-FCL-45HC', 'Sea-LCL']})
aggrid.configure_column("origin_collection_fees", header_name='Origin Collection Fees', editable=True, suppressMovable=True, type=["numericColumn"])
aggrid.configure_column("origin_minimum_collection_fee", header_name='Origin Min Collection Fee', editable=True, suppressMovable=True, type=["numericColumn"])
aggrid.configure_column("origin_handling_fees", header_name='Origin Handling Fee', editable=True, suppressMovable=True, type=["numericColumn"])
aggrid.configure_column("origin_minimum_handling_fee", header_name='Origin Min Handling Fee', editable=True, suppressMovable=True, type=["numericColumn"])
aggrid.configure_column("freight_rate", header_name='Freight Rate', editable=True, suppressMovable=True, type=["numericColumn"])
aggrid.configure_column("bunker_adjustment_factor", header_name='Bunker Adjustment Factor', editable=True, suppressMovable=True, type=["numericColumn"])
aggrid.configure_column("dangerous_goods_surcharge", header_name='Dangerous Goods Surcharge', editable=True, suppressMovable=True, type=["numericColumn"])
aggrid.configure_column("documentation_fees", header_name='Documentation Fees', editable=True, suppressMovable=True, type=["numericColumn"])
aggrid.configure_column("filing_fees", header_name='Filing Fees', editable=True, suppressMovable=True, type=["numericColumn"])
aggrid.configure_column("other_fees_per_bill_of_lading", header_name='Other Fees per BoL', editable=True, suppressMovable=True, type=["numericColumn"])
aggrid.configure_column("other_fees_per_container", header_name='Other Fees per Container', editable=True, suppressMovable=True, type=["numericColumn"])
aggrid.configure_column("other_fees_per_cbm", header_name='Other Fees per CBM', editable=True, suppressMovable=True, type=["numericColumn"])
aggrid.configure_column("other_fees_per_kg", header_name='Other Fees per KG', editable=True, suppressMovable=True, type=["numericColumn"])
aggrid.configure_column("destination_handling_fees", header_name='Destination Handling Fees', editable=True, suppressMovable=True, type=["numericColumn"])
aggrid.configure_column("destination_minimum_handling_fee", header_name='Destination Min Handling Fee', editable=True, suppressMovable=True, type=["numericColumn"])
aggrid.configure_column("destination_delivery_fees", header_name='Destination Delivery Fees', editable=True, suppressMovable=True, type=["numericColumn"])
aggrid.configure_column("destination_minimum_delivery_fee", header_name='Destination Min Delivery Fee', editable=True, suppressMovable=True, type=["numericColumn"])

aggrid.configure_selection(selection_mode= 'single')

gridOptions = aggrid.build()
data = AgGrid(rate_data,
              gridOptions=gridOptions,
              height=200,
              fit_columns_on_grid_load=False,
              update_mode=GridUpdateMode.SELECTION_CHANGED | GridUpdateMode.VALUE_CHANGED,
              allow_unsafe_jscode=True,
              reload_data=False,
              theme='streamlit')

with col1:
    if st.button('Insert Row'):
        supabase.table('rate_data').insert({'service_provider': 'Enter', 'origin_code': 'Enter', 'destination_code': 'Enter', 'freight_service': 'Enter', 'origin_collection_fees': 0, 'origin_minimum_collection_fee': 0, 'origin_handling_fees': 0, 'origin_minimum_handling_fee': 0, 'freight_rate': 0, 'bunker_adjustment_factor': 0, 'dangerous_goods_surcharge': 0, 'documentation_fees': 0, 'filing_fees': 0, 'other_fees_per_bill_of_lading': 0, 'other_fees_per_container': 0, 'other_fees_per_cbm': 0, 'other_fees_per_kg': 0, 'destination_handling_fees': 0, 'destination_minimum_handling_fee': 0, 'destination_delivery_fees': 0, 'destination_minimum_delivery_fee': 0}).execute()
            
with col2:
    if st.button('Delete Row'):
        supabase.table('rate_data').delete().eq('origin_code', data["selected_rows"][0]['origin_code']).execute()

if st.button('Save Changes'):
    
    for i in range(rate_data.shape[0]):

        if rate_data.loc[i]['service_provider'] != data['data']['service_provider'][i]:
            supabase.table('rate_data').update({'service_provider': data['data']['service_provider'][i]}).eq('service_provider', rate_data.loc[i]['service_provider']).execute()
            st.caption(f"Name column data changed from {rate_data.loc[i]['service_provider']} to {data['data']['service_provider'][i]}...")
        
        if rate_data.loc[i]['origin_code'] != data['data']['origin_code'][i]:
            supabase.table('rate_data').update({'origin_code': data['data']['origin_code'][i]}).eq('origin_code', rate_data.loc[i]['origin_code']).execute()
            st.caption(f"Name column data changed from {rate_data.loc[i]['origin_code']} to {data['data']['origin_code'][i]}...")

        if rate_data.loc[i]['destination_code'] != data['data']['destination_code'][i]:
            supabase.table('rate_data').update({'destination_code': data['data']['destination_code'][i]}).eq('destination_code', rate_data.loc[i]['destination_code']).execute()
            st.caption(f"Name column data changed from {rate_data.loc[i]['destination_code']} to {data['data']['destination_code'][i]}...")

        if rate_data.loc[i]['freight_service'] != data['data']['transport_mode'][i]:
            supabase.table('rate_data').update({'freight_service': data['data']['freight_service'][i]}).eq('freight_service', rate_data.loc[i]['freight_service']).execute()
            st.caption(f"Name column data changed from {rate_data.loc[i]['freight_service']} to {data['data']['freight_service'][i]}...")

        if rate_data.loc[i]['origin_collection_fees'] != data['data']['origin_collection_fees'][i]:
            supabase.table('rate_data').update({'origin_collection_fees': data['data']['origin_collection_fees'][i]}).eq('origin_collection_fees', rate_data.loc[i]['origin_collection_fees']).execute()
            st.caption(f"Name column data changed from {rate_data.loc[i]['origin_collection_fees']} to {data['data']['origin_collection_fees'][i]}...")

        if rate_data.loc[i]['origin_minimum_collection_fee'] != data['data']['origin_minimum_collection_fee'][i]:
            supabase.table('rate_data').update({'origin_minimum_collection_fee': data['data']['origin_minimum_collection_fee'][i]}).eq('origin_minimum_collection_fee', rate_data.loc[i]['origin_minimum_collection_fee']).execute()
            st.caption(f"Name column data changed from {rate_data.loc[i]['origin_minimum_collection_fee']} to {data['data']['origin_minimum_collection_fee'][i]}...")

        if rate_data.loc[i]['origin_handling_fees'] != data['data']['origin_handling_fees'][i]:
            supabase.table('rate_data').update({'origin_handling_fees': data['data']['origin_handling_fees'][i]}).eq('origin_handling_fees', rate_data.loc[i]['origin_handling_fees']).execute()
            st.caption(f"Name column data changed from {rate_data.loc[i]['origin_handling_fees']} to {data['data']['origin_handling_fees'][i]}...")
            
        if rate_data.loc[i]['origin_minimum_handling_fee'] != data['data']['origin_minimum_handling_fee'][i]:
            supabase.table('rate_data').update({'origin_minimum_handling_fee': data['data']['origin_minimum_handling_fee'][i]}).eq('origin_minimum_handling_fee', rate_data.loc[i]['origin_minimum_handling_fee']).execute()
            st.caption(f"Name column data changed from {rate_data.loc[i]['origin_minimum_handling_fee']} to {data['data']['origin_minimum_handling_fee'][i]}...")

        if rate_data.loc[i]['freight_rate'] != data['data']['freight_rate'][i]:
            supabase.table('rate_data').update({'freight_rate': data['data']['freight_rate'][i]}).eq('freight_rate', rate_data.loc[i]['freight_rate']).execute()
            st.caption(f"Name column data changed from {rate_data.loc[i]['freight_rate']} to {data['data']['freight_rate'][i]}...")

        if rate_data.loc[i]['bunker_adjustment_factor'] != data['data']['bunker_adjustment_factor'][i]:
            supabase.table('rate_data').update({'bunker_adjustment_factor': data['data']['bunker_adjustment_factor'][i]}).eq('bunker_adjustment_factor', rate_data.loc[i]['bunker_adjustment_factor']).execute()
            st.caption(f"Name column data changed from {rate_data.loc[i]['bunker_adjustment_factor']} to {data['data']['bunker_adjustment_factor'][i]}...")

        if rate_data.loc[i]['dangerous_goods_surcharge'] != data['data']['dangerous_goods_surcharge'][i]:
            supabase.table('rate_data').update({'dangerous_goods_surcharge': data['data']['dangerous_goods_surcharge'][i]}).eq('dangerous_goods_surcharge', rate_data.loc[i]['dangerous_goods_surcharge']).execute()
            st.caption(f"Name column data changed from {rate_data.loc[i]['dangerous_goods_surcharge']} to {data['data']['dangerous_goods_surcharge'][i]}...")
            
        if rate_data.loc[i]['documentation_fees'] != data['data']['documentation_fees'][i]:
            supabase.table('rate_data').update({'documentation_fees': data['data']['documentation_fees'][i]}).eq('documentation_fees', rate_data.loc[i]['documentation_fees']).execute()
            st.caption(f"Name column data changed from {rate_data.loc[i]['documentation_fees']} to {data['data']['documentation_fees'][i]}...")
            
        if rate_data.loc[i]['filing_fees'] != data['data']['filing_fees'][i]:
            supabase.table('rate_data').update({'filing_fees': data['data']['filing_fees'][i]}).eq('filing_fees', rate_data.loc[i]['filing_fees']).execute()
            st.caption(f"Name column data changed from {rate_data.loc[i]['filing_fees']} to {data['data']['filing_fees'][i]}...")
            
        if rate_data.loc[i]['other_fees_per_bill_of_lading'] != data['data']['other_fees_per_bill_of_lading'][i]:
            supabase.table('rate_data').update({'other_fees_per_bill_of_lading': data['data']['other_fees_per_bill_of_lading'][i]}).eq('other_fees_per_bill_of_lading', rate_data.loc[i]['other_fees_per_bill_of_lading']).execute()
            st.caption(f"Name column data changed from {rate_data.loc[i]['other_fees_per_bill_of_lading']} to {data['data']['other_fees_per_bill_of_lading'][i]}...")
            
        if rate_data.loc[i]['other_fees_per_container'] != data['data']['other_fees_per_container'][i]:
            supabase.table('rate_data').update({'other_fees_per_container': data['data']['other_fees_per_container'][i]}).eq('other_fees_per_container', rate_data.loc[i]['other_fees_per_container']).execute()
            st.caption(f"Name column data changed from {rate_data.loc[i]['other_fees_per_container']} to {data['data']['other_fees_per_container'][i]}...")
            
        if rate_data.loc[i]['other_fees_per_cbm'] != data['data']['other_fees_per_cbm'][i]:
            supabase.table('rate_data').update({'other_fees_per_cbm': data['data']['other_fees_per_cbm'][i]}).eq('other_fees_per_cbm', rate_data.loc[i]['other_fees_per_cbm']).execute()
            st.caption(f"Name column data changed from {rate_data.loc[i]['other_fees_per_cbm']} to {data['data']['other_fees_per_cbm'][i]}...")
            
        if rate_data.loc[i]['other_fees_per_kg'] != data['data']['other_fees_per_kg'][i]:
            supabase.table('rate_data').update({'other_fees_per_kg': data['data']['other_fees_per_kg'][i]}).eq('other_fees_per_kg', rate_data.loc[i]['other_fees_per_kg']).execute()
            st.caption(f"Name column data changed from {rate_data.loc[i]['other_fees_per_kg']} to {data['data']['other_fees_per_kg'][i]}...")
            
        if rate_data.loc[i]['destination_handling_fees'] != data['data']['destination_handling_fees'][i]:
            supabase.table('rate_data').update({'destination_handling_fees': data['data']['destination_handling_fees'][i]}).eq('destination_handling_fees', rate_data.loc[i]['destination_handling_fees']).execute()
            st.caption(f"Name column data changed from {rate_data.loc[i]['destination_handling_fees']} to {data['data']['destination_handling_fees'][i]}...")
            
        if rate_data.loc[i]['destination_minimum_handling_fee'] != data['data']['destination_minimum_handling_fee'][i]:
            supabase.table('rate_data').update({'destination_minimum_handling_fee': data['data']['destination_minimum_handling_fee'][i]}).eq('destination_minimum_handling_fee', rate_data.loc[i]['destination_minimum_handling_fee']).execute()
            st.caption(f"Name column data changed from {rate_data.loc[i]['destination_minimum_handling_fee']} to {data['data']['destination_minimum_handling_fee'][i]}...")
            
        if rate_data.loc[i]['destination_delivery_fees'] != data['data']['destination_delivery_fees'][i]:
            supabase.table('rate_data').update({'destination_delivery_fees': data['data']['destination_delivery_fees'][i]}).eq('destination_delivery_fees', rate_data.loc[i]['destination_delivery_fees']).execute()
            st.caption(f"Name column data changed from {rate_data.loc[i]['destination_delivery_fees']} to {data['data']['destination_delivery_fees'][i]}...")
                
        if rate_data.loc[i]['destination_minimum_delivery_fee'] != data['data']['destination_minimum_delivery_fee'][i]:
            supabase.table('rate_data').update({'destination_minimum_delivery_fee': data['data']['destination_minimum_delivery_fee'][i]}).eq('destination_minimum_delivery_fee', rate_data.loc[i]['destination_minimum_delivery_fee']).execute()
            st.caption(f"Name column data changed from {rate_data.loc[i]['destination_minimum_delivery_fee']} to {data['data']['destination_minimum_delivery_fee'][i]}...")


# # Upload PDF Invoices

# In[384]:


# add streamlit header

st.header('')

st.header('2. Upload PDF Invoices')

uploaded_files = st.file_uploader("Choose a PDF file", type=['pdf'], accept_multiple_files=True)


# # Download Audit Results

# In[385]:


# add streamlit header

st.header('')

st.header('3. Download Audit Results')


# In[386]:


# read pdf files and extract content

invoice_data = []

for i in uploaded_files:
    pdf = pdfplumber.open(i)
    pdf_page = pdf.pages[0]
    content = pdf_page.extract_text()
    file_name = i.name
    invoice_data.append([file_name, content])
        
invoice_data = pd.DataFrame(invoice_data, columns = ['file_name', 'content'])


# In[387]:


# extract bill of lading number

invoice_data['air_bill_of_lading'] = invoice_data['content'].apply(lambda x: re.findall(r"\d{3}\-?\d{8}", x)).apply(lambda x: ','.join(map(str, x)))

invoice_data['ocean_bill_of_lading'] = invoice_data['content'].apply(lambda x: re.findall(r"[A-Z]{4}\d{8-12}", x)).apply(lambda x: ','.join(map(str, x)))

invoice_data['bill_of_lading'] = invoice_data['air_bill_of_lading'] + invoice_data['ocean_bill_of_lading']


# In[388]:


# extract service provider

service_provider = pd.DataFrame(supabase.table('service_provider').select('*').execute().data)

invoice_data['service_provider'] = invoice_data['content'].apply(lambda x: re.findall(r"(?=(\b" + '\\b|\\b'.join(service_provider['service_provider']) + r"\b))", x)).apply(lambda x: x[0] if len(x)>0 else "")


# In[389]:


# extract origin and destination port codes

port_codes = pd.DataFrame(supabase.table('port_codes').select('*').execute().data)

invoice_data['origin_code'] = invoice_data['content'].apply(lambda x: re.findall(r"(?=(\b" + '\\b|\\b'.join(port_codes['port_code']) + r"\b))", x)).apply(lambda x: x[0] if len(x)>0 else "")

invoice_data['destination_code'] = invoice_data['content'].apply(lambda x: re.findall(r"(?=(\b" + '\\b|\\b'.join(port_codes['port_code']) + r"\b))", x)).apply(lambda x: x[1] if len(x)>1 else "")


# In[390]:


# extract freight service

invoice_data['air'] = invoice_data['content'].apply(lambda x: re.findall(r"\d{3}\-?\d{8}", x)).apply(lambda x: 1 if len(x)>0 else 0)

invoice_data['sea-FCL-20GP'] = invoice_data['content'].apply(lambda x: re.findall(r"20GP\s*\-?\s*[A-Z]{4}\d{7}|[A-Z]{4}\d{7}\s*\-?\s*20GP", x)).apply(lambda x: len(set(x)))

invoice_data['sea-FCL-20OT'] = invoice_data['content'].apply(lambda x: re.findall(r"20OT\s*\-?\s*[A-Z]{4}\d{7}|[A-Z]{4}\d{7}\s*\-?\s*20OT", x)).apply(lambda x: len(set(x)))

invoice_data['sea-FCL-20RF'] = invoice_data['content'].apply(lambda x: re.findall(r"20RF\s*\-?\s*[A-Z]{4}\d{7}|[A-Z]{4}\d{7}\s*\-?\s*20RF", x)).apply(lambda x: len(set(x)))

invoice_data['sea-FCL-20TK'] = invoice_data['content'].apply(lambda x: re.findall(r"20TK\s*\-?\s*[A-Z]{4}\d{7}|[A-Z]{4}\d{7}\s*\-?\s*20TK", x)).apply(lambda x: len(set(x)))

invoice_data['sea-FCL-40GP'] = invoice_data['content'].apply(lambda x: re.findall(r"40GP\s*\-?\s*[A-Z]{4}\d{7}|[A-Z]{4}\d{7}\s*\-?\s*40GP", x)).apply(lambda x: len(set(x)))

invoice_data['sea-FCL-40HC'] = invoice_data['content'].apply(lambda x: re.findall(r"40HC\s*\-?\s*[A-Z]{4}\d{7}|[A-Z]{4}\d{7}\s*\-?\s*40HC", x)).apply(lambda x: len(set(x)))

invoice_data['sea-FCL-40OT'] = invoice_data['content'].apply(lambda x: re.findall(r"40OT\s*\-?\s*[A-Z]{4}\d{7}|[A-Z]{4}\d{7}\s*\-?\s*40OT", x)).apply(lambda x: len(set(x)))

invoice_data['sea-FCL-40RF'] = invoice_data['content'].apply(lambda x: re.findall(r"40RF\s*\-?\s*[A-Z]{4}\d{7}|[A-Z]{4}\d{7}\s*\-?\s*40RF", x)).apply(lambda x: len(set(x)))

invoice_data['sea-FCL-45HC'] = invoice_data['content'].apply(lambda x: re.findall(r"45HC\s*\-?\s*[A-Z]{4}\d{7}|[A-Z]{4}\d{7}\s*\-?\s*45HC", x)).apply(lambda x: len(set(x)))

invoice_data['sea-LCL'] = invoice_data['content'].apply(lambda x: re.findall(r"LCL\s*\-?\s*[A-Z]{4}\d{7}|[A-Z]{4}\d{7}\s*\-?\s*LCL", x)).apply(lambda x: len(set(x)))


# In[391]:


# extract container id

invoice_data['container_id'] = ''

for i in range(0, len(invoice_data)):
    if invoice_data[['sea-FCL-20GP', 'sea-FCL-20OT', 'sea-FCL-20RF', 'sea-FCL-20TK', 'sea-FCL-40GP', 'sea-FCL-40HC', 'sea-FCL-40OT', 'sea-FCL-40RF', 'sea-FCL-45HC', 'sea-LCL']][i] > 0:
        invoice_data['container_id'] = invoice_data['content'].apply(lambda x: re.findall(r"[A-Z]{4}\d{7}", x)).apply(lambda x: ','.join(map(str, x)))


# In[392]:


# extract number of pallets

invoice_data['pallets'] = invoice_data['content'].apply(lambda x: re.findall(r"(\d*[.,]*\d*[.,]*\d+[.,]*\d*)\s(?=PLT)", x)).apply(lambda x: min(x) if len(x)>0 else "")


# In[393]:


# extract weight

invoice_data['weight'] = invoice_data['content'].apply(lambda x: re.findall(r"(\d*[.,]*\d*[.,]*\d+[.,]\d*)\s(?=KG)", x)).apply(lambda x: min(x) if len(x)>0 else "")


# In[394]:


# extract volume

invoice_data['volume'] = invoice_data['content'].apply(lambda x: re.findall(r"(\d*[.,]*\d*[.,]*\d+[.,]\d*)\s(?=M3)", x)).apply(lambda x: min(x) if len(x)>0 else "")


# In[395]:


# extract invoice amount and currency

currencies = pd.DataFrame(supabase.table('currencies').select('*').execute().data)

invoice_data['invoice_amount'] = invoice_data['content'].apply(lambda x: re.findall(r"TOTAL (\d*[.,]*\d*[.,]*\d+[.,]\d{2})", x)).apply(lambda x: max(x) if len(x)>1 else "")

invoice_data['invoice_currency'] = invoice_data['content'].apply(lambda x: re.findall(r"TOTAL (?=(\b" + '\\b|\\b'.join(currencies['currency']) + r"\b))", x)).apply(lambda x: x[0] if len(x)>0 else "")


# In[396]:


# extract dates

invoice_data['departure_date'] = invoice_data['content'].apply(lambda x: re.findall(r"\d{1,2}-[a-zA-Z]{3}-\d{2}", x)).apply(lambda x: sorted(pd.to_datetime(x))[0] if len(x)>0 else "")

invoice_data['arrival_date'] = invoice_data['content'].apply(lambda x: re.findall(r"\d{1,2}-[a-zA-Z]{3}-\d{2}", x)).apply(lambda x: sorted(pd.to_datetime(x))[1] if len(x)>1 else "")

invoice_data['invoice_date'] = invoice_data['content'].apply(lambda x: re.findall(r"\d{1,2}-[a-zA-Z]{3}-\d{2}", x)).apply(lambda x: sorted(pd.to_datetime(x))[2] if len(x)>2 else "")

invoice_data['due_date'] = invoice_data['content'].apply(lambda x: re.findall(r"\d{1,2}-[a-zA-Z]{3}-\d{2}", x)).apply(lambda x: sorted(pd.to_datetime(x))[3] if len(x)>3 else "")

#invoice_data['payment_terms'] = invoice_data['due_date'] - invoice_data['invoice_date']


# In[397]:


# convert all figures into floats

for i in range(invoice_data.shape[0]):
        
    if len(invoice_data['weight'][i])>0:
        
        invoice_data['weight'][i] = invoice_data['weight'][i].replace(",", "").replace(".", "")
        invoice_data['weight'][i] = invoice_data['weight'][i][:-2] + "." + invoice_data['weight'][i][-2:]
        
    else: invoice_data['weight'][i] = ""

        
    if len(invoice_data['volume'][i])>0:
        
        invoice_data['volume'][i] = invoice_data['volume'][i].replace(",", "").replace(".", "")
        invoice_data['volume'][i] = invoice_data['volume'][i][:-3] + "." + invoice_data['volume'][i][-3:]
        
    else: invoice_data['volume'][i] = ""

        
    if len(invoice_data['invoice_amount'][i])>0:
        
        invoice_data['invoice_amount'][i] = invoice_data['invoice_amount'][i].replace(",", "").replace(".", "")
        invoice_data['invoice_amount'][i] = invoice_data['invoice_amount'][i][:-2] + "." + invoice_data['invoice_amount'][i][-2:]
        
    else: invoice_data['invoice_amount'][i] = ""

        
invoice_data['pallets'] = pd.to_numeric(invoice_data['pallets'], downcast='integer')
invoice_data['weight'] = pd.to_numeric(invoice_data['weight'], downcast='float')
invoice_data['volume'] = pd.to_numeric(invoice_data['volume'], downcast='float')
invoice_data['invoice_amount'] = pd.to_numeric(invoice_data['invoice_amount'], downcast='float')

invoice_data = invoice_data.drop(columns=['content'])


# In[398]:


# transforming invoice data table from lane-level to freight-service-level information

verified_data = invoice_data.melt(
    id_vars = ['file_name', 'bill_of_lading', 'service_provider', 'origin_code', 'destination_code', 'invoice_currency', 'invoice_amount'],
    value_vars = ['air', 'sea-FCL-20GP', 'sea-FCL-20OT', 'sea-FCL-20RF', 'sea-FCL-20TK', 'sea-FCL-40GP', 'sea-FCL-40HC', 'sea-FCL-40OT', 'sea-FCL-40RF', 'sea-FCL-45HC', 'sea-LCL'], 
    var_name = 'freight_service', 
    value_name = 'quantity')

verified_data = verified_data.merge(rate_data, 'left', on=['service_provider', 'origin_code', 'destination_code', 'freight_service'])

verified_data['should_cost'] = verified_data['quantity'] * verified_data['origin_collection_fees'] + verified_data['quantity'] * verified_data[['origin_handling_fees', 'freight_rate', 'bunker_adjustment_factor', 'dangerous_goods_surcharge', 'other_fees_per_container', 'destination_handling_fees']].sum(axis=1) + verified_data['quantity'] * verified_data['destination_delivery_fees'] + verified_data[['documentation_fees', 'filing_fees', 'other_fees_per_bill_of_lading']].sum(axis=1) * verified_data['quantity'] / verified_data.groupby(['bill_of_lading', 'service_provider', 'origin_code', 'destination_code'])['quantity'].sum()

#verified_data


# In[399]:


# verify invoice amount

verified_data_bol = verified_data.groupby(['bill_of_lading', 'service_provider', 'origin_code', 'destination_code', 'invoice_currency', 'invoice_amount'])['should_cost'].sum().reset_index()

verified_data_bol['deviation'] = verified_data['should_cost'] - verified_data['invoice_amount']

#verified_data_bol


# In[400]:


# plot graph with deviations

if not verified_data_bol.empty:

    df = pd.DataFrame(verified_data_bol, columns=['bol', 'invoice_amount', 'should_cost'])

    fig = px.area(verified_data_bol, x="bol", y=['invoice_amount', 'should_cost'], labels={'bol': 'Bill of Lading Number', 'invoice_amount': 'Invoice Amount', 'should_cost': 'Should Cost', 'value': 'Amount', 'variable': ''})

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


# In[403]:


# add streamlit table and download button

output_data = verified_data_bol[['bill_of_lading', 'service_provider', 'origin_code', 'destination_code', 'invoice_currency', 'invoice_amount', 'should_cost', 'deviation']]

aggrid = GridOptionsBuilder.from_dataframe(output_data)

aggrid.configure_column('bill_of_lading', header_name='BoL', editable=False, suppressMovable=True)
aggrid.configure_column('service_provider', header_name='Service Provider', editable=False, suppressMovable=True)
aggrid.configure_column('origin_code', header_name='Origin', editable=False, suppressMovable=True)
aggrid.configure_column('destination_code', header_name='Destination', editable=False, suppressMovable=True)
#aggrid.configure_column('freight_service', header_name='Freight Service', editable=False, suppressMovable=True)
#aggrid.configure_column('pallets', header_name='Pallets', editable=False, suppressMovable=True, type=['numericColumn','numberColumnFilter','customNumericFormat'], precision=0)
#aggrid.configure_column('weight', header_name='Weight', editable=False, suppressMovable=True, type=['numericColumn','numberColumnFilter','customNumericFormat'], precision=2)
#aggrid.configure_column('volume', header_name='Volume', editable=False, suppressMovable=True, type=['numericColumn','numberColumnFilter','customNumericFormat'], precision=2)
aggrid.configure_column('invoice_currency', header_name='Currency', editable=False, suppressMovable=True)
aggrid.configure_column('invoice_amount', header_name='Invoice Cost', editable=False, suppressMovable=True, type=['numericColumn','numberColumnFilter','customNumericFormat'], precision=0)
aggrid.configure_column('should_cost', header_name='Should Cost', editable=False, suppressMovable=True, type=['numericColumn','numberColumnFilter','customNumericFormat'], precision=0)
aggrid.configure_column('deviation', header_name='Deviation', editable=False, suppressMovable=True, type=['numericColumn','numberColumnFilter','customNumericFormat'], precision=0)

gridOptions = aggrid.build()

AgGrid(output_data,
       gridOptions=gridOptions,
       height=200,
       fit_columns_on_grid_load=True,
       theme='streamlit')

st.download_button(
     label="Download CSV",
     data=invoice_data.to_csv(),
     file_name='verified_data.csv',
     mime='text/csv',
)


# In[402]:


# save uploaded invoices into database

for i in range(0, len(invoice_data)):
    supabase.table('invoice_data').upsert({'file_name':invoice_data['file_name'][i], 'bill_of_lading':invoice_data['bill_of_lading'][i], 'service_provider':invoice_data['service_provider'][i], 'origin_code':invoice_data['origin_code'][i], 'destination_code':invoice_data['destination_code'][i], 'pallets':int(invoice_data['pallets'][i]), 'weight':float(invoice_data['weight'][i]), 'volume':float(invoice_data['volume'][i]), 'invoice_amount':float(invoice_data['invoice_amount'][i]), 'invoice_currency':invoice_data['invoice_currency'][i], 'departure_date':str(invoice_data['departure_date'][i]), 'arrival_date':str(invoice_data['arrival_date'][i]), 'invoice_date':str(invoice_data['invoice_date'][i]), 'due_date':str(invoice_data['due_date'][i])}).execute()

