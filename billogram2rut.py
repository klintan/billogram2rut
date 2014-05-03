#Billogram2RUT
import requests
from billogram_api import BillogramAPI, BillogramExceptions

#connect to the API
username = ''
authkey = ''
api = BillogramAPI(username, authkey)

#get all invoices that are not marked as "Done" in ROT/RUT
def get_nonRUT_invoice(api):
	query = api.billogram.query()
	query.filter_state_any('Paid')

	#get the 10 latest invoice objects that are "Paid"
	query.page_size = 10
	bgs = query.get_page(1)
	if not bgs:
		print("No billogram found")
		return

	with open('rut_ansokan.xml', 'w') as xml_file:
		xml_file.write('<?xml version="1.0" encoding="UTF-8" standalone="no" ?>')
		xml_file.write('<HtAnsokan xmlns="se/skatteverket/hunten/ansokan/2.0" xmlns:htko="se/skatteverket/hunten/komponent/2.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">')
		xml_file.write('<htko:AnsokningsNr>{request_number}</htko:AnsokningsNr>'.format(request_number = "12"))
		xml_file.write('<htko:HushallAnsokan>')

		for idx,bg in enumerate(bgs):
			bg = bgs[idx]
			bg.refresh()
			total_invoiced_sum = bg['total_sum']+bg['regional_sweden']['rotavdrag']*1.25
			rut_requested = bg['regional_sweden']['rotavdrag']*1.25
			print bg['customer']['name']
			print "Fakturannummer"
			print bg['invoice_no']
			print bg['flags']
			for ev in bg['events']:
				if ev['type'] == "Payment":
					print ev['created_at']
					#print bg['events']
					print "Betalat Belopp"
					print ev['data']['amount']
					payment_date = ev['created_at']
					payment_done = ev['data']['amount']

			xml_file.write('<htko:Arenden>')
			xml_file.write('<htko:Kopare>19{personal_number}</htko:Kopare>'.format(personal_number=bg['regional_sweden']['rotavdrag_personal_number'].replace('-', '')))
			xml_file.write('<htko:BetalningsDatum>{payment_date}</htko:BetalningsDatum>'.format(payment_date=payment_date.split(' ', 1)[0]))
			xml_file.write('<htko:FaktureratBelopp>{total_invoiced_sum}</htko:FaktureratBelopp>'.format(total_invoiced_sum=int(total_invoiced_sum)))
			xml_file.write('<htko:BetaltBelopp>{payment_done}</htko:BetaltBelopp>'.format(payment_done=payment_done))
			xml_file.write('<htko:BegartBelopp>{rut_requested}</htko:BegartBelopp>'.format(rut_requested=int(rut_requested)))
			xml_file.write('<htko:FakturaNr>{invoice_number}</htko:FakturaNr>'.format(invoice_number=bg['invoice_no']))
			xml_file.write('</htko:Arenden>')

	    
		xml_file.write('</htko:HushallAnsokan>')
		xml_file.write('</HtAnsokan>')
		xml_file.close()


#set RUT/ROT to "Done" for each invoice in the report.
def find_update_example(api):
    qry = api.items.query()

    qry.filter_search('title', 'gadget')

    for item in qry.iter_all():
        item.update({
            'price': item['price']*1.1
        })


get_nonRUT_invoice(api)