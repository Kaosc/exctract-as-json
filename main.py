from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import warnings
import time
import json

warnings.filterwarnings("ignore", category=DeprecationWarning)

class Exctractor:
   def __init__(self):
      self.questions = []
      self.drvPath = "./driver/chromedriver.exe"
      self.service = Service(self.drvPath)
      self.browserProfile = webdriver.ChromeOptions()
      self.browserProfile.add_argument("--lang=en")
      self.browserProfile.add_argument("--enable-features=WebContentsForceDark")
      self.browserProfile.add_argument("--log-level=3")
      self.browserProfile.add_argument('--hide-scrollbars')
      self.browserProfile.add_argument("--headless")
      self.browserProfile.add_argument("--disable-gpu")
      self.browserProfile.add_argument('--mute-audio')
      self.browserProfile.add_argument('window-size=1920,1080')
      self.browserProfile.add_argument('window-position=0,0')
      self.browserProfile.add_argument("--start-maximized")
      self.browserProfile.add_argument("--force-dark-mode")
      self.browserProfile.add_experimental_option("excludeSwitches", ["disable-popup-blocking"])
      self.browserProfile.add_experimental_option('prefs', {"profile.default_content_setting_values.notifications": "2"})
      self.browserProfile.add_experimental_option('excludeSwitches', ['enable-logging'])
      self.browserProfile.add_experimental_option('prefs', {"intl.accept_languages": "en,en_US"})
      self.browser = webdriver.Chrome(service=self.service, options=self.browserProfile)

   def getUrls(self, baseUrl):
      urls = []

      self.browser.get(baseUrl)
      time.sleep(3)

      aList = self.browser.find_elements(By.XPATH, '//*[@class="aq-quizzes"]/li/a')

      for a in aList:
         urls.append(a.get_attribute("href"))

      return urls

   def extract(self, url, index, total, name):
      print(f"Crawling: {index}/{total} - {name}")

      self.browser.get(url)
      time.sleep(3)

      # click to button to show all
      self.browser.find_element(By.XPATH, '//*[@id="quizForm"]/a').click()
      time.sleep(2)

      # click to button and of the page
      self.browser.find_element(By.XPATH, '//*[@id="ariQueMainAnsContainer"]/div[4]/a').click()
      time.sleep(1)
      self.browser.switch_to.alert.accept()
      time.sleep(2)

      try:
         dropDownOptions = self.browser.find_elements(By.XPATH, '//*[@id="yui-pg0-0-rpp14"]/option')
         dropDownOptions[-1].click()
         time.sleep(3)
      except:
         pass

      trs = self.browser.find_elements(By.XPATH, '//*[@class="aq-question-panel-content"]')

      # Loop through all questions
      for tr in trs:
         question = {
            "question": {
               "TR": "",
               "EN": ""
            },
            "answers": {
               "TR": [],
               "EN": []
            },
            "correctAnswer": {
               "TR": "",
               "EN": ""
            },
         }

         # get question
         question["question"]["TR"] = tr.find_element(By.CLASS_NAME, "aq-question-content").text
         
         # get image
         try:
            question.__setitem__("questionImage", {
               "uri": tr.find_element(By.CLASS_NAME, "aq-question-content").find_element(By.TAG_NAME, "img").get_attribute("src") 
            }) 
         except:
            pass
         
         # get answers
         answers = tr.find_elements(By.CLASS_NAME, "aq-answer")
         for answer in answers:
            question["answers"]["TR"].append(answer.text)

         # get correct answer
         tbody = tr.find_element(By.TAG_NAME, "tbody")
         correctAnswerTrs = tbody.find_elements(By.TAG_NAME, "tr")
         del correctAnswerTrs[0]
         
         correctAnswerIndex = 0
         for i in range(len(correctAnswerTrs)):
            try: 
               correctAnswerTrs[i].find_element(By.TAG_NAME, "i")
               correctAnswerIndex = i
               break
            except:
               pass

         try:
            question["correctAnswer"]["TR"] = question["answers"]["TR"][correctAnswerIndex]
         except:
            print(f"Error: correct answer not found - {question['question']['TR']}")

         self.questions.append(question)

   def writeToFile(self, name):
      with open(f"{name}.json", "w", encoding="utf-8") as file:
         file.write("[")
         file.write("\n")
      for question in self.questions:
         seriliazedQuestion = json.dumps(question, indent=4, ensure_ascii=False)
         with open(f"{name}.json", "a", encoding="utf-8") as file:
            file.write(seriliazedQuestion + ",\n")
      with open(f"{name}.json", "a", encoding="utf-8") as file:
         file.write("]")

      self.questions = []
      
exctractor = Exctractor()

baseUrls = []

for baseUrl in baseUrls:
   name = baseUrl["name"]
   url = baseUrl["url"]

   print(f"Base url: {name}")
   urlList = exctractor.getUrls(url)

   total = len(urlList)

   for i in range(0, len(urlList)):
      exctractor.extract(urlList[i], i, total, name), 

   exctractor.writeToFile(name)
