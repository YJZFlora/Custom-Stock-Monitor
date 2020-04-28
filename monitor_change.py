import ssl
import queue
import base64
import getpass
import smtplib
import datetime
import requests
import threading
from Crypto.Cipher import AES
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import boto3
from bs4 import BeautifulSoup
from apscheduler.schedulers.blocking import BlockingScheduler

KEY = getpass.getpass("Please enter the key: ")
T_FORMAT = '%Y/%m/%d %H:%M'
CLIENT = boto3.resource("dynamodb")
table = CLIENT.Table("stock-monitor-user-stock")
buffer = CLIENT.Table("stock-monitor-subscribe-buffer")


# AES Encryption
def add_to_16(value):
    while len(value) % 16 != 0:
        value += '\0'
    return str.encode(value)

def decrypt(key, value):
    aes = AES.new(add_to_16(key), AES.MODE_ECB)
    base64_decrypted = base64.decodebytes(value.encode(encoding='utf-8'))
    decrypted_value = str(aes.decrypt(base64_decrypted), encoding='utf-8').replace('\0','')
    return decrypted_value


def do_job():
    scheduler = BlockingScheduler()
    scheduler.add_job(check_update, 'interval', seconds=10, id='check_update')
    scheduler.start()

def next_time(dt, min_interval):
    # delete seconds and microseconds
    dt = datetime.datetime.strptime(dt.strftime(T_FORMAT), T_FORMAT)
    for i in range(1, min_interval + 1):
        delta = datetime.timedelta(minutes=i)
        nt = dt + delta
        if nt.minute % min_interval == 0:
            return nt

def get_len(dictionary):
    length = 0
    for value in dictionary.values():
        length += len(value)
    return length

def check_price(stock):
    r = requests.get('https://finance.yahoo.com/quote/{0}'.format(stock))
    soup = BeautifulSoup(r.text, features='html.parser')
    price = soup.find_all('div', {'class': 'My(6px) Pos(r) smartphone_Mt(6px)'})[0].find('span').text
    return float(price.replace(',',''))

def send_mail(email, stock, price, percent):
    message = MIMEMultipart('alternative')
    message['Subject'] = 'Stock Monitor Notification'
    message['From'] = SENDER
    message['To'] = email

    text = """\
    Howdy!
    
    The price of stock "{}" you subscribed has changed over {}%, which is ${} now.
    
    CSCE678 Customized Stock Monitoring
    """.format(stock, percent, price)

    part = MIMEText(text, 'plain')
    message.attach(part)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
        server.login(SENDER, PASSWD)
        server.sendmail(SENDER, email, message.as_string())


def check_update():
    now = datetime.datetime.now()
    now = datetime.datetime.strptime(now.strftime(T_FORMAT), T_FORMAT)
    if now not in plans.keys():
        for item in buffer.scan()['Items']:
            time = next_time(datetime.datetime.now(), 5)
            stock = item['Stock']
            email = item['Email']
            plans_lock.acquire()
            plans.setdefault(time, dict()).setdefault(stock, []).append(email)
            plans_lock.release()
            buffer.delete_item(Key=item)
            print(plans)
        return
    min_time = min(plans.keys())
    if now == min_time:
        print("update !")
        plan = plans[min_time]
        plans_lock.acquire()
        del plans[min_time]
        plans_lock.release()
        print(plans)

        class myThread(threading.Thread):
            def __init__(self, threadID, name, q):
                threading.Thread.__init__(self)
                self.threadID = threadID
                self.name = name
                self.q = q
            def run(self):
                process_data(self.name, self.q)

        def process_data(threadName, q):
            while not exitFlag:
                queueLock.acquire()
                if not workQueue.empty():
                    email, stock, price = q.get()
                    queueLock.release()
                    data = table.get_item(Key={'Email': email, 'Stock': stock})['Item']
                    b_price = float(data['Buying-Price'])
                    percent = float(data['Percent'])
                    freq = datetime.timedelta(minutes=int(data['Frequence']))
                    # Dealing with plans
                    plans_lock.acquire()
                    plans.setdefault(min_time + freq, dict()).setdefault(stock, []).append(email)
                    plans_lock.release()
                    print("update {} and {}".format(email, stock))
                    # Decide whether to email
                    if abs((price - b_price) / b_price) > (percent / 100):
                        send_mail(email, stock, price, percent)
                else:
                    queueLock.release()
        
        exitFlag = 0
        queueLock = threading.Lock()
        workQueue = queue.Queue(get_len(plan))
        threads = []
        threadID = 1

        for tName in range(8):
            thread = myThread(threadID, str(tName), workQueue)
            thread.start()
            threads.append(thread)
            threadID += 1

        queueLock.acquire()
        for stock, emails in plan.items():
            price = check_price(stock)
            for email in emails:
                workQueue.put((email, stock, price))
        queueLock.release()

        while not workQueue.empty():
            pass

        exitFlag = 1

        for t in threads:
            t.join()

SENDER = decrypt(KEY, 'pmhJGWg4R34Q3mJGMmKao78VwITmCoFGHgQKhBxneU4=')
PASSWD = decrypt(KEY, '5R7EwsQQ44v50hRsaTWm/A==')
plans = dict()
plans_lock = threading.Lock()

# Initialize plans
plans_lock.acquire()
for item in table.scan()['Items']:
    time = next_time(datetime.datetime.now(), 5)
    stock = item['Stock']
    email = item['Email']
    plans.setdefault(time, dict()).setdefault(stock, []).append(email)
plans_lock.release()
print(plans)

for item in buffer.scan()['Items']:
    buffer.delete_item(Key=item)

do_job()
