from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
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
    driver.get(base_url)
    element = driver.find_element(By.XPATH, '//*[@id="header"]/div/div/nav/ul/li[2]/a')
    driver.execute_script("arguments[0].click();", element) 
    driver.switch_to.window(driver.window_handles[-1])  # 새탭으로 열림
    time.sleep(5)

    user_id ="haemin9299"
    password= "@lhmlove9209"
     
    driver.find_element(By.ID, 'id').send_keys(user_id) 
    time.sleep(5) 
    driver.find_element(By.ID, 'password').send_keys(password) 
    time.sleep(5) 
    driver.find_element(By.XPATH, '//*[@id="loginForm"]/div/ul[2]/li/a').click()
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
        
    for list in board_list:
        board_number = list.find_all("td")
        list_number = board_number[0].text  # 번호
    
        link_list = list.find("td",  {"class" : "subject"}) 
        link = link_list.find("a")
        list_url = link.get("href")
        link_url= "https://www.science.go.kr/board/view?" + list_url     # 상세 URL

        detail(link_url)
        
        datas.append(detail(link_url))

        
    if len(datas) > 0: 
                db = DatabaseManager(DATABASE_ID) 
                db.connection() 
                query = ''' 
                        INSERT INTO board_nsm (TITLE, REG_DATE, LINK_URL, READ_COUNT, CONTENT, ATTACH_URL)  
                        VALUES ( 
                            %s, 
                            %s, 
                            %s, 
                            %s, 
                            %s,
                            %s 
                        ) 
                    '''         
                db.execute_query_bulk(query, datas)
            
                

def detail(link_url):
    driver.get(link_url)

    detail_html = driver.page_source
    detail_soup = bs(detail_html, 'html.parser')
    
    main_header = detail_soup.find("article",  {"class" : "board-view"}) 
    
    title = main_header.find("h1",  {"class" : "view-title"}).text               # 제목

    header_body = main_header.find("ul",  {"class" : "info"})                
    header_main = header_body.find("li")

    reg_date = header_body.select('span')[0].text                             # 등록일
    read_count = header_body.select('span')[1].text                           # 조회수
            
    # header_all = header_main.find_all("span")
        
    # reg_date = ""
    # read_count = ""   
                
    content = main_header.find("div", {"class" : "view-content"}).text 
    
    attach_header = main_header.find("div",  {"class" : "board_list"})
    
    if main_header.find("div",  {"class" : "board_list"}) != None:
        attach_list = attach_header.find("ul",  {"class" : "down_file"})
        attach = attach_list.find("a")
        attach_url= attach.get("href") 
            
   
        return [title, reg_date, link_url, read_count, content , attach_url]


def main(): 
    
    # login()
    
    crawling()
    
    
if __name__ == '__main__':
    main()
