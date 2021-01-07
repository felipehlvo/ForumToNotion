import notion
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import os
import selenium
from selenium import webdriver
import time
from PIL import Image
import io
import requests
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from notion.client import *
from notion.block import *
from notion.client import NotionClient

# Optionally, to speed up the process, define the token_v2 and the collection view below

token = "" # Puth the token_v2 here as a string
link_cv = "" # Put the collection view link here as a string


def AccessNotion():
    #Security
    global client
    try:
        client = NotionClient(token_v2 = token)
    except:
        pass
    while ('client' not in globals()) or type(client) != notion.client.NotionClient:
        token = input("Please paste your Notion token: ")
        try:
            client = NotionClient(token_v2 = token)
        except:
            print("Something went wrong. Is your token correct?")
    print("ACCESS GRANTED.")

def GetCollectionView():
    global cv
    # Get Colletions
    try:
        cv = client.get_collection_view(link_cv)
    except:
        pass
    while ('cv' not in globals()) or ((type(cv) != notion.collection.BoardView) and (type(cv) !=notion.collection.TableView)):
        link_cv = input("Please paste link to collection view: ")
        try:
            cv = client.get_collection_view(link_cv)
        except:
            print("Something went wrong. Is your link correct?")
    print("DATABASE FOUND.")

def CreatePage():
    print("Creating Page...")
    global session
    session = cv.collection.add_row()
    


    # Go to recently created session page
    global page
    page = client.get_block(session.id)
    page.title = soup.find('h1').text

    

    # Clean Page
    for block in page.children:
        block.remove()

    #In-class Notes
    CreateInclassNotes()
    

    # Readings
    CreateReadings()
    
    # Study Guide
    CreateStudyGuide()

    # Pre-class
    CreatePreclass()
    
    # Session Properties
    DefineProperties()
    
    print("You page is ready! Access it here: " + page.get_browseable_url())
            
def CreateInclassNotes():
    global page
    print("Formatting In-class Notes...")
    notes = page.children.add_new(SubheaderBlock,
                                  title="In-class Notes",
                                  color="yellow")
    divider0 = page.children.add_new(DividerBlock)
    page.children.add_new(TextBlock, title="")
    print("Done \n")
    
    
def CreateReadings():    
    global count
    print("Formatting Readings...")
    readings = page.children.add_new(SubheaderBlock, title="Readings", color="orange")
    divider1 = page.children.add_new(DividerBlock)

    readings_titles = soup.find_all('h4')[1:]
    descriptions = soup.find("div", {"class": "description underlined-links"})
    count = 0
    global links
    links = []
    for title in readings_titles:
        print("   - " + title.text)
        CreateReading(title)
    print("Done \n")
    

def CreateReading(title):
        global count
        global links
        quote = title.find_next_sibling("blockquote")
        if title.find_next_sibling().name == "p" and title.find_next_sibling().findChild().name == "a":
            count+=1
            try:
                link = title.find_next_sibling("p").findChild()
                links.append(link.get("href"))
                cur_reading = page.children.add_new(ToggleBlock,
                                  title="[{0}]({1})".format(title.text,
                                                            link.text))
            except:
                cur_reading = page.children.add_new(ToggleBlock, title = title.text)
        else:
            cur_reading = page.children.add_new(ToggleBlock, title = title.text)

        # Content of toggle    
        cur_reading.children.add_new(TextBlock, title="**Objective:**", color = "grey")
        cur_reading.children.add_new(TextBlock, title=html_to_markdown(quote.text))
        cur_reading.children.add_new(TextBlock, title="**Notes:**")
        cur_reading.children.add_new(TextBlock, title="")
        cur_reading.children.add_new(TextBlock, title="**Summary:**")
        cur_reading.children.add_new(TextBlock, title="")
        
def CreateStudyGuide(color = "blue"):
    print("Formatting Study Guide...")
    study_guide = page.children.add_new(SubheaderBlock,
                                        title="Study Guide",
                                        color=color)
    divider2 = page.children.add_new(DividerBlock)

    prestudy = soup.find_all('h3')[3]
    study_text = prestudy.find_previous_siblings(['p', 'pre'])

    page.children.add_new(TextBlock, title=html_to_markdown(study_text[:-count]))
    print("Done \n")
    
def CreatePreclass(color = "green"):
    print("Formatting Pre-Class...")
    Preclass = page.children.add_new(SubheaderBlock, title="Pre-class", color=color)
    divider2 = page.children.add_new(DividerBlock)

    prepreclass = soup.find_all('h3')[3]
    preclass_text = prepreclass.find_next_siblings()
    preclass_mark = html_to_markdown(preclass_text)

    page.children.add_new(TextBlock, title=preclass_mark)
    print("Done \n")
    
def DefineProperties():
    global session
    print("Defining Class Properties...")
    session.name = soup.find('h1').text[1:]
    session.course = soup.find('h1').text.split()[0]
    session.class_link = soup.find('h1').findChild('a').get('href')
    session.materials = links
    session.reviewed = False
    hcs = ["#" + i.text.split("-")[-1] for i in soup.find_all('a', "hash-link")]
    
    try:
        session.hcs_los = hcs
    except:
        session.hcs_los = ", ".join(hcs)
    print("Done \n")
    
def html_to_markdown(html):
    markdown = ''
    for i in html:
        markdown+=md(str(i).replace("<code>", "`").replace("</code>", "`"), strip = ['pre']) 
    return markdown

def login():
    driver.get("https://forum.minerva.kgi.edu/")
    
    main_window_handle = None
    while not main_window_handle:
        main_window_handle = driver.current_window_handle
    time.sleep(5)
    login_button = driver.find_element_by_xpath("//button[1]")
    login_button.click()

    signin_window_handle = None
    while not signin_window_handle:
        for handle in driver.window_handles:
            if handle != main_window_handle:
                signin_window_handle = handle
                break

    driver.switch_to.window(signin_window_handle)
    
    mail_address = input("E-mail: ")
    password = input("Password: ")
    
    try:
        
        driver.find_element_by_id("identifierId").send_keys(mail_address)
        driver.find_element_by_id("identifierNext").click()
        driver.implicitly_wait(2)


        driver.find_element_by_name("password").send_keys(password)
        driver.find_element_by_id("passwordNext").click()
    except:
        "Wrong credentials"

    time.sleep(10)
    driver.switch_to.window(main_window_handle)
   




AccessNotion()

GetCollectionView()

### AUTOMATIC LOGIN, (currently not working) ### 

# try:
#     del test_login
# except:
#     pass
    
# while ("test_login" not in locals()) or (test_login == None):
#     driver = webdriver.Chrome(ChromeDriverManager().install())
#     wait = WebDriverWait(driver, 10)
#     login()

    
#     soup = BeautifulSoup(driver.page_source, "html.parser")
#     test_login = soup.find('a', 'navigation-link ')
#     if test_login == None:
#         print("Something went wrong with the login")

###    ########  ####

# Opening Chrome
driver = webdriver.Chrome(ChromeDriverManager().install())
driver.get("https://forum.minerva.kgi.edu/")
print("Go to the newly opened Chrome page and login to Forum. After that, come back to the notebook and follow the code outputs.")

# Wait untl login
try:
    element = WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.CLASS_NAME, "navigation-link "))
    )
except:
    print("You took too long to login")
    driver.quit()


make_another = "Yes"
url = input("URL to class (type 'stop' to exit): ")
while make_another == 'Yes':
    try:
        driver.get(url)
    except:
        print("Couldn't find page with this url.")
        continue

    time.sleep(5)
    
    # Scraping page
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Create New Notion Page
    class_link = soup.find('h1').findChild('a').get('href')
    if class_link in [row.class_link for row in cv.collection.get_rows()]:
        make_duplicate = input("Class already exists. Do you want to make a copy? (Yes/No)")
        if make_duplicate == "Yes":
            CreatePage()
    else:
        CreatePage()
        
    while make_another != ("Yes" or "No"):
        make_another = input("Another class? (Yes/No): ")
    

