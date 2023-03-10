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
        {'fieldname': 'enabled', 'label': 'Enabled', 'fieldtype': 'Check', 'width': 120},
        {'fieldname': 'start_date', 'label': 'Start Date', 'fieldtype': 'Date', 'width': 120},
        {'fieldname': 'end_date', 'label': 'End Date', 'fieldtype': 'Date', 'width': 120},
        {'fieldname': 'item', 'label': 'Item', 'fieldtype': 'Link', 'options': 'Item', 'width': 250},
        {'fieldname': 'sales_invoice', 'label': 'Referenz', 'fieldtype': 'Data', 'width': 150},
        {'fieldname': 'status', 'label': 'Status', 'fieldtype': 'Data', 'width': 150}
    ]

def get_data(filters):

    dataSubscription = frappe.db.get_list('sqSubscriptionItem',filters={'customer': filters.customer, 'enabled': filters.enabled} ,fields=['customer', 'enabled', 'start_date' , 'end_date', 'item', 'name'])
    #frappe.throw(str(data))
    data = []
    for d in dataSubscription:
        #dataSubscriptionPeriod = frappe.db.get_list('sqSubscriptionPeriod',filters={'parent': d.name, 'sales_invoice': ["is", "set"]} ,fields=['sales_invoice', 'start_date' , 'status'])
        dataSubscriptionPeriod = frappe.db.get_list('sqSubscriptionPeriod',filters={'parent': d.name,'sales_invoice': ["is", "not set"]} ,fields=['sales_invoice','start_date', 'status', 'parent', 'name'])
        data.append(d)
        #frappe.msgprint(str( d.name), "Debug")
        for p in dataSubscriptionPeriod:
            per = []
            p.customer = p.name
            per.append(p)
            frappe.msgprint(str(per), "Debug")
            data.append(p)

    return data