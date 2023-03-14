# Copyright (c) 2023, simpliq and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    columns, data = [], []      
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    return [
        {'fieldname': 'customer', 'label': 'Customer', 'fieldtype': 'Link', 'options': 'Customer', 'width': 150},
        {'fieldname': 'autorenew', 'label': 'Renew', 'fieldtype': 'Check', 'width': 60},
        {'fieldname': 'start_date', 'label': 'Start Date', 'fieldtype': 'Date', 'width': 100},
        {'fieldname': 'end_date', 'label': 'End Date', 'fieldtype': 'Date', 'width': 100},
        {'fieldname': 'item', 'label': 'Item', 'fieldtype': 'Link', 'options': 'Item', 'width': 250},
        {'fieldname': 'qty', 'label': 'Quantity', 'fieldtype': 'Float', 'width': 100},
        {'fieldname': 'sales_invoice', 'label': 'Referenz', 'fieldtype': 'Data', 'width': 150},
        {'fieldname': 'status', 'label': 'Status', 'fieldtype': 'Data', 'width': 100}
    ]

def get_data(filters):

    dataSubscription = frappe.db.get_list('sqSubscriptionItem',filters={'customer': filters.customer, 'autorenew': filters.autorenew} ,fields=['customer', 'autorenew', 'item', 'name'])
    #frappe.throw(str(data))
    data = []
    for d in dataSubscription:
        dataSubscriptionPeriod = frappe.db.get_list('sqSubscriptionPeriod',filters={'parent': d.name,'sales_invoice': ["is", "not set"]} ,fields=['sales_invoice','start_date','end_date', 'idx', 'status', 'parent', 'name', 'qty'])
        data.append(d)
        #frappe.msgprint(str( d.name), "Debug")
        for p in dataSubscriptionPeriod:
            #per = []
            p.customer = "--- Period: " + str(p.idx)
            #per.append(p)
            #frappe.msgprint(str(per), "Debug")
            data.append(p)

    return data


def get_Invoicable_entries(customer):
    dataSubscription = frappe.db.get_list('sqSubscriptionItem',filters={'customer': customer} ,fields=['name', 'item', 'autorenew'])
    #frappe.throw(str(data))
    data = []
    for d in dataSubscription:
        dataSubscriptionPeriod = frappe.db.get_list('sqSubscriptionPeriod',filters={'parent': d.name,'sales_invoice': ["is", "not set"]} ,fields=['sales_invoice','start_date','end_date', 'idx', 'status', 'qty', 'name'])
        
        for p in dataSubscriptionPeriod:
            p.item = d.item
            p.autorenew = d.autorenew
            data.append(p)

    #frappe.throw(str(data))
    return data


@frappe.whitelist()
def create_invoice(customer):

    entries = get_Invoicable_entries(customer)
    #frappe.msgprint(str(entries), "Debug")
    sinv = frappe.get_doc({
        'doctype': "Sales Invoice",
        'customer': customer,
        'customer_group': frappe.get_value("Customer", customer, "customer_group")
    })
    
    for e in entries:

        strStart = _('Start')
        strEnd = _('Ende')
        strPeriod = _('Periode')
        strAutorenew = _('Wird erneuert')
        if e.autorenew == True:
            strAutorenewF = _('Wird erneuert') + ":&nbsp;" + _('Yes')
        else:
            strAutorenewF = _('Wird erneuert') + ":&nbsp;" + _('No')

        item = {
            'item_code': e.item,
            'qty': e.qty,
            'rate': frappe.db.get_value('Item Price',{'item_code': e.item}, 'price_list_rate'),
            'description': strPeriod + ":&nbsp;" + str(e.idx) + "<br>" + strStart + ":&nbsp;" + str(e.start_date) + "<br>" + strEnd + ":&nbsp;"+ str(e.end_date) + "<br>" + strAutorenewF,
            'remarks': "-"
        }
        sinv.append('items', item)
        
    sinv.insert()

    for e in entries:
        d = frappe.get_doc('sqSubscriptionPeriod', e.name)
        d.db_set('sales_invoice', sinv.name, commit=True)
        d.save(
            ignore_permissions=True, # ignore write permissions during insert
            ignore_version=True # do not create a version record
        )

    frappe.db.commit()
    
    return sinv.name