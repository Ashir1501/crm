import random
import pytz 
from datetime import datetime, date, timedelta
from django.core.management.base import BaseCommand, CommandParser
from crmManagerApp.models import Customer, Interaction, Deal, Task
from userManagerApp.models import Assigner

class Command(BaseCommand):
    help = 'Populates the database with random generated data'

    def add_arguments(self, parser: CommandParser):
        parser.add_argument('--amount',type=int,help='the number of customers should be created')


    def handle(self, *args, **options):
        names = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles",'kirk','Drake','Gojo','Guta','Rock','Kevin','Xavier','Jaden','kartik','Travis','Tarun','Nick','Peter','Sheldon','Malcom']
        surname = ["Smith", "Jones", "Taylor", "Brown", "Williams", "Wilson", "Johnson", "Davies", "Patel", "Wright",'Blight','Rahul','Pranav','Mahesh','Tanmay','Alexa','Will','Shantanu','Jakson','Akumala','Fury','Parker','Milton','Blinkin']
        normal_user = ['nu_loyd','nu_steve']
        manager_user = ['mu_lynda','mu_rachel']
        company = ['foogle','google','microsoft','amazone','united','mintra','flipkart','meta','tata','mahindra','hansung','samsung','toyota','perplexity','openai','apple','spacex']
        dtitle = ['ERP system', 'Product Tracking System', 'Food Delivery System','Large Language Model','API','Inventory Management System','OpenCV Face Recognition System','Ecommerce-Website','Image Editing App','AI Chatbot']
        ttitle = ['planning','implementing','development','deployment','testing','reviewing','architecture planning']
        damount = ['10000','15000','20000','25000','30000','35000','40000','45000','50000','55000','60000','13000','17000','23000']
        #taking amount from command line if not then 500
        amount = options["amount"] if options["amount"] else 500
        for i in range(0, amount):
            dt = pytz.utc.localize(datetime.now() - timedelta(days=random.randint(0, 1825))).date()
            custName=random.choice(names) + " " + random.choice(surname)
            custEmail = custName.replace(' ','') + '@gmail.com'
            phone = ''
            phone += str(random.randint(6,9))
            for j in range(1,10):
                phone += str(random.randint(0,9))
            # creating Customer object
            customer = Customer.objects.create(
                customer_name = custName,
                customer_email = custEmail,
                customer_phone = phone,
                customer_company = random.choice(company),
                arrived_date = dt,
                deal_won=True if random.randint(1, 2) == 1 else False,
                deal_assigned= False,
                custRegiteredByUser = random.choice(normal_user)
            )
            if(customer.deal_won == True):
                #assigining manager to customer
                asign = Assigner.objects.create(
                    customer = customer,
                    manager_name = random.choice(manager_user)
                )
                asign.save()
                dn = random.randint(0,5)
                #a customer can have any number of deals i've taken 0-5
                for d in range(0,dn):
                    deal = Deal.objects.create(
                        deal_title = random.choice(dtitle),
                        deal_status=random.choice(Deal.status_option)[0],
                        deal_amount = str(random.choice(damount)),
                        deal_withCustomer = asign.customer,
                        dealCreatedByUser = asign.manager_name,
                        deal_initiationDate = customer.arrived_date + timedelta(days=d*d),
                        deal_expectedCloseDate = customer.arrived_date +timedelta(days=d*d) + timedelta(days=3 * 30)
                    )
                    customer.deal_assigned = True
                    customer.save()
                    deal.save()
                    tn = random.randint(0,5)
                    #creating task object and a deal can have certain amount of task i've taken 0-5
                    for t in range(0,tn):
                        task = Task.objects.create(
                            task_title = random.choice(ttitle),
                            task_status = random.choice(Task.status_option)[0],
                            task_relatedToDeal = deal,
                            taskCreatedByUser = deal.dealCreatedByUser,
                            task_dueDate = deal.deal_initiationDate + timedelta(days=(t*t)+1)
                        )
                        task.save()          
        self.stdout.write(self.style.SUCCESS("Successfully populated the database."))

        