# OCR_project2
scraps a book's website with beautiful soup 
# scrappingproject
Project 2 of my Python's OCR path 

**VERSION 1.0.0**

The following code is designed to scrap the https://books.toscrape.com/ website. For each of the books on the website, the code will give me the following information : 
        1. the product page URL 
        2. the universal product code (upc)
        3. the title
        4. the price including tax
        5. the price excluding tax
        6. the number of books available
        7. the product description
        8. the category
        9. the review rating
        10. the book's image URL
        
**VIRTUAL ENVIRONMENT** 

The only modules you will need to install are requests and BeautifulSoup. The other ones are built-in modules.

        
**DEMO CODE** 

The project contains two modules. 

The links_and_titles_scrapper module defines three important functions. 
The first one is writing_csv_file(url). The input is the URL of one of the book categories from the website. The output is a CSV file containing the title and the link to each book's page in the category.
The second one is all_categories_links(url). You can use it if you want to scrap all the categories from the website. As input you need to give it the URL to the last category ('https://books.toscrape.com/catalogue/category/books/crime_51/index.html'). It will return a list containing the link to all the categories from the website except the last one. You can then loop through that list with writing_csv_file function. 
In order to be exhaustive, you will have to call writing_csv_file with the crime's category URL. 
The third one is all_categories_titles(url). Althought it is defined in the links_and_titles_scrapper module, it is used in the second module. 

The second module, book_scrapper, defines one important function. 
It's name is create_csv_file. The function takes one string : the name of one of the csv files previously created with the first module. It will return for each of the books in the csv file a dictionnary containing the 10 information listed below. 
Those 10 information will be saved in a new csv file. If you want to create a csv file for each book of the website, no matter the category, you need to use the all_categories_titles(url) function (which is imported). 
The most useful argument it takes is the name of csv file created for the last category of the website("Crime_.csv"). With that argument, the function will create a csv file for each of the books in the website except the ones in the Crime category. Here again, you will have to recall the function afterwards with "Crime_.csv". 


Ex: let's say you want to take the 10 information for each book in the category Christian. In the links_and_title_scrapper module you call the writing_csv_file function with the "https://books.toscrape.com/catalogue/category/books/christian_43/index.html" argument. 
A file named 'Christian_.csv' will be created. You then switch to the book_scrapper module. There, you call the create_csv_file function with the 'Christian_.csv' argument. This call will return you three files (there are three books in the category) with the needed information on each book.


**CONTRIBUTORS** 

Gide Rutazihana, student, giderutazihana81@gmail.com 
Ashutosh Purushottam, mentor  


**LICENCE** 

There's no Licence 
