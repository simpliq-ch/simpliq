# Copyright (c) 2023, simpliq and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
    columns, data = [], []      
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {'fieldname': 'customer', 'label': 'Customer', 'fieldtype': 'Link', 'options': 'Customer', 'width': 150},
        {'fieldname': 'enabled', 'label': 'Enabled', 'fieldtype': 'Check', 'width': 50},
        {'fieldname': 'start_date', 'label': 'Start Date', 'fieldtype': 'Date', 'width': 80},
        {'fieldname': 'end_date', 'label': 'End Date', 'fieldtype': 'Date', 'width': 80},
        {'fieldname': 'item', 'label': 'Item', 'fieldtype': 'Link', 'options': 'Item', 'width': 200}
    ]

def get_data(filters):
    sql_query = """ SELECT * FROM tabsqSubscriptionItem WHERE Customer = 'Test Kunde';""".format(customer = filters.customer)
    entries = frappe.db.sql(sql_query, as_dict=True)
    return entries