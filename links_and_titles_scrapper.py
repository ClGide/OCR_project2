""" This script creates a CSV file with the titles and links of all the books in a category.

Whether or not the book category contains multiple webpages, the script writes all the titles and links in a single
CSV file.

"""

import csv
import os

import requests
from bs4 import BeautifulSoup


def remove_suffix(input_string, suffix):
    """ Equivalent of the 3.9 Python removesuffix string method (this script is written in the 3.8 version).
    """
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string


def requesting_page(url):
    """

    Args: URL to the page.

    Returns: the HTML source code. 'page' is an instance of bs4.BeautifulSoup class.

    """
    response = requests.get(url)
    page = BeautifulSoup(response.content, features='lxml')
    return page


def get_titles(url):
    """

    Args: The URL to a book category's webpage.

    Returns: The titles of all the books in the category.

    """

    page = requesting_page(url)

    # to get all the book titles in the first page, we search for the title attributes.
    content = page.find_all('a')
    all_titles_in_first_page = []
    for link in content:
        all_titles_in_first_page.append(link.get('title', 'No title attribute'))

    # the previous list contains a tags w/o title attributes, we need to remove them.
    all_titles_in_first_page = [i for i in all_titles_in_first_page if i != 'No title attribute']

    return all_titles_in_first_page


def get_links(url):
    """

    Args: The URL to a book category's webpage

    Returns: The links to all the books from the webpage as they're referenced in the source code

    """
    page = requesting_page(url)
    content = page.find_all('a')  # we get all the a tags, the ones that define links
    all_links_raw_format = []
    for link in content:
        all_links_raw_format.append(link.get('href'))
    return all_links_raw_format


def cleaning_links(url):
    """Takes abbreviated links as they're referenced in the HTML source code and returns their explicit version.

    Args: The URL to a book category's webpage.

    Returns: The links to all the books from the webpage ready to use.

    """
    all_links_raw_format = get_links(url)

    # The first 54 links refer to the homepage or the book categories.
    books_in_first_page_raw_format = all_links_raw_format[54:]

    # In the HTML source code the links are abbreviated, that's why we use the replace method to get the full links.
    prefix_to_url = 'http://books.toscrape.com/catalogue/'
    books_in_first_page_good_format = [i.replace('../../../', prefix_to_url) for i in books_in_first_page_raw_format]

    # There's two links per book in the HTML source code. We therefore need to remove the doubles.
    almost_clean_list = books_in_first_page_good_format[:-1]
    links_in_first_page_clean_list = []
    [links_in_first_page_clean_list.append(i) for i in almost_clean_list if i not in links_in_first_page_clean_list]

    return links_in_first_page_clean_list


def getting_next_page_link(prefix, page):
    """Some book categories contains multiple webpages. This function helps us navigate through the whole category.

    Args:
        prefix: In the HTML source code, links are abbreviated. The prefix is used to complete them.
        page: The HTML source code.

    Returns: Useful link to the next page in the category.

    """
    a_tag = page.find(class_="next").findChild()
    next_page = a_tag.get('href')
    link_to_next_page = prefix + "/" + next_page

    return link_to_next_page


def completing_list_w_links(prefix, list_w_links, content):
    """Gets the links to the books contained in the other webpages contained in the category.

    This function need to be nested in the right function. It appends to an already existing list of links. It also
    presuppose that the page've been already scrapped in order to have all the a tags from the HTML source code.

    Args:
        prefix: to complete the abbreviated links scrapped from the HTML source code.
        list_w_links: The links in the first webpage of the book category.
        content: instance of the class bs4.BeautifulSoup. An iterable containing all the a tags.

    Returns: The useful links to the books contained in the webpage.

    """
    next_page_links_raw_format = [link.get('href').replace('../../../', prefix) for link in content][54:-2]
    [list_w_links.append(link) for link in next_page_links_raw_format if link not in list_w_links]


def completing_list_w_titles(list_w_titles, content):
    """Similarly to completing_list_w_links, this function needs to be nested in the right function.

    Args:
        list_w_titles: The links from which to extract the titles.
        content: instance of the class bs4.BeautifulSoup. An iterable containing all the a tags.

    Returns: The titles to the books contained in the webpage.

    """
    for link in content:
        list_w_titles.append(link.get('title', 'No title attribute'))
    list_w_titles = [i for i in list_w_titles if i != 'No title attribute']
    return list_w_titles


