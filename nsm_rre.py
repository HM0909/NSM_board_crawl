from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup as bs
import time
from db_manager import DatabaseManager

DATABASE_ID = "local"   

# 국립중앙과학관(NSM)

base_url = "https://www.science.go.kr/mps"
login_url = "https://rsvn.science.go.kr/nsm/member/login?returnURL= + ?? " 
board_url = "https://www.science.go.kr/board?menuId=MENU00401&siteId=" 

options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def login(): 
    # 메인에서 로그인 버튼 클릭
    driver.get(base_url)
    element = driver.find_element_by_xpath('//*[@id="header"]/div/div/nav/ul/li[2]/a')  
    driver.execute_script("arguments[0].click();", element)
    # 새탭으로 열린 로그인 페이지 이동
    driver.switch_to.window(driver.window_handles[-1])
    
    # 로그인
    id = ""
    password = ""

    driver.find_element_by_id('id').send_keys(id) 
    time.sleep(5) 
    driver.find_element_by_id('password').send_keys(password) 
    time.sleep(5) 
    driver.find_element_by_xpath('//*[@id="loginForm"]/div/ul[2]/li/a').click() 
    time.sleep(5)


def crawling(): 
    driver.get(board_url)

    html = driver.page_source
    soup = bs(html, 'html.parser')
        
    board_main = soup.find("table",  {"class" : "tstyle-list"}) 
    board_body = board_main.find("tbody")
    board_list = board_body.find_all("tr")
    
    datas = []

    
    for item in board_list:
        board = item.find_all("td") 
        board_number = board[0].text.strip()               # 글번호
    
        data = board[1]
        link = data.find("a")
        url = link.get("href")
        link_url = "https://www.science.go.kr" + url       # 상세 URL
        
        detail(board_number, link_url)
        
        datas.append(detail(board_number, link_url)) 
    

    if len(datas) > 0:  
                    db = DatabaseManager(DATABASE_ID)  
                    db.connection()  
                    query = '''  
                            INSERT INTO board_nsm (BD_NUMBER, LINK_URL, TITLE, REG_DATE, READ_COUNT, CONTENT, ATTACH_URL)   
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
         
 
         
def detail(board_number, link_url): 
    driver.get(link_url)

    detail_html = driver.page_source
    detail_soup = bs(detail_html, 'html.parser')  
    
    detail_main = detail_soup.find("article",  {"class" : "board-view"}) 
    
    title = detail_main.find("h1",  {"class" : "view-title"}).text                     # 제목

    main = detail_main.find("ul",  {"class" : "info"})
    boby = main.find_all("li")

    reg_date_all = boby[0].text  
    reg_date = reg_date_all.replace("작성일", "").strip()                               # 작성일
                   
    read_count_all  = boby[1].text 
    read_count = read_count_all.replace("조회수", "").strip()                           # 조회수
        
    if read_count != "":
        read_count = read_count.replace(",", "") 
    else: 
        read_count = 0
    
    content = detail_main.find("div",  {"class" : "view-content"}).text.strip()         # 내용
   
    attach_url = ""
    
    if detail_main.find("ul",  {"class" : "down_file"}) != None: 
        detail_item = detail_main.find("ul",  {"class" : "down_file"})
        detail_data = detail_item.find_all("li")
        
        for data in detail_data:
            link = data.find("a")
            attach_url = link.get("href")                                               # 파일 URL      

            
    return [board_number, link_url, title, reg_date, read_count, content, attach_url]
        
         
def main(): 
    
    login()
    
    crawling()
    
    
if __name__ == '__main__':
    main()