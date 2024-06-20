from bs4 import BeautifulSoup
import requests
import telebot
from time import sleep
from keep_alive import keep_alive
keep_alive()
# Replace 'YOUR_BOT_TOKEN' with your actual bot token
BOT_TOKEN = '7483677516:AAEfp2vhP9a6p9yvLCOPDMKqzGW-Il_dScE'
CHAT_ID = '-1002063899284'  # Replace with your chat ID
bot = telebot.TeleBot(BOT_TOKEN)
def get_jobs():
    url = "https://nafezly.com/projects?page=1&specialize=development"
    text = requests.get(url).text
    soup = BeautifulSoup(text, 'html.parser')
    project_boxes = soup.find_all('div', class_='project-box')

    jobs = []

    for box in project_boxes:
        des_url=box.find('a', style="color: var(--bg-color-3);")['href']
        html = requests.get(des_url).text
        soupp = BeautifulSoup(html, 'html.parser')
        description = soupp.find('h2', class_='col-12 p-0 naskh font-2 m-0').get_text()
        job_data = {
            "title": box.find('a', style="color: var(--bg-color-3);").get_text(strip=True),
            "description": description,
            "link": box.find('a', style="color: var(--bg-color-3);")['href'],
            "price_range": box.find("span", class_="fal fa-usd-circle").parent.get_text(strip=True).replace("fal fa-usd-circle", "").strip(),
            "time_duration": box.find("span", class_="fal fa-business-time").parent.get_text(strip=True).replace("fal fa-business-time", "").strip(),
            "number_of_offers": box.find("span", class_="fal fa-ballot").parent.get_text(strip=True).replace("fal fa-ballot", "").strip(),
            "time_since_posted": box.find("span", class_="fal fa-clock").parent.get_text(strip=True).replace("fal fa-clock", "").strip(),
            "location": box.find("span", class_="fal fa-map-marker-alt").parent.get_text(strip=True).replace("fal fa-map-marker-alt", "").strip(),
            "status": box.find("span", class_="fas fa-check-circle").parent.get_text(strip=True).replace("fas fa-check-circle", "").strip()
        }
        jobs.append(job_data)
    jobs.reverse()
    return jobs

def send_job_message(job):
    message = f"*{job['title']}*\n\n" \
              f"*الوصف: * {job['description']}\n\n" \
              f"*الرابط: * [Job Link]({job['link']})\n\n" \
              f"*الميزانية: * {job['price_range']}\n\n" \
              f"*المدة المتاحة: * {job['time_duration']}\n\n" \
              f"*عدد المتقدمين: * {job['number_of_offers']}\n\n" \
              f"*تاريخ النشر: * {job['time_since_posted']}\n\n" \
              f"*بلد الناشر: * {job['location']}\n\n" \
              f"*الحالة:* *{job['status']}*"

    # Split the message into chunks of 4096 characters (Telegram's max message size for Markdown)
    # Each chunk will be sent as a separate message
    max_message_length = 4096
    for chunk in split_message(message, max_message_length):
        bot.send_message(CHAT_ID, chunk, parse_mode='Markdown')

def split_message(text, max_length):
    """Split text into chunks of max_length for Telegram messages."""
    if len(text) <= max_length:
        return [text]
    chunks = []
    current_chunk = ""
    for line in text.splitlines():
        if len(current_chunk) + len(line) + 1 <= max_length:
            current_chunk += line + "\n"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = line + "\n"
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

previous_jobs = []

def check_for_new_jobs():
    global previous_jobs
    current_jobs = get_jobs()
    new_jobs = [job for job in current_jobs if job not in previous_jobs]
    for job in new_jobs:
        send_job_message(job)
    previous_jobs = current_jobs

# Start polling for new jobs every 2 minutes
while True:
    try:
        check_for_new_jobs()
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        continue
    sleep(120)
