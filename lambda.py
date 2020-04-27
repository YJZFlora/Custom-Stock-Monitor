import boto3

def lambda_handler(event, context):
    client = boto3.resource("dynamodb")
    table = client.Table("stock-monitor-user")
    update_buffer = client.Table("stock-monitor-buffer")
    Info = event["Information"]
    for i in range(len(Info)):
        table.put_item(Item={
            "Email": event["Email"], 
            "Stock": Info[i]["Stock"],
            "Buying-Price": Info[i]["Buying-Price"],
            "Frequence": Info[i]["Frequence"],
            "Percent": Info[i]["Percent"]
        })
        update_buffer.put_item(Item={
            "Email": event["Email"], 
            "Stock": Info[i]["Stock"]
        })
    return "OK"