def next_pages_links_and_titles(url):
    """

    Args: the URL of the page to scrap.

    Returns: four lists. They contain the titles and links with all the books in the category. EXCEPT
            the first twenty books scrapped above. If there are less than 40 books in the category, the last two
            lists will be empty.

    """
    page = requesting_page(url)
    # WARNING: there are two url links for the first page of each multi-page category.
    # One ending w/'page-1' and the other w/'index'. The below code works only for the url ending w/'index'.
    prefix_for_next_pages_links = remove_suffix(url, "/index.html")

    # I'm initializing those lists outside the while loop. Otherwise, the statements will clean the lists
    # at each iteration.
    second_page_links = []
    all_titles_in_second_page = []

    next_page_links = []
    all_titles_in_next_pages = []

    books = "just to get this variable assigned before the while loop. I use it to end the loop when needed"
    while books is not None:
        if page.find(class_="next") is not None:
            # What follows is getting me the page number two (or other even number) HTML source code.
            link_to_second_page = getting_next_page_link(prefix_for_next_pages_links, page)
            response = requests.get(link_to_second_page)
            second_page = BeautifulSoup(response.content, features='lxml')
            content = second_page.find_all('a')

            # The following gets me the the page number two (or other even number) links and titles.
            completing_list_w_links(prefix_for_next_pages_links, second_page_links, content)
            all_titles_in_second_page = completing_list_w_titles(all_titles_in_second_page, content)

            # What's above solves the problem for even nr pages i.e. 2, 4, 6...
            # What's below ensures I get the titles and links for odd nr pages i.e. 3, 5, 7...

            if second_page.find(class_='next') is not None:
                # I split the linkToNextPage string into a 3-item list then reconstruct the right link.
                link_to_next_page = getting_next_page_link(prefix_for_next_pages_links, second_page)
                # getting the HTML source codes.
                response = requests.get(link_to_next_page)
                next_page = BeautifulSoup(response.content, features='lxml')
                content = next_page.find_all('a')
                # getting the links.
                completing_list_w_links(prefix_for_next_pages_links, next_page_links, content)
                # getting the titles
                all_titles_in_next_pages = completing_list_w_titles(all_titles_in_next_pages, content)
                # Vital lines for the while loop:
                page = next_page
            # The two else statements are necessary :
            # the first will stop the while loop when there is an odd number of webpages in the category
            # the other one will stop the while loop when there is one or an even number of webpages
            else:
                books = None
        else:
            books = None
    return second_page_links, all_titles_in_second_page, next_page_links, all_titles_in_next_pages


def put_together_the_dict(url):
    """

    Args: the URL of the page to scrap.

    Returns: the header and the dictionnary we will write to the csv file. The dictionnary contains the
            links and titles of all the books in the category.

    """
    # collecting all the relevant data.
    first_page_links = cleaning_links(url)
    first_page_titles = get_titles(url)
    even_nr_pages_links = next_pages_links_and_titles(url)[0]
    even_nr_pages_titles = next_pages_links_and_titles(url)[1]
    odd_nr_pages_links = next_pages_links_and_titles(url)[2]
    odd_nr_pages_titles = next_pages_links_and_titles(url)[3]

    # getting the header of the csv file together. The csv file will be written in the next function.
    first_page_titles.extend(even_nr_pages_titles)
    first_page_titles.extend(odd_nr_pages_titles)
    header = first_page_titles

    # getting together the dict that will be written in the csv file.
    # Each key-value pair is a title-link pair.
    first_page_dict = dict(zip(first_page_titles, first_page_links))
    even_pages_dict = dict(zip(even_nr_pages_titles, even_nr_pages_links))
    odd_pages_dict = dict(zip(odd_nr_pages_titles, odd_nr_pages_links))
    first_page_dict.update(even_pages_dict)
    first_page_dict.update(odd_pages_dict)
    all_books_dict = first_page_dict

    return header, all_books_dict


def writing_titles_and_links_to_file(url):
    """

    Args: The URL of the page to scrap.

    Returns: The csv file where the titles and links of all the books in the category will be stored.

    """
    # saving the folder where we started the process
    current_folder = os.getcwd()

    # create the csv file title
    csv_file_name = url.split('/')[-2].title()
    suffix = ".csv"
    csv_file_name = ''.join([i for i in csv_file_name if not i.isdigit()]) + suffix

    # getting the header and the dict from the previous function
    header = put_together_the_dict(url)[0]
    all_books_dict = put_together_the_dict(url)[1]

    # making the category folder where we will store the books csv file'
    folder_name = remove_suffix(csv_file_name, '_.csv')
    if not os.path.isdir(folder_name):
        os.mkdir(os.path.join(os.getcwd(), folder_name))
    os.chdir(os.path.join(os.getcwd(), folder_name))

    # writing the csv file
    with open(csv_file_name, 'w', encoding="windows-1252") as f:
        writer = csv.DictWriter(f, delimiter=',', fieldnames=header)
        writer.writeheader()
        writer.writerow(all_books_dict)

    # returning to the folder we were in when starting the process
    os.chdir(current_folder)

# The following is used for test purposes.


def all_categories_links(url):
    """ Gets all the categories' link from the website.
    Use the crime category (the last one) URL's as input. The source code of a category doesn't have the auto-ref.
    Therefore, a loop using the below function will stop at the category which URL was used.

    Args: The URL from which to scrap the links.
        (ideally : https://books.toscrape.com/catalogue/category/books/crime_51/index.html)

    Returns: list with the link to all the categories of the site (except the crime category).

    """
    all_links = get_links(url)
    all_categories_raw_format = all_links[4:54]
    prefix = "http://books.toscrape.com/catalogue/category/books/"
    all_categories = [i.replace("../", prefix) for i in all_categories_raw_format]
    all_categories.remove("index.html")
    return all_categories


def all_categories_titles(url):
    """
    WARNING : To avoid a bug I removed the last item (the inexistent auto-ref to the URL's in the HTML code)
    Consequently, in order to obtain the full list :
    1-use the last category's URL. 2-manually add the last category's csv file name

    Args: The URL from which to scrap the links.
        (ideally : https://books.toscrape.com/catalogue/category/books/crime_51/index.html)

    Returns: All the csv file names (except 'Crime_.csv')

    """
    list_all_categories_links = all_categories_links(url)
    all_categories_csv_file_name = []
    for link in list_all_categories_links[:-1]:
        all_categories_csv_file_name.append(
            "".join([i for i in link.split('/')[-2] if not i.isdigit()]).title() + ".csv")
    return all_categories_csv_file_name


if __name__ == '__main__':
    all_categories_links = all_categories_links("https://books.toscrape.com/catalogue/category/books/crime_51/index.html")
    all_categories_links.append("https://books.toscrape.com/catalogue/category/books/crime_51/index.html")
    for category_link in all_categories_links:
        writing_titles_and_links_to_file(category_link)
