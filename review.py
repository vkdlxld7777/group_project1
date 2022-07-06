import time
from selenium import webdriver
from bs4 import BeautifulSoup
import re
from db_controll import db_crud as db
from chrome_confirm import chromedriver_update as driver_confirm


def googledriver_start(path):
    driver = webdriver.Chrome(path)
    driver.implicitly_wait(3)
    return driver


cid_list = []
db_cont = db()

path = driver_confirm()

book_extra_data = db_cont.itemlist_extra()
rev_extra_data = db_cont.review_extra()
conv_list = [i[0] for i in rev_extra_data]
conv_set = set(conv_list)
rev_ibsn_list = list(conv_set)

driver = googledriver_start(path)
#로그인
#크롤링이 끝나면 제 아이디와 비번이 있기에.. 삭제됩니다.-------------------------------------------
driver.get('https://www.aladin.co.kr/login/wlogin_popup.aspx?SecureOpener=1')
driver.find_element_by_xpath('//*[@id="Email"]').send_keys('dleodnd7777')
driver.find_element_by_xpath('//*[@id="Password"]').send_keys('studybook12#')
driver.find_element_by_xpath('//*[@id="LoginForm"]/div[2]/a/div').click()
time.sleep(6)
# -------------------------------------------------------------------------------------------------


for itemId,isbn in book_extra_data:
    if isbn in rev_ibsn_list:
        print(itemId,isbn)
        continue
    db_input_data = []
    rev_list = []
    star_cnt_list = []
    user_id_list = []
    driver.get('https://www.aladin.co.kr/shop/wproduct.aspx?ItemId='+itemId)
    
    try:
    #리뷰추출
        for i in range(1,40):
            driver.execute_script("window.scrollTo(0, {0})".format(i*500))
            src = driver.page_source
            soup = BeautifulSoup(src,'html.parser')
            conte_list = soup.findAll('div',attrs={'class':'Ere_prod_blogwrap'})
            sect_list = None
            
            #conte_list의 리스트 갯수가 최소 2개가 나와 하나하나 살펴보기위한 반복문
            for i in conte_list:
                if '100자평' in i.text:
                    sect_list = i
            
            #엘리멘트 안에 100자평 이라는 단어가 존재할 경우
            if sect_list is not None and '100자평' in sect_list.text:
                
                #전체 클릭
                driver.find_element_by_xpath('//*[@id="tabTotal"]').click()
                
                #100자평 리뷰 확인
                rev_cnt = soup.findAll('div',id="CommentReviewList")[0].text
                
                
                #100자 평이 없을 경우 
                if rev_cnt.strip() == '등록된 100자평이 없습니다.':
                    #None 값으로 넣는다.
                    temp = {'isbn':isbn, 'user_id': '', 'score': 0, 'rev_content':''}
                    db_input_data.append(temp)
                
                #100자 평이 있을경우
                else:
                    #우선 100자 평 갯수 파악
                    conte_list = int(re.sub('[^0-9]','',soup.findAll('a',id='tabTotal')[0].text))
                    
                    #5배수 만큼 '더보기' 클릭
                    for i in range((conte_list//5)-1 if (conte_list//5)-1<4 else 3):
                        driver.find_element_by_xpath('//*[@id="divReviewPageMore"]/div[1]/a').click()
                        time.sleep(2)
                        
                    #리뷰 평점 및 리뷰 내역 추출
                    src = driver.page_source
                    soup = BeautifulSoup(src,'html.parser')
                    
                    #리뷰 평점 추출
                    star_list = soup.select('#CommentReviewList > div.review_list_wrap > ul > div.hundred_list > div.HL_star')
                    
                    for i in star_list:
                        count = 0
                        star_cnt = i.select('img')
                        for j in star_cnt:
                            if 'icon_star_on' in star_cnt[0]['src']:
                                count += 1
                        star_cnt_list.append(count*2)
                    
                    #리뷰 내역 및 유저 아이디 추출
                    rev_location = soup.select('#CommentReviewList > div.review_list_wrap > ul > div.hundred_list > div.HL_write')
                    
                    for i in rev_location:
                        rev_text = i.select_one('div > ul > li > div > div > a').text.strip()
                        user_id = i.select_one('div > ul > li:nth-child(2) > div > a').text.strip()
                        
                        rev_list.append(rev_text)
                        user_id_list.append(user_id)
                    
                    #추출한 리스트들 합쳐서 반환
                    for i in zip(star_cnt_list,rev_list,user_id_list):
                        temp = {'isbn':isbn, 'user_id': i[2], 'score': i[0], 'rev_content':i[1]}
                        db_input_data.append(temp)
                break
            time.sleep(0.5)
    except:
        continue
    
    #DB 입력
    for i in db_input_data:
        db_cont.review_insert(i)


db_cont.db_conn_exit()
