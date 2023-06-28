def paytm_payment_process(request):
    # o_id = request.GET['o_id'
    o_id = request.GET.get('o_id')
    # print(o_id)
    order=Order.objects.get(id=o_id)
    email=order.email
    # cart=order.cart
    # print(order.order_status,order.total)
    param_dict = {

        'MID': 'PLtXFQ32092519130257',
        'ORDER_ID': str(order.id),
        'TXN_AMOUNT': str(order.total),
        'CUST_ID': email,
        'INDUSTRY_TYPE_ID': 'Retail',
        'WEBSITE': 'WEBSTAGING',
        'CHANNEL_ID': 'WEB',
        'CALLBACK_URL': 'http://127.0.0.1:8000/handlerequest/',

    }

    from PayTm import Checksum
    MERCHANT_KEY = 'Please Type your merchant Key'
    param_dict['CHECKSUMHASH'] = checksum.generate_checksum(param_dict, MERCHANT_KEY)
    return render(request, 'paytm.html', {'param_dict': param_dict})