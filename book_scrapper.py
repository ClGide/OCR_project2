""" This script extracts links and titles for each books in the category from a given csv file.

"""

import csv
import os
import urllib.request

import requests
from bs4 import BeautifulSoup

from links_and_titles_scrapper import remove_suffix, all_categories_titles


def get_lists_from_csv(csv_file_name):
    """ Creates two lists from the given csv file.

    Args:
        csv_file_name: the name of one of the csv files created with the book_scrapper.py module.

    Returns: two lists. One containing the links to all the books in the category. The other containing the titles
            of all the books in the category.

    """
    # saving the folder where we started the process
    current_folder = os.getcwd()

    # going to the folder containing the file we need
    folder_name = remove_suffix(csv_file_name, '_.csv')
    if os.path.isdir(folder_name):
        os.chdir(folder_name)

    f = open(csv_file_name, 'r', encoding="windows-1252")
    reader = csv.DictReader(f)
    x = []
    for key in reader:
        x.append(key)
    csv_dict = x[0]
    links = list(csv_dict.values())
    books = list(csv_dict.keys())
    f.close()

    # returning to the folder we were in when starting the process
    os.chdir(current_folder)

    return links, books


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
    """ Designed to be used inside create_csv_file(). It writes a file containing the 10 required informations.

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


def writing_book_information(csv_file_name):
    """
    First, we get each of the 10 required information as a key-value pair. Then, we write
    them as a dictionary.

    Args: the name of one of the csv files created with the links_and_titles_scrapper.py module.

    Returns: The csv file containing the 10 required information.

    """
    # saving the folder where we started the process
    current_folder = os.getcwd()

    # specifying the folder where to write the files
    folder_name = remove_suffix(csv_file_name, '_.csv')
    if not os.path.isdir(folder_name):
        os.mkdir(os.path.join(os.getcwd(), folder_name))
    os.chdir(os.path.join(os.getcwd(), folder_name))

    links = list(get_lists_from_csv(csv_file_name))[0]
    books = list(get_lists_from_csv(csv_file_name))[1]

    if len(links) == len(books):
        n = len(links)
    else:
        print("one list is bigger than the other")

    for i in range(n):
        # cleaning all the titles that will be used as filenames.
        book_csv_file_name = cleaning_titles(books[i])

        # requesting the HTML source code we will scrap
        product_page_url = requests.get(links[i]).text
        book_page = BeautifulSoup(product_page_url, 'lxml')

        # Here we get the product page URL (1)
        book_dict = {"product_page_url": links[i]}

        # Here we get the universal product code of the book (2)
        try:
            upc = book_page.find('tr').text.rstrip().lstrip()
            book_dict["universal_product_code"] = upc
        except AttributeError:
            if AttributeError:
                book_dict["universal_product_code"] = "Unable to scrap this information"

        # Here we get the title (3)
        title = books[i]
        book_dict["title"] = title

        # I create a list with the table from which I'll take four useful information.
        # The catch-exception block is long because four information depend on the existence of the "class" tag
        try:
            product_table = book_page.find('table', class_="table table-striped")
            product_table = list(product_table)

            # Useful info one : the price including tax (4)
            price_including_tax = product_table[7].text.rstrip().lstrip()
            price_including_tax = price_including_tax[-5:]
            book_dict["price_including_tax"] = price_including_tax

            # Useful info two : the price excluding tax (5)
            price_excluding_tax = product_table[5].text.rstrip().lstrip()
            price_excluding_tax = price_excluding_tax[-5:]
            book_dict["price_excluding_tax"] = price_excluding_tax

            # Useful info three : the number of books available (6)
            number_available_text = product_table[11].text.split()
            number_available_ugly_text = number_available_text[-2]
            number_available = "".join([i for i in number_available_ugly_text if i != "("])
            book_dict["number_available"] = number_available

            # Useful info four : the ratings (9)
            review_rating_tag = product_table[-2].text.rstrip().lstrip()
            book_dict['review_rating'] = review_rating_tag

        except TypeError:
            if TypeError:
                book_dict["price_including_tax"] = "Unable to scrap this information"
                book_dict["price_excluding_tax"] = "Unable to scrap this information"
                book_dict["number_available"] = "Unable to scrap this information"
                book_dict['review_rating'] = "Unable to scrap this information"

        # Here we get the product description (7)
        errors = (IndexError, AttributeError)
        try:
            product_description = book_page.find_all('p')
            book_dict["product_description"] = product_description[3].encode("windows-1252")
        except errors:
            if errors:
                book_dict["product_description"] = "Unable to scrap this information"

        # Here we get the category (8)
        try:
            category_parent = book_page.find('ul')
            categories = category_parent.find_all('li')
            category_parent_list = list(categories)
            category = category_parent_list[2].text.rstrip().lstrip()
            book_dict["category"] = category
        except errors:
            if errors:
                book_dict["category"] = "Unable to scrap this information"

        # Here we get the image URL (10)
        try:
            image_url_parent = book_page.find(class_='item active')
            image_url_list = list(image_url_parent)
        except TypeError:
            print("The HTML source code of this book doesn't seem to cointain the expected 'item active' class")
        image_url_text = image_url_list[1]
        image_url_text = str(image_url_text)
        # The first [].notation refers to the list item to extract while the second is splitting the string
        image_url = image_url_text.rsplit('src="')[1][:-3]
        # We need to add an suffix in order to get the good webpage
        s = "http://books.toscrape.com/"
        image_url = image_url.replace('../../', s)
        book_dict["image_url"] = image_url

        writing_header(book_dict, book_csv_file_name)

    # returning to the folder we were in when starting the process
    os.chdir(current_folder)


def all_books_filename(csv_file_name):
    """

    Args:
        csv_file_name: a category's csv filename

    Returns: a list storing the csv filename of all the books in the category

    """

    # Getting the list of books from the first function defined in the script
    books = list(get_lists_from_csv(csv_file_name))[1]
    n = len(books)

    # We are creating a list of all the book csv filenames
    # We will use the list to save the images of all the books
    books_csv_name_list = []
    for i in range(n):
        book_csv_file_name = cleaning_titles(books[i])
        books_csv_name_list.append(book_csv_file_name)

    return books_csv_name_list


def down_image(folder_to_read_from, image_filename, folder_to_write_to):
    """
    First, we get to the directory where the book file we are searching is saved. From that file we extract the
    image url's needed for the download. Second, we specify the folder where we will save the image and we
    download it.

    Args:
        folder_to_read_from: the folder where we will find the book csv file's.
        image_filename: the book's csv filename
        folder_to_write_to: the folder where to store the downloaded image.

    Returns: downloads the jpg image and stores it in the designated folder.

    """
    # saving the folder where we started the process
    current_folder = os.getcwd()

    # specifying the folder where to search the image url's
    if os.path.isdir(folder_to_read_from):
        os.chdir(os.path.join(os.getcwd(), folder_to_read_from))

    # Taking the image URL from the book's csv file
    with open(image_filename, 'r') as f:
        lines = f.readlines()

        image_url = lines[-2]

        # Creating the folder where we'll store all the images then moving to it
        if not os.path.isdir(folder_to_write_to):
            os.mkdir(os.path.join(os.getcwd(), folder_to_write_to))
        os.chdir(os.path.join(os.getcwd(), folder_to_write_to))

        # requesting the data in bytes and creating the image
        image_name = remove_suffix(image_filename, '.csv') + '.jpg'
        urllib.request.urlretrieve(image_url, image_name)

    # returning to the folder we were in when starting the process
    os.chdir(current_folder)


if __name__ == "__main__":
    # The all_categories_title function is imported from the links_and_titles_scrapper module
    all_csv_category_titles = all_categories_titles(
        "http://books.toscrape.com/catalogue/category/books/crime_51/index.html")
    all_csv_category_titles.append("Crime_.csv")
    for csv_file in all_csv_category_titles:
        writing_book_information(csv_file)


    # Downloading the books' image from the website.
    # If your computer and/or connection aren't fast enough you might need to rerun the script multiple times
    # Each time you need to rerun it, check the number of downloaded images and use the number as an index
    for book_category in all_csv_category_titles:
        books_file_name = list(get_lists_from_csv(book_category))[1]
        for book in books_file_name:
            book = cleaning_titles(book)
            category_folder_name = remove_suffix(book_category, '_.csv')
            image_category = category_folder_name + "_images"
            down_image(category_folder_name, book, image_category)
