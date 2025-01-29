import os
import time
from flask import Flask, jsonify
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()

app = Flask(__name__)

message = Mail(
    from_email='manan228@gmail.com',
    to_emails='manan228@gmail.com')
message.template_id = "d-2891c6a8a72d4a83857fd36807b8841e"

def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    # service = Service(r"D:\Download\chromedriver-win64\chromedriver-win64\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def scrape_jobs():
    driver = init_driver()

    # URL to scrape
    url = "https://www.orioninc.com/careers/jobs/?keyword=&_job_category=technology-and-engineering&_job_location=north-america"
    driver.get(url)

    wait = WebDriverWait(driver, 5)

    try:
        decline_button = wait.until(EC.element_to_be_clickable((By.ID, "hs-eu-decline-button")))
        decline_button.click()

        print("Cookie popup dismissed.")

    except NoSuchElementException:
        print("No cookie popup appeared.")

    except TimeoutException:
        print("Timed out waiting for the cookie popup to be clickable.")

    # Function to load all jobs by clicking the "Load More" button
    def load_all_jobs():
        while True:
            try:
                load_more_button = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "load-more"))
                )

                load_more_button.click()
                print("Load more button clicked")
                time.sleep(3)
            except TimeoutException:
                print("No more 'Load More' button found.")
                break
            except Exception as e:
                print(f"Error while clicking 'Load More': {e}")
                break

    # Call the function to load all jobs
    load_all_jobs()

    # Extract job details
    jobs_data = []
    jobs = driver.find_elements(By.CLASS_NAME, "teaser-search")
    for job in jobs:
        title = job.find_element(By.CLASS_NAME, "article-title").text
        link = job.find_element(By.CLASS_NAME, "article-title").get_attribute("href")
        category = job.find_element(By.CLASS_NAME, "category").text.replace("Category:", "").strip()
        work_type = job.find_element(By.CLASS_NAME, "work-type").text.replace("Work Type:", "").strip()

        jobs_data.append({
                "title": title,
                "link": link,
                "category": category,
                "work_type": work_type
            })

    driver.quit()

    message.dynamic_template_data = {
        "jobs": jobs_data
    }

    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    response = sg.send(message)
    
    return jobs_data

@app.route('/get_jobs', methods=['GET'])
def get_jobs():
    try:    
        jobs_data = scrape_jobs()
        return jsonify(jobs_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
