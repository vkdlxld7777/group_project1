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

driver = googledriver_start(path)

#로그인
#크롤링이 끝나면 제 아이디와 비번이 있기에.. 삭제됩니다.-------------------------------------------
driver.get('https://www.aladin.co.kr/login/wlogin_popup.aspx?SecureOpener=1')
driver.find_element_by_xpath('//*[@id="Email"]').send_keys('dleodnd7777')
driver.find_element_by_xpath('//*[@id="Password"]').send_keys('studybook12#')
driver.find_element_by_xpath('//*[@id="LoginForm"]/div[2]/a/div').click()
time.sleep(6)
#-------------------------------------------------------------------------------------------------

driver.get('https://www.aladin.co.kr/')

#국내도서 클릭
driver.find_element_by_xpath('//*[@id="#head_book_layer"]/a/img').click()
#웹소스 가져오기
src = driver.page_source
soup = BeautifulSoup(src,'html.parser')

#목록추출
div_list = soup.findAll('ul',id='browse')
find_category = div_list[0].find_all(id=re.compile("browse"))
for i in find_category:
    data = re.sub('[0-9]','',i.attrs["id"])
    if len(data)==6:
        cid = i.next_element.attrs["href"].split('=')[1]
        category = i.text.strip()
        cid_list.append({'cid':cid,'category':category})

# 장르소설만 특별취급합니다....
for i,item in enumerate(cid_list):
    if item['cid'] == '50927':
        print(i)
        print(data[i])
        del data[i]
        break
plus_data = [{'cid':'50926','category':'추리/미스터리소설'},{'cid':'50927','category':'라이트 노벨'},
             {'cid':'50928','category':'판타지/환상문학'},{'cid':'50930','category':'과학소설(SF)'},
             {'cid':'50931','category':'호러.공포소설'},{'cid':'50932','category':'무협소설'},
             {'cid':'50933','category':'액션/스릴러소설'},{'cid':'50935','category':'로맨스소설'}]
cid_list = cid_list+plus_data

#직접 들어가기
#테마기준 각 책당 화면에 보이면 content 뽑기
def book_content(category,div_list):
    result = []
    for data in div_list:
        book_content = {}
        book_content["itemId"] = data.find('a').attrs["href"].split('=')[1].strip()
        book_content["category"] = category
        book_content["title"] = data.find('a').text
        publ_auth = data.find('span',attrs={'class':'gw'}).text.split('/')
        book_content["author"] = publ_auth[0].strip()
        book_content["publisher"] = publ_auth[1].strip()
        book_content["price"] = re.sub("[^0-9]","",data.find('span',attrs={'class':'p1'}).text)
        result.append(book_content)
    return result
all_list = []
#테마별
for i in cid_list:
    driver.get('https://www.aladin.co.kr/shop/wbrowse.aspx?CID='+i['cid']+'&BrowseTarget=BestSeller')
    src = driver.page_source
    soup = BeautifulSoup(src,'html.parser')
    div_list = soup.findAll('td',attrs={'class':'tc'})
    #book_content 추출
    all_list += book_content(i['category'],div_list)
    time.sleep(5)
    
    
    
    
    
#itemID 검색 테스트데이터
# all_list = [{'itemId':'295216320'},{'itemId':'296479776'},{'itemId':'296104295'},{'itemId':'288756034'},{'itemId':'296919926'},{'itemId':'294426044'},{'itemId':'295838672'}]


#itemID로 진행
for num,book in enumerate(all_list):
    #db에 저장되어 있는 데이터는 건너뛰기 위해 불러오기-----------------------------------------------
    extra = db_cont.itemlist_extra()
    save_itemId = [i[0] for i in extra]
    save_isbn = [i[1] for i in extra]
    #------------------------------------------------------------------------------------------------
    try:
        if book['itemId'] in save_itemId:
            continue
        result = {}
        driver.get('https://www.aladin.co.kr/shop/wproduct.aspx?ItemId='+book["itemId"])
        time.sleep(1)
        
        #스크롤 내리기 스크롤을 내려야 페이지가 동기화 됩니다...
        # 개요 가져오기----------------------------------------------------------------------------------------------
        for i in range(1,40):
            driver.execute_script("window.scrollTo(0, {0})".format(i*500))
            time.sleep(0.3)
            src = driver.page_source
            soup = BeautifulSoup(src,'html.parser')
            conte_list = soup.findAll('div',attrs={'class':'Ere_prod_middlewrap'})
            
            #//*[@id="Ere_prod_allwrap"]/div[9]/div[10]
            if '책소개' in conte_list[0].text:
                description_list = soup.findAll('div',attrs={'class':'Ere_prod_mconts_box'})
                break
        
        for i in description_list:
            book['description'] = ''
            if '책소개' in i.text:
                book['description'] = i.text.replace('책소개','').strip()
                break
        #------------------------------------------------------------------------------------------------------------
        
        
        #평점 가져오기------------------------------------------------------------------------------------------------
        for i in range(1,40):
            driver.execute_script("window.scrollTo(0, {0})".format(i*500))
            time.sleep(0.3)
            src = driver.page_source
            soup = BeautifulSoup(src,'html.parser')
            conte_list = soup.findAll('div',attrs={'class':'Ere_prod_graphwrap_a'})
            try:
                if conte_list[0].text is not None and ('평점 분포' in conte_list[0].text):
                    description_list = soup.findAll('div',attrs={'class':'star_area_a'})
                    break
            except:
                continue
        try:
            book['avg_score'] = soup.select_one('#Ere_prod_allwrap > div.Ere_prod_graphwrap_a > div.graph_box > div.star_area_a > div > div.anay_conts > div > div > div:nth-child(1) > div > div.num').text
        except:
            book['avg_score'] = '0'
        #------------------------------------------------------------------------------------------------------------
        
        
        
        #출판일 가져오기---------------------------------------------------------------------------------------------
        book['p_date'] = re.search('\d{4}-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])',soup.findAll('li',attrs={'class':'Ere_sub2_title'})[0].text).group()
        #------------------------------------------------------------------------------------------------------------
        
        
        
        #페이지,ISBN 가져오기----------------------------------------------------------------------------------------
        book_data = soup.findAll('div',attrs={'class':'conts_info_list1'})[0].find_all('li')
        for i in book_data:
            text = i.text
            if '쪽' in text:
                book['page'] = re.sub("[^0-9]",'',text.replace('쪽','').strip())
                if book['page'] == '':
                    book['page'] = 200
            elif 'ISBN' in text:
                book['isbn'] = text.split(':')[1].strip()
        #------------------------------------------------------------------------------------------------------------
        
        
        
        #리뷰 부분 ---------------------------------------------------------------------------------------
        # 들어갈때 isbn 번호만 가져오고 평점 갯수만큼 db에 넣어야함 따라서
        # 초기화되는 리스트 안 객체를 생성해서 이따 db넣을때 반복해야함
        #-----------------------------------------------------------------------------------------------------------
    except:
        continue
    
    #있는데 통과됬음... 확인해봐야함
    
    if book['isbn'] not in save_isbn:
        db_cont.bookdata_insert(book)
    


#DB커넥트 종료
db_cont.db_conn_exit()

# #임시적 저장
# result = {i : data for i,data in enumerate(all_list)}
# with open("C:/Users/vkdlx/Desktop/coding/group_project1/myDictionary.pkl","wb") as tf:
#     pickle.dump(result,tf)
    
# with open("C:/Users/vkdlx/Desktop/coding/group_project1/myDictionary.pkl","wb") as tf:
#     new_dict = pickle.load(tf)
    
# print(new_dict.item())

while True:
    pass


