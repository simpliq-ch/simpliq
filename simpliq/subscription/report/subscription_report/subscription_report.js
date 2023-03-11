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
            fieldname: 'autorenew',
            label: __('Autorenew'),
            fieldtype: 'Check',
			default: true
		}

	],
    "initial_depth": 0,

    onload: function (report) {
        report.page.add_inner_button(__("Create Invoice"), function() {
            console.log("Create invoice for " + frappe.query_report.filters[0].value);
            frappe.call({
                'method': "simpliq.subscription.report.subscription_report.subscription_report.create_invoice",
                'args': {
                    'customer': frappe.query_report.filters[0].value
                },
                'callback': function(response) {
                    frappe.show_alert( __("Created") + ": <a href='/app/sales-invoice/" + response.message
                        + "'>" + response.message + "</a>");
                    frappe.query_report.refresh();
                }
            });

        });
    }
};