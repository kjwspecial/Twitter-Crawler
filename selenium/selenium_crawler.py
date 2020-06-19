import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import time
from bs4 import BeautifulSoup as bs
import json
import codecs


def init_driver(chromedriver_path):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('window-size=1920x1080')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(chromedriver_path ,options = chrome_options)
    driver.wait = WebDriverWait(driver,5)
    return driver

def close_driver(driver):
    driver.close()
    return

class wait_for_more_than_n_elements_to_be_present(object):
    def __init__(self, locator, count):
        self.locator = locator
        self.count = count
 
    def __call__(self, driver):
        try:
            elements = EC._find_elements(driver, self.locator)
            return len(elements) > self.count
        except StaleElementReferenceException:
            return False

def login_twitter(driver, username, password):
 
    driver.get("https://twitter.com/login")

    username_field = driver.find_element_by_name("session[username_or_email]")
    password_field = driver.find_element_by_name("session[password]")

    username_field.send_keys(username)
    driver.implicitly_wait(1)
 
    password_field.send_keys(password)
    driver.implicitly_wait(1)
 
    #login in 버튼 클릭
    #driver.find_element_by_class_name("EdgeButtom--medium").click()
    driver.find_element_by_xpath('//*[@id="react-root"]/div/div/div[2]/main/div/div/form/div/div[3]/div/div/span/span').click()
    return

def login_twitter(driver, username, password):
 
    # 트위터 web page:
    driver.get("https://twitter.com/login")

    # find the boxes for username and password
    username_field = driver.find_element_by_name("session[username_or_email]")
    password_field = driver.find_element_by_name("session[password]")
    # enter your username:
    username_field.send_keys(username)
    driver.implicitly_wait(1)
 
    # enter your password:a
    password_field.send_keys(password)
    driver.implicitly_wait(1)
 
    # click the "Log In" button:
    #driver.find_element_by_class_name("EdgeButtom--medium").click()
    driver.find_element_by_xpath('//*[@id="react-root"]/div/div/div[2]/main/div/div/form/div/div[3]/div/div/span/span').click()
    return

def search_twitter(driver, query):
    driver.get('http://twitter.com/search')
    
    
# old_Version
#     # search box 로딩.
#     box = driver.wait.until(EC.presence_of_element_located((By.NAME, "q"))) 
#     # find search box
#     driver.find_element_by_name("q").clear()
#     # 쿼리입력
#     box.send_keys(query)
#     box.submit()

    #search box
    element = driver.find_element_by_xpath('//input[@placeholder]')
    #쿼리 입력
    element.send_keys(query)
    element.submit()

    wait = WebDriverWait(driver, 5)
    
    
    try:
        # html list items, class = 'data-item-id'
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "li[data-item-id]")))
 
        while True:
            #너무 빨리찾으면, IP 벤당하는듯
            time.sleep(5)
            # 트윗 추출
            tweets = driver.find_elements_by_css_selector("li[data-item-id]")
            number_of_tweets = len(tweets)
            # 스크롤링
            driver.execute_script("arguments[0].scrollIntoView();", tweets[-1])
            try:
                wait.until(wait_for_more_than_n_elements_to_be_present(
                    (By.CSS_SELECTOR, "li[data-item-id]"), number_of_tweets))
            except TimeoutException:
                # 더이상없을때, exit while loop
                break
        page_source = driver.page_source
        
    except TimeoutException:
        page_source=None


    return page_source

def extract_tweets(page_source):
    soup = bs(page_source,'lxml')
    tweets = []
    for li in soup.find_all("li", class_='js-stream-item'):
        if 'data-item-id' not in li.attrs:
            continue
        else:
            tweet = {
                'tweet_id': li['data-item-id'],
                'text': None,
                'user_id': None,
                'user_screen_name': None,
                'user_name': None,
                'created_at': None,
                'retweets': 0,
                'likes': 0,
                'replies': 0
            }
 
            text_p = li.find("p", class_="tweet-text")
            if text_p is not None:
                tweet['text'] = text_p.get_text()
                
            # id, screen_name, user_name
            user_details_div = li.find("div", class_="tweet")
            if user_details_div is not None:
                tweet['user_id'] = user_details_div['data-user-id']
                tweet['user_screen_name'] = user_details_div['data-screen-name']
                tweet['user_name'] = user_details_div['data-name']
 
            # time
            date_span = li.find("span", class_="_timestamp")
            if date_span is not None:
                tweet['created_at'] = float(date_span['data-time-ms'])
 
            # Retweets
            retweet_span = li.select("span.ProfileTweet-action--retweet > span.ProfileTweet-actionCount")
            if retweet_span is not None and len(retweet_span) > 0:
                tweet['retweets'] = int(retweet_span[0]['data-tweet-stat-count'])
 
            # Likes
            like_span = li.select("span.ProfileTweet-action--favorite > span.ProfileTweet-actionCount")
            if like_span is not None and len(like_span) > 0:
                tweet['likes'] = int(like_span[0]['data-tweet-stat-count'])
 
            # Replies
            reply_span = li.select("span.ProfileTweet-action--reply > span.ProfileTweet-actionCount")
            if reply_span is not None and len(reply_span) > 0:
                tweet['replies'] = int(reply_span[0]['data-tweet-stat-count'])
 
            tweets.append(tweet)
 
    return tweets

if __name__ =="__main__":
    statr_time= time.time()
    keyword = ['$MSFT']
    for key in keyword:
        chromedriver_path = os.getcwd()+'/chromedriver'
        driver =init_driver(chromedriver_path)
        username = ""
        password = ""
        login_twitter(driver, username, password)
        
        page_source = search_twitter(driver,"$"+key)
        tweets = extract_tweets(page_source)
        
        with open(key + '.json', 'w') as file:
            file.write(json.dumps(tweets)) 
        print(key+" is done!"+"\t --- %s seconds --- " %(time.time()-statr_time))
        driver.quit()

