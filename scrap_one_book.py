""" This script allows us to scrap a book's detail using it's URL.

"""

import csv
import os
import urllib.request

import requests
from bs4 import BeautifulSoup

from links_and_titles_scrapper import remove_suffix


def cleaning_titles(book):
    """ Removes the characters forbidden by the NTFS from the string.
    """

    if not book.startswith(' '):
        book_csv_file_name = book.replace(' ', '_') + ".csv"
    book_csv_file_name = book_csv_file_name.replace(':', '_')
    book_csv_file_name = book_csv_file_name.replace('/', '-')
    book_csv_file_name = book_csv_file_name.replace('?', '-')
    book_csv_file_name = book_csv_file_name.replace("<", '_')
    book_csv_file_name = book_csv_file_name.replace('"', '_')
    book_csv_file_name = book_csv_file_name.replace('>', '_')
    book_csv_file_name = book_csv_file_name.replace('|', '-')
    book_csv_file_name = book_csv_file_name.replace("*", '_')
    return book_csv_file_name


def writing_header(ten_information, book_csv_file_name):
    """ Designed to be used writing_book_information(). It writes a file containing the 10 required information.

    Args:
        ten_information: the dictionary that will be written in the file.
        book_csv_file_name: the name of the file we will write.
    """

    with open(book_csv_file_name, 'w', encoding="windows-1252") as f:
        header = ["product_page_url",
                  "universal_product_code",
                  "title",
                  "price_including_tax",
                  "price_excluding_tax",
                  "number_available",
                  "category",
                  "review_rating",
                  "product_description",
                  "image_url"]
        writer = csv.DictWriter(f, delimiter='\n', fieldnames=header)
        writer.writeheader()
        writer.writerow(ten_information)


def writing_book_information(csv_file_name, URL):
    """
    First, we get each of the 10 required information as a key-value pair. Then, we write
    them as a dictionary.

    Args:
        csv_file_name: the name of the csv file we will create.
        URL: the link to the book we want to scrap

    Returns: The csv file containing the 10 required information.

    """

    # cleaning the title that will be used as filename.
    book_csv_file_name = cleaning_titles(csv_file_name)

    # requesting the HTML source code we will scrap.
    product_page_url = requests.get(URL).text
    book_page = BeautifulSoup(product_page_url, 'lxml')

    # Here we get the product page URL (1).
    book_dict = {"product_page_url": URL}

    # Here we get the universal product code of the book (2).
    try:
        upc = book_page.find('tr').text.rstrip().lstrip()
        book_dict["universal_product_code"] = upc
    except AttributeError:
        if AttributeError:
            book_dict["universal_product_code"] = "Unable to scrap this information"

    # Here we get the title (3).
    title = csv_file_name
    book_dict["title"] = title

    # I create a list with the table from which I'll take four useful information.
    # The catch-exception block is long because four information depend on the existence of the "class" tag.
    try:
        product_table = book_page.find('table', class_="table table-striped")
        product_table = list(product_table)

        # Useful info one : the price including tax (4).
        price_including_tax = product_table[7].text.rstrip().lstrip()
        price_including_tax = price_including_tax[-5:]
        book_dict["price_including_tax"] = price_including_tax

        # Useful info two : the price excluding tax (5).
        price_excluding_tax = product_table[5].text.rstrip().lstrip()
        price_excluding_tax = price_excluding_tax[-5:]
        book_dict["price_excluding_tax"] = price_excluding_tax

        # Useful info three : the number of books available (6).
        number_available_text = product_table[11].text.split()
        number_available_ugly_text = number_available_text[-2]
        number_available = "".join([i for i in number_available_ugly_text if i != "("])
        book_dict["number_available"] = number_available

        # Useful info four : the ratings (9).
        review_rating_tag = product_table[-2].text.rstrip().lstrip()
        book_dict['review_rating'] = review_rating_tag

    except TypeError:
        if TypeError:
            book_dict["price_including_tax"] = "Unable to scrap this information"
            book_dict["price_excluding_tax"] = "Unable to scrap this information"
            book_dict["number_available"] = "Unable to scrap this information"
            book_dict['review_rating'] = "Unable to scrap this information"

    # Here we get the product description (7).
    errors = (IndexError, AttributeError)
    try:
        product_description = book_page.find_all('p')
        book_dict["product_description"] = product_description[3].encode("windows-1252")
    except errors:
        if errors:
            book_dict["product_description"] = "Unable to scrap this information"

    # Here we get the category (8).
    try:
        category_parent = book_page.find('ul')
        categories = category_parent.find_all('li')
        category_parent_list = list(categories)
        category = category_parent_list[2].text.rstrip().lstrip()
        book_dict["category"] = category
    except errors:
        if errors:
            book_dict["category"] = "Unable to scrap this information"

    # Here we get the image URL (10).
    try:
        image_url_parent = book_page.find(class_='item active')
        image_url_list = list(image_url_parent)
    except TypeError:
        print("The HTML source code of this book doesn't seem to cointain the expected 'item active' class")
    image_url_text = image_url_list[1]
    image_url_text = str(image_url_text)
    # The first [].notation refers to the list item to extract while the second is splitting the string.
    image_url = image_url_text.rsplit('src="')[1][:-3]
    # We need to add an suffix in order to get the good webpage.
    s = "http://books.toscrape.com/"
    image_url = image_url.replace('../../', s)
    book_dict["image_url"] = image_url

    writing_header(book_dict, book_csv_file_name)


def down_image(image_filename, folder):
    """

    Args: the book's csv filename and the folder where to store the downloaded image.

    Returns: downloads the jpg image in the designated folder.

    """
    # saving the folder where we started the process
    current_folder = os.getcwd()

    # Taking the image URL from the book's csv file.
    with open(image_filename, 'r') as f:
        lines = f.readlines()

        image_url = lines[-2]

        # Creating the folder where we'll store all the images then moving to it.
        if not os.path.isdir(folder):
            os.mkdir(os.path.join(os.getcwd(), folder))
        os.chdir(os.path.join(os.getcwd(), folder))

        # requesting the data in bytes and creating the image.
        image_name = remove_suffix(image_filename, '.csv') + '.jpg'
        urllib.request.urlretrieve(image_url, image_name)

    # returning to the folder we were in when starting the process
    os.chdir(current_folder)
