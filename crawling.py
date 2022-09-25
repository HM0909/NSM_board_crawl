from unicodedata import category
import re
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import urllib.request as ur
import time
from webdriver_manager.chrome import ChromeDriverManager    # Mac
from db_manager import DatabaseManager

HEADER = ['제목', '조회수', 'URL', '첨부파일URL', '작성자', '내용', '등록일']
ARGV_COUNT = 2
DATABASE_ID = "local"

# 국립중앙과학관(NSM)

base_url = "https://www.science.go.kr/mps"
board_url = "https://www.science.go.kr/board?menuId=MENU00401&siteId=" 
login_url = "https://rsvn.science.go.kr/nsm/member/login?returnURL= + ?? " 

driver = webdriver.Chrome(executable_path='C:\hm_py\chromedriver')    # Windows


def login():
    driver.get(base_url)

    # 로그인 페이지 이동
    element = driver.find_element_by_xpath('//*[@id="header"]/div/div/nav/ul/li[2]/a')  
    driver.execute_script("arguments[0].click();", element)
    time.sleep(1)
    driver.switch_to.window(driver.window_handles[-1])  #새로 연 탭으로 이동
                  
    # 로그인
    user_id = ""
    password = ""

    driver.find_element_by_id('id').send_keys(user_id)
    time.sleep(5)
    driver.find_element_by_id('password').send_keys(password)
    time.sleep(5)
    element = driver.find_element_by_xpath('//*[@id="loginForm"]/div/ul[2]/li/a') 
    driver.execute_script("arguments[0].click();", element)                      

    time.sleep(5)
 

def crawling():
    driver.get(board_url)
    html = driver.page_source
    soup = bs(html, 'html.parser')

    board_main = soup.find("table",  {"class" : "tstyle-list"}) 
    board_body = board_main.find("tbody")
    board_list = board_body.find_all("tr")
    
    datas =[]

    for item in board_list:    
        board_number = item.select_one("td")                              # 자료 번호
        board_number = re.sub('<.+?>', '', str(board_number)).strip()            
                
        print(board_number)
        
        data = item.find("td", {"class":"subject"})                                         
        link = data.find("a")                                                    
        link_url = link.get("href")                                        # 상세 URL
        
        print("https://www.science.go.kr"+ link_url)   
        # detail("https://www.science.go.kr"+link_url)
        datas.append(detail(link_url, board_number))


    if len(datas) > 0:
        db = DatabaseManager(DATABASE_ID)
        db.connection()
        print(datas)
        query = '''
                INSERT INTO board_nsm (TITLE, WRITER, CONTENT, LINK_URL, READ_COUNT, REG_DATE, ATTACH_URL)
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
            '''        

        db.execute_query_bulk(query, datas)        
            
#상세 크롤링
def detail(detail_url, board_number):
    driver.get("https://www.science.go.kr" + detail_url)
    
    detail_html = driver.page_source 
    detail_soup = bs(detail_html, 'html.parser')

    view_header = detail_soup.find("div", {"id" : "detail-contents"})
    title = view_header.find("h1", {"class" : "view-title"}).text            # 제목
    header_all = detail_soup.find("ul", {"class" : "info"})
    reg_date = header_all.select('span')[0].text                             # 등록일
    read_count = header_all.select('span')[1].text                           # 조회수 
    content = view_header.find("div", {"class" : "view-content"}).text       # 내용
    
    writer = ""
    attach_url= ""                                                           # 첨부파일 URL
    
    print(title, reg_date, read_count, content)
     
    return [title, writer, content, detail_url , read_count, reg_date, attach_url]

def main():
    
    login()
         
    crawling()
            
    driver.quit()
         
if __name__ == '__main__':
    main()