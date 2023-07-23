from selenium import webdriver
from pymongo import MongoClient
from selenium.webdriver.support import expected_conditions as EC
import threading

First_Page              = 1
Last_Page               = 1#1373




TypeOfBook              ={"edebiyat": 526,"cocuk-kitaplari":519,"tarih-kitaplari":339,"saglik":63,"yemek-kitaplari":8}
         

def crop_string(text): #for crop unexpected space character

    text = text.strip()
    words = text.split()
    cropped_text = " ".join(words)

    return cropped_text

def scrapting_kitap_yurdu(db):
     # Start explorer with web-driver
    try:
        kitapyurdu =[]
        driver = webdriver.Chrome() #If the selenium version you are using is v4.6.0 or above then you don't really have to set the driver.exe path.
        for page_number in range(1,Last_Page+1): #iterate in all books pages (1-1373) with many 100 books per page.
            # go to all books pages with url
            driver.get('https://www.kitapyurdu.com/index.php?route=product/category&page='+str(page_number)+'&filter_category_all=true&path=1&filter_in_stock=1&sort=purchased_365&order=DESC&limit=100')
            books = driver.find_elements("xpath",'//div[@class="product-cr"]') # find all books component
            
            for book in books:#iterate books in all books and get datas
                book_title = book.find_element("xpath",'.//div[@class="image"]/div[@class="cover"]/a[@class="pr-img-link"]/img').get_attribute("alt")
                publisher = book.find_element("xpath",'.//div[@class="publisher"]/span/a/span').get_attribute("innerHTML")
                author = book.find_element("xpath",'.//div[@class="author compact ellipsis"]').text
                price = crop_string(book.find_element("xpath",'.//div[@class="price"]').text)+" TL"
                print("Book Title:", book_title)
                print("Publisher:", publisher)
                print("Author",author)
                print("Price",price)
                data ={'title':book_title,'author':author,'publisher':publisher,'price':price}
                kitapyurdu.append(data)
        
        
        
        collection = db['kitapyurdu']
        collection.insert_many(kitapyurdu)

# Bağlantıyı kapatın
        

    except:
        print(page_number)    

    driver.quit()

def scrapting_kitapsepeti(db):
    driver_2 = webdriver.Chrome() 
    kitapsepeti = []
    for key in TypeOfBook.keys():
        driver_2.get("https://www.kitapsepeti.com/"+key)
        for page_num in range(1,2):#TypeOfBook[key]+1
            driver_2.get("https://www.kitapsepeti.com/"+key+"?pg="+str(page_num))
            Books = driver_2.find_elements("xpath",'//div[@class="col col-3 col-md-4 col-sm-6 col-xs-6 p-right mb productItem zoom ease"]')# Find all book elements then collect data
            for book in Books:
                book_infos = book.find_element("xpath",'.//div[@class="col col-12 drop-down hover lightBg"]').text.split('\n')
                book_title = book_infos[0]
                book_publisher = book_infos[1]
                book_author   = book_infos[2]
                book_price  = book_infos[3]
                print("Kitap:",book_title)
                print("Yayin:",book_publisher)
                print("Yazar:",book_author)
                print("Ücreti:",book_price)
                data ={'title':book_title,'author':book_author,'publisher':book_publisher,'price':book_price}
                kitapsepeti.append(data)
        collection = db['kitapsepeti']
        collection.insert_many(kitapsepeti)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
    
    driver_2.quit()




if __name__=="__main__":
    mongo_client = MongoClient('localhost', 27017)
    db = mongo_client['smartmaple']
    thread1 = threading.Thread(target=scrapting_kitap_yurdu(db))
    thread2 = threading.Thread(target=scrapting_kitapsepeti(db))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()
    mongo_client.close()

