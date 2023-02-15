from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
import time
import os
import re
from tkinter import *

DRIVER_LOCATION = os.environ['DRIVER_LOCATION']

career = None
topics = None
num_to_check = 1


# This is the function that is called when the user hits the search button on the Tkinter window
def search():
    global career
    global topics
    global num_to_check
    career = career_input.get()
    topics = topic_input.get()
    if career and topics and num_to_check:
        try:
            num_to_check = int(num_input.get())
            window.destroy()

        except ValueError:
            num_warning = Label(text="Please input a number (e.g. 50) for how many job postings you want to search",
                                fg="red")
            num_warning.grid(columnspan=2,
                             column=0,
                             row=6)
    else:
        warning_label = Label(text="Please input a job, your desired topics, and the number of postings to search",
                              fg='red')
        warning_label.grid(columnspan=2,
                           column=0,
                           row=5)


# This is a recursive function that gets the links for the different job postings
def get_links(start_link, all_text, num_checked, to_check):
    try:
        if num_checked < to_check:
            start_link.click()

            new_elements = driver.find_elements(by=By.CSS_SELECTOR,
                                                value='#gws-plugins-horizon-jobs__job_details_page')

            new_el = new_elements[num_checked]
            new_content = new_el.get_attribute('innerHTML').strip().lower()
            all_text += new_content

            new_links = driver.find_elements(by=By.CSS_SELECTOR,
                                             value='.gws-plugins-horizon-jobs__tl-lif')
            num_checked += 1

            try:
                start_link = new_links[num_checked]
            except IndexError:
                print("The number of available posts was smaller than the desired search amount")
                return all_text, num_checked
            return get_links(start_link, all_text, num_checked, to_check)

        else:
            return all_text, num_checked

    except NoSuchElementException or ElementNotInteractableException:
        print("The number of available posts was smaller than the desired search amount")
        return all_text, num_checked


# This is the code for the Tkinter window
window = Tk()
window.title('Job Skill Searcher')

window.config(padx=100,
              pady=100)

career_label = Label(text="What job do you want to search?",
                     justify='right')
career_label.grid(column=0,
                  row=1,
                  pady=10)
career_input = Entry(width=60)
career_input.grid(column=1,
                  row=1)

topic_label = Label(text="Type what topics you want to search with a comma a space between each topic",
                    justify='right',
                    padx=10,
                    pady=10)
topic_label.grid(column=0,
                 row=2)
topic_input = Entry(width=60)
topic_input.grid(column=1,
                 row=2)

num_label = Label(text="How many job postings do you want to check?",
                  justify="right",
                  pady=10)
num_label.grid(column=0,
               row=3)
num_input = Entry(width=30)
num_input.grid(column=1,
               row=3)

submit_button = Button(text='Submit',
                       width=20,
                       command=search)
submit_button.grid(columnspan=2,
                   column=0,
                   row=4)

window.mainloop()

# This makes sure that the whole program won't run unless there were correctly input values
if career and topics and num_to_check != 1:
    service = Service(executable_path=DRIVER_LOCATION)
    driver = webdriver.Chrome(service=service)

    driver.get('https://www.google.com/')
    search_bar = driver.find_element(by=By.CSS_SELECTOR,
                                     value='input')
    search_bar.send_keys(career, ' jobs')
    search_bar.send_keys(Keys.ENTER)
    time.sleep(0.2)

    # This gets the first job link, the first job text, and then calls the get_links() function
    try:
        first_link = driver.find_element(by=By.CSS_SELECTOR,
                                         value='.gws-plugins-horizon-jobs__li-ed')
        first_link.click()

        text = driver.find_element(by=By.CSS_SELECTOR,
                                   value='#gws-plugins-horizon-jobs__job_details_page')
        text_content = text.get_attribute('innerHTML').strip().lower()

        links = driver.find_elements(by=By.CSS_SELECTOR,
                                     value='.gws-plugins-horizon-jobs__tl-lif')
        first_job = links[1]

        search_text = topics.split(", ")

        new_text, num_jobs = get_links(first_job, text_content, 0, num_to_check)

        filtered_text = re.sub('<[^>]+>', '', new_text)

        # Creates a dictionary for the search terms and the number of times they have been referenced
        count_dict = {}
        for word in search_text:
            count_dict[word] = 0

        for word in search_text:
            count_dict[word] += len(re.findall(word.lower(), filtered_text))

        # Displays results
        print(f"\nOut of {num_jobs} job postings, this is the number of references for each topic:\n")

        for word in search_text:
            print(f"{word} has been referenced {count_dict[word]} times")

    except NoSuchElementException:
        print("It seems that there are no job postings for that position. Please try again.")

else:
    print("The program has ended without running")
