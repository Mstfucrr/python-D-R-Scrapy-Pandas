import scrapy
import pandas as pd

class DrSpider(scrapy.Spider):
    name = "dr_spider"

    start_urls = [
        "https://www.dr.com.tr/kategori/Kitap/Ders-Sinav-Kitaplari/Universite-Ders-Kitaplari/Tip/grupno=10000070/?Page=1&Manufacturer[0]=Güneş%20Tıp%20Kitabevleri",
    ]


    myBookList = []
    def parse(self, response):
        book_list = response.css("div.prd")
        for book_list_item in book_list:
            book = Book(
                kitap_num= len(self.myBookList),
                kitap_adi=book_list_item.css(".prd-name::text").extract_first(),
                yazar = book_list_item.css(".pName a.who::text").extract_first(),
                yayinevi = book_list_item.css("a.prd-publisher::text").extract_first(),
                fiyat = book_list_item.css("div.prd-price::text").extract_first(),
            )
            self.myBookList.append(book)
        next_btn = response.css("li.pagination-next")
        if len(next_btn) > 0:
            print(next_btn)
            print("*****************************************************************")
            next_url = next_btn.css("a::attr(href)").extract_first()
            next_url = "https://www.dr.com.tr" + next_url
            yield scrapy.Request(url=next_url, callback=self.parse)
        else:
            book.save_to_csv(self.myBookList)
class Book():
    def __init__(self,kitap_num, kitap_adi, yazar, yayinevi, fiyat):
        self.kitap_num = kitap_num
        self.kitap_adi = kitap_adi
        self.yazar = yazar
        self.yayinevi = yayinevi
        self.fiyat = fiyat

    def save_to_csv(self,myBookList):

        kitap_num_list = [book.kitap_num+1 for book in myBookList]
        kitap_adi_list = [book.kitap_adi.strip() for book in myBookList]
        yazar_list = [book.yazar.strip() for book in myBookList]
        yayinevi_list = [book.yayinevi.strip() for book in myBookList]
        fiyat_list = [book.fiyat.strip() for book in myBookList]
        
        df = pd.DataFrame({
            "Kitap Adı": kitap_adi_list,
            "Yazar":  yazar_list,
            "Yayinevi": yayinevi_list,
            "Fiyat": fiyat_list,
        }, columns=["Kitap Adı","Yazar","Yayinevi","Fiyat"]) # dataframe oluşturuldu.

        hierarchy = list(zip(df["Yayinevi"],df["Yazar"],df["Fiyat"])) 
        hierarchy = pd.MultiIndex.from_tuples(hierarchy) 
        
        df.set_index(hierarchy, inplace=True) 
        df.index.names = ["Yayinevleri","Yazarlar","Fiyatlar"]    
        df.drop(["Yayinevi","Yazar","Fiyat"], axis=1, inplace=True)
        df = df.sort_index()  


        df.to_excel("Dr.xlsx", index=True, encoding="utf-8-sig")


