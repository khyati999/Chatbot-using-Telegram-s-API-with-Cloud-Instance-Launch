import os
import telebot
from dotenv import load_dotenv
import boto3

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
ec2_client=None
instance_id=None
 
 #Say Hello to Users
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message,""" 
        What can this bot do?
        This bot can help you launch ec2 instance!!
        You can control me by sending following commands:
        
        /hello- Bot greetings
        /login_aws- help you login in aws account.
        /launch_instance- launch instance
        /terminate_ins- terminate the instance 
                 
 """)

@bot.message_handler(commands=['hello'])
def send_welcome(message):
    bot.reply_to(message, "Hello, how are you doing?")


@bot.message_handler(commands=['login_aws'])
def login_aws(message):
    # Start the login process by asking for AWS credentials
    bot.reply_to(message, "Please enter your AWS Access Key:")
    bot.register_next_step_handler(message, get_access_key)

def get_access_key(message):
    # Store the AWS Access Key in a variable
    global access_key
    access_key = message.text
    bot.reply_to(message, "Great! Now, please enter your AWS Secret Access Key:")
    bot.register_next_step_handler(message, get_secret_access_key)

def get_secret_access_key(message):
    # Store the AWS Secret Access Key in a variable
    global secret_access_key
    secret_access_key = message.text
    bot.reply_to(message, "Thank you. Please enter your AWS region (e.g., us-east-1):")
    bot.register_next_step_handler(message, get_aws_region)

def get_aws_region(message):
    # Store the AWS region in a variable
    global region
    region = message.text
    global ec2_client
    ec2_client=boto3.client(
        'ec2',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_access_key,
        region_name=region
    )
    if ec2_client:
        bot.reply_to(message, "You are now logged into your AWS account.")
    else:
        bot.reply_to(message, "Login failed. Please check your credentials and try again.")

@bot.message_handler(commands=['launch_instance'])
def launch_instance(message):
    global ec2_client
    global instance_id
    if ec2_client:
        try:
            response = ec2_client.run_instances(
                ImageId='ami-0287a05f0ef0e9d9a',
                MinCount=1,
                MaxCount=1,
                InstanceType='t2.micro',
                KeyName='bot'
            )
            instance_id = response['Instances'][0]['InstanceId']
            bot.reply_to(message, f'Launched EC2 instance: {instance_id}')
        except Exception as e:
            bot.reply_to(message, f"Failed to launch EC2 instance. Error: {str(e)}")
    else:
        bot.reply_to(message, "Please log in to your AWS account first.")

@bot.message_handler(commands=['terminate_ins'])
def terminate(message):
    global instance_id
    if ec2_client:
        try:
            if instance_id:
                response = ec2_client.terminate_instances(InstanceIds=[instance_id])
                if response['TerminatingInstances'][0]['CurrentState']['Name'] == 'shutting-down':
                    bot.reply_to(message, f'Terminating EC2 instance: {instance_id}')
                else:
                    bot.reply_to(message, f"Failed to terminate EC2 instance.")
            else:
                bot.reply_to(message, "Instance ID is not available. Please launch an instance first.")
        except Exception as e:
            bot.reply_to(message, f"Failed to terminate EC2 instance. Error: {str(e)}")
    else:
        bot.reply_to(message, "Please log in to your AWS account first.")
bot.infinity_polling()
