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

   def extract(self, url, index, total):
      print(f"Crawling: {index}/{total}")

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
            "questionImage": ""
         }

         # get question
         question["question"]["TR"] = tr.find_element(By.CLASS_NAME, "aq-question-content").text
         
         # get image
         try:
            question["questionImage"] = tr.find_element(By.CLASS_NAME, "aq-question-content").find_element(By.TAG_NAME, "img").get_attribute("src") 
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
               if correctAnswerTrs[i].find_element(By.TAG_NAME, "td").get_attribute("class") == "icon-ok":
                  correctAnswerIndex = i
                  break
            except:
               pass
               
         question["correctAnswer"]["TR"] = question["answers"]["TR"][correctAnswerIndex]

         self.questions.append(question)

   def writeToFile(self):
      with open("questions.json", "w", encoding="utf-8") as file:
         file.write("[")
         file.write("\n")
      for question in self.questions:
         seriliazedQuestion = json.dumps(question, indent=4, ensure_ascii=False)
         with open("questions.json", "a", encoding="utf-8") as file:
            file.write(seriliazedQuestion + ",\n")
      with open("questions.json", "a", encoding="utf-8") as file:
         file.write("]")
      
exctractor = Exctractor()

# while True:
#    url = input("URL: ")
#    exctractor.extract(url)

urlList = []

total = len(urlList)

for i in range(0, len(urlList)):
   exctractor.extract(urlList[i], i, total)

exctractor.writeToFile()