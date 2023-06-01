import requests
from bs4 import BeautifulSoup

# WHY
# The SearchRequest module contains all the internal logic for the library.
#
# This encapsulates the logic,
# ensuring users can work at a higher level of abstraction.

# USAGE
# req = search_request.SearchRequest("[QUERY]", search_type="[title]")


class SearchRequest:

    col_names = [
        "ID",
        "Author",
        "Title",
        "Publisher",
        "Year",
        "Pages",
        "Language",
        "Size",
        "Extension",
        "Mirror_1",
        "Mirror_2",
        "Mirror_3",
        "Mirror_4",
        "Mirror_5",
        "Edit",
    ]

    def __init__(self, query, search_type="title"):
        self.query = query
        self.search_type = search_type

        if len(self.query) < 3:
            raise Exception("Query is too short")

    def strip_i_tag_from_soup(self, soup):
        subheadings = soup.find_all("i")
        for subheading in subheadings:
            subheading.decompose()
        return soup

    def get_search_page(self):
        query_parsed = "%20".join(self.query.split(" "))
        if self.search_type.lower() == "title":
            search_url = (
                f"http://gen.lib.rus.ec/search.php?req={query_parsed}&column=title"
            )
        elif self.search_type.lower() == "author":
            search_url = (
                f"http://gen.lib.rus.ec/search.php?req={query_parsed}&column=author"
            )
        search_page = requests.get(search_url)
        return search_page

    def aggregate_request_data(self):
        search_page = self.get_search_page()
        soup = BeautifulSoup(search_page.text, "lxml")
        # self.strip_i_tag_from_soup(soup)

        # Libgen results contain 3 tables
        # Table2: Table of data to scrape.
        information_table = soup.find_all("table")[2]

        # Determines whether the link url (for the mirror)
        # or link text (for the title) should be preserved.
        # Both the book title and mirror links have a "title" attribute,
        # but only the mirror links have it filled.(title vs title="libgen.io")
        output_data = []
        for row in information_table.find_all("tr")[1:]:
            row_data = dict()
            for col_name, row_col in zip(self.col_names, row.find_all("td")):
                a = row_col.find("a")
                #mirrors
                if row_col.find("a") and row_col.find("a").has_attr("title") and row_col.find("a")["title"] != "":
                    row_data[col_name] = row_col.a.get("href")
                    continue
                
                if col_name == "Title":
                    ISBNs = []
                    for a in row_col.find_all("a"):
                        if a.has_attr("title"):
                            print(a)
                            i = a.find("i")
                            if i:
                                isbn_string = next(i.stripped_strings)
                                
                                ISBNs += isbn_string.split(", ")
                            self.strip_i_tag_from_soup(a)
                            title_field = "".join(a.stripped_strings)
                            
                            
                    row_data["Title"] = title_field
                    row_data["ISBNs"] = ISBNs

                    
                else:
                    self.strip_i_tag_from_soup(row_col)
                    val = "".join(row_col.stripped_strings)
                    row_data[col_name] = val

            output_data.append(row_data)
                    
        return output_data
