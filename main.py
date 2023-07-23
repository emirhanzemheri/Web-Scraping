from selenium import webdriver
from pymongo import MongoClient
import threading


Last_Page               = 1373 #Range of kitap yurdus for all books page
TypeOfBook              = {"edebiyat": 526,"cocuk-kitaplari":519,"tarih-kitaplari":339,"saglik":63,"yemek-kitaplari":8} # All sections in kitap sepeti for iterate all kind of books with range.
kitapyurdu_datas        = [] #initially empty list for collecting datas and load database for kitapyurdu          
kitapsepeti_datas       = [] #initially empty list for collecting datas and load database for kitapsepeti


def crop_string(text): #for crop unexpected space character
    text         = text.strip()
    words        = text.split()
    cropped_text = " ".join(words)
    return cropped_text

def scraping_kitap_yurdu():
    # Start explorer with web-driver
    try:
        driver_kitapyurdu = webdriver.Chrome() #If the selenium version you are using is v4.6.0 or above then you don't really have to set the driver.exe path.
        for page_number in range(1,Last_Page+1): #iterate in all books pages (1-1373) with many 100 books per page.
            #go to all books pages with url
            driver_kitapyurdu.get('https://www.kitapyurdu.com/index.php?route=product/category&page='+str(page_number)+'&filter_category_all=true&path=1&filter_in_stock=1&sort=purchased_365&order=DESC&limit=100')
            books = driver_kitapyurdu.find_elements("xpath",'//div[@class="product-cr"]') # find all books component
            
            for book in books:#iterate books in all books and get datas from html tags with xpath method
                book_title = book.find_element("xpath",'.//div[@class="image"]/div[@class="cover"]/a[@class="pr-img-link"]/img').get_attribute("alt")
                publisher  = book.find_element("xpath",'.//div[@class="publisher"]/span/a/span').get_attribute("innerHTML")
                author     = book.find_element("xpath",'.//div[@class="author compact ellipsis"]').text
                price      = crop_string(book.find_element("xpath",'.//div[@class="price"]').text)+" TL"
                data_book       = {'title':book_title,'author':author,'publisher':publisher,'price':price}
                kitapyurdu_datas.append(data_book)
                
        
        collection = db['kitapyurdu'] # When finished collect data create collection with name 'kitapyurdu'
        collection.insert_many(kitapyurdu_datas) #insert datas to collection

    except:
        print("Error occured in kitap sepeti sayfa:"+page_number+"Infos:"+data_book)    

    driver_kitapyurdu.quit() # Quit chorme driver when finished kitapyurdu scraping
    
def scraping_kitapsepeti():
    try:
        driver_2 = webdriver.Chrome() #open chrome driver for scraping kitapsepeti
        
        for key in TypeOfBook.keys(): #iterate in kitapsepeti type of books
            driver_2.get("https://www.kitapsepeti.com/"+key) #go to type of book page
            for page_num in range(1,TypeOfBook[key]+1):
                driver_2.get("https://www.kitapsepeti.com/"+key+"?pg="+str(page_num))
                Books = driver_2.find_elements("xpath",'//div[@class="col col-3 col-md-4 col-sm-6 col-xs-6 p-right mb productItem zoom ease"]')# Find all book elements then collect data
                for book in Books:
                    book_infos = book.find_element("xpath",'.//div[@class="col col-12 drop-down hover lightBg"]').text.split('\n')
                    if len(book_infos) == 4:
                        book_title     = book_infos[0]  # Some books don't have a author name in www.kitapsepeti.com so adjust with publisher name
                        book_publisher = book_infos[1]
                        book_author    = book_infos[2]
                        book_price     = book_infos[3]
                    else:
                        book_title     = book_infos[0]
                        book_publisher = book_infos[1]
                        book_author    = book_infos[1] # Some books don't have a author name in www.kitapsepeti.com so adjust with publisher name
                        book_price     = book_infos[2]

                    data_book = {'title':book_title,'author':book_author,'publisher':book_publisher,'price':book_price}
                    kitapsepeti_datas.append(data_book)
                    
            collection = db['kitapsepeti'] # When finished collect data create collection with name 'kitapsepeti'
            collection.insert_many(kitapsepeti_datas) 
    except:
        print("Error occured in kitap sepeti sayfa:"+page_num+"Infos:"+book_infos)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
        collection = db['kitapsepeti']   # Record datas before error occured. 
        collection.insert_many(kitapsepeti_datas) #insert datas to collection
    
    driver_2.quit() # Quit chorme driver when finished kitapsepeti scraping
    




if __name__=="__main__":
    mongo_client = MongoClient('localhost', 27017) # connect local host MongoDB
    db = mongo_client['smartmaple']   # create data base 'smartmaple'




    thread1 = threading.Thread(target=scraping_kitap_yurdu)#Create two thread for asynchrons web scraping same time for www.kitapsepeti.com and www.kitapyurdu.com
    thread2 = threading.Thread(target=scraping_kitapsepeti)
    
    
    thread1.start()# Start threads same time and waits until finish
    thread2.start()


    thread1.join()
    thread2.join()
    mongo_client.close() #Close the client

