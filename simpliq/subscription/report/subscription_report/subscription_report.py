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


def get_Invoivable_entries(customer):
    dataSubscription = frappe.db.get_list('sqSubscriptionItem',filters={'customer': customer} ,fields=['name', 'item'])
    #frappe.throw(str(data))
    data = []
    for d in dataSubscription:
        dataSubscriptionPeriod = frappe.db.get_list('sqSubscriptionPeriod',filters={'parent': d.name,'sales_invoice': ["is", "not set"]} ,fields=['sales_invoice','start_date','end_date', 'idx', 'status', 'qty', 'name'])
        
        for p in dataSubscriptionPeriod:
            p.item = d.item
            
            data.append(p)
        data.append(p)
    #frappe.throw(str(data))
    return data


@frappe.whitelist()
def create_invoice(customer):

    entries = get_Invoivable_entries(customer)
    #frappe.msgprint(str(entries), "Debug")
    sinv = frappe.get_doc({
        'doctype': "Sales Invoice",
        'customer': customer,
        'customer_group': frappe.get_value("Customer", customer, "customer_group")
    })
    
    for e in entries:
        
        item = {
            'item_code': e.item,
            'qty': e.qty,
            'rate': 99,
            'description': "Test description",            # will be overwritten by frappe
            'remarks': "Test remakrks"

        }
        sinv.append('items', item)
        
    sinv.insert()


    # insert abo references
    for e in entries:
        docSubscriptionPeriod = frappe.get_doc("sqSubscriptionPeriod", e.name)
        docSubscriptionPeriod.db_set('sales_invoice', sinv.name)
        docSubscriptionPeriod.save()
        
    frappe.db.commit()
    
    return sinv.name