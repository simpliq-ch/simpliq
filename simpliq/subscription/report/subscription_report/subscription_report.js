// Copyright (c) 2023, simpliq and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Subscription Report"] = {
	"filters": [
		{
            fieldname: 'customer',
            label: __('Customer'),
            fieldtype: 'Link',
            options: 'Customer'
        },
        {
            fieldname: 'enabled',
            label: __('Enabled'),
            fieldtype: 'Check',
			default: true
		}

	],
    "initial_depth": 0
};
