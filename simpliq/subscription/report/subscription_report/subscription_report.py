# Copyright (c) 2023, simpliq and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import today,getdate,add_to_date



def execute(filters=None):
    columns, data = [], []      
    columns = get_columns()
    data = get_data(filters)
    report_summary = get_summary(filters)
    return columns, data, _("<h3>Summary of all Customers</h3>"), None, report_summary


def get_columns():
    return [
        {'fieldname': 'customer', 'label': 'Customer', 'fieldtype': 'Link', 'options': 'Customer', 'width': 180},
        {'fieldname': 'name', 'label': 'Subscription', 'fieldtype': 'Link', 'options': 'sqSubscriptionItem','width': 100},
        #{'fieldname': 'autorenew', 'label': 'Autorenew', 'fieldtype': 'Check', 'width': 100},
        {'fieldname': 'item', 'label': 'Item', 'fieldtype': 'Link', 'options': 'Item', 'width': 250},
        {'fieldname': 'start_date', 'label': 'Start Date', 'fieldtype': 'Date', 'width': 95},
        {'fieldname': 'end_date', 'label': 'End Date', 'fieldtype': 'Date', 'width': 95},
        {'fieldname': 'qty', 'label': 'Quantity', 'fieldtype': 'Float', 'width': 80},
        {'fieldname': 'rate', 'label': 'Price', 'fieldtype': 'Currency', 'width': 100}
    ]

def get_data(filters):

    dataSubscription = frappe.db.get_list('sqSubscriptionItem',filters={'customer': filters.customer} ,fields=['customer', 'autorenew', 'item', 'name'])
    #frappe.throw(str(data))
    data = []
    for d in dataSubscription:
        dataSubscriptionPeriod = frappe.db.get_list('sqSubscriptionPeriod',filters={'parent': d.name,'sales_invoice': ["is", "not set"]} ,fields=['sales_invoice','start_date','end_date', 'idx', 'status', 'parent', 'name', 'qty'])
        d.indent = 0
        totalAmount = 0
        for p in dataSubscriptionPeriod: 
            totalAmount += (frappe.db.get_value('Item Price', {'item_code': d.item,}, 'price_list_rate') * p.qty)
        d.rate = totalAmount
        data.append(d)
        #frappe.msgprint(str( d.name), "Debug")
        for p in reversed(dataSubscriptionPeriod):
            #per = []
            p.customer = "Period: " + str(p.idx)
            p.name = "-"
            p.rate = (frappe.db.get_value('Item Price', {'item_code': d.item,}, 'price_list_rate') * p.qty)
            p.indent = 1
            data.append(p)

    return data


def get_summary(filters):
    
    numOfOPenPeriods,totalAmountOfOpenPeriods = 0,0
    customerList = []
    customerString = ""
    dataSubscription = frappe.db.get_list('sqSubscriptionItem',fields=['customer', 'item', 'name'])

    for d in dataSubscription:
        dataSubscriptionPeriod = frappe.db.get_list('sqSubscriptionPeriod',filters={'parent': d.name, 'sales_invoice': ["is", "not set"]} ,fields=['qty'])
        if dataSubscriptionPeriod: 
            if d.customer not in customerList:
                customerList.append( d.customer)
            for p in dataSubscriptionPeriod:
                totalAmountOfOpenPeriods += (frappe.db.get_value('Item Price', {'item_code': d.item,}, 'price_list_rate') * p.qty)

    totalAmountOfOpenPeriodsStr = str(totalAmountOfOpenPeriods) + " CHF"
    dataSubscriptionPeriodAll = frappe.db.get_list('sqSubscriptionPeriod',filters={'sales_invoice': ["is", "not set"]} ,fields=['sales_invoice','start_date','end_date', 'idx', 'status', 'parent', 'name', 'qty'])

    for c in customerList:
        customerString += c + "<br>"

    return [
        {
            'value' : customerString,
            #'indicator' : '',
            'label' : _('Open Subscriptions'),
            'datatyp' : 'Text',
        },
        {
            'value' : len(dataSubscriptionPeriodAll),
            'indicator' : 'Red',
            'label' : _('Num. of open Periods'),
            'datatyp' : 'Int',
        },
        {
            'value' : totalAmountOfOpenPeriodsStr,
            'indicator' : 'Green',
            'label' : _('Amount'),
            'datatyp' : 'Text',
        },
    ]


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

@frappe.whitelist()
def check_newperiod(customer):
    dataSubscription = frappe.db.get_list('sqSubscriptionItem',filters={'autorenew': True} ,fields=['customer', 'autorenew', 'name'])
    r = "nothing added" 
    for d in dataSubscription:

        next = True

        while next:
            #dataSubscriptionPeriod = frappe.db.get_list('sqSubscriptionPeriod',filters={'parent': d.name,'end_date': ["<=", add_to_date(today(), months=1)]} ,fields=['start_date','end_date', 'parent', 'name', 'qty'])
            lastperiod = frappe.get_last_doc('sqSubscriptionPeriod', filters={"parent": d.name}, order_by='end_date desc')

            #frappe.msgprint(str(add_to_date(today(), months=1, as_datetime=True)), "Debug")
            if getdate(lastperiod.end_date) <= getdate(add_to_date(today(), months=1, as_datetime=True)):
                period = frappe.new_doc('sqSubscriptionPeriod')
                period.qty = lastperiod.qty
                period.parent = lastperiod.parent
                period.parenttype = lastperiod.parenttype
                period.parentfield = lastperiod.parentfield
                period.idx = lastperiod.idx + 1
                periodlength = abs(lastperiod.start_date-lastperiod.end_date).days
                if periodlength >= 365: #YEAR SUBSCRIPTION
                    period.end_date = add_to_date(lastperiod.end_date, years=1)
                    period.start_date = add_to_date(lastperiod.start_date, years=1)
                elif periodlength >= 28: #MONTH SUBSCRIPTION
                    period.end_date = add_to_date(lastperiod.end_date, months=1)
                    period.start_date = add_to_date(lastperiod.start_date, months=1)
                else: #DAYS SUBSCRIPTION
                    period.end_date = add_to_date(lastperiod.end_date, days=periodlength)
                    period.start_date = add_to_date(lastperiod.start_date, days=periodlength)
                period.insert()
                frappe.db.commit()
                r = "new periods added" 
            else:
                next = False
        #frappe.msgprint(str(len(dataSubscriptionPeriod)), "Debug")
    
    return r