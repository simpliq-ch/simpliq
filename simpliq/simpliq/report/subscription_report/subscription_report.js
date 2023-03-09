// Copyright (c) 2023, simpliq and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Subscription Report"] = {
	"filters": [
		{
            fieldname: 'customer',
            label: __('Customer'),
            fieldtype: 'Link',
            options: 'Customer',
            default: frappe.defaults.get_user_default('customer')
        },
        {
            fieldname: 'interval',
            label: __('Interval'),
            fieldtype: 'Select',
            options: [
                'Yearly',
                'Monthly'
            ],
            default: 'Yearly',
        }

	]
};
