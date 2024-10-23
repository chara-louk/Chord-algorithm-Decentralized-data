import requests
from bs4 import BeautifulSoup
from chord_alg import Node
import time


my_list = []
award_list = []
education_list = []
name_list = []


def get_soup(url, timeout=100):
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        print(f"Error making request to {url}: {e}")
        return None


url = "https://en.wikipedia.org/wiki/List_of_computer_scientists"
soup = get_soup(url)

# i my_list periexei ola ta links twn scientist
if soup:

    content_div = soup.find('div', {'id': 'mw-content-text'})

    for link in content_div.find_all('li'):
        if link.find_parents('div', class_='div-col'):
            continue
        name = link.find('a')
        my_list.append(name)

    # gia kathe scientist psaxnume mesa sto link tis plirofories awards kai education
    for scientist_name in my_list[:10]:
        name_text = scientist_name.text
        award_counter = 0
        scientist_url = "https://en.wikipedia.org" + scientist_name.get('href')
        soup_scientist = get_soup(scientist_url)
        name_list.append(name_text)

        # gia na brume to education psaxnume sto pinaka infobox.
        # meta psaxnume ton header "institutions" mesa ston pinaka
        if soup_scientist:
            text2 = "Unknown education Info"
            education_info = []
            tb_scientist = soup_scientist.find('table', class_="infobox biography vcard")
            if tb_scientist:

                institution_headers = tb_scientist.find_all('th', class_='infobox-label', scope="row",
                                                            string=["Alma\xa0mater"])
                if institution_headers:
                    for header in institution_headers:
                        # otan brume ton header 'institutions' apo deksia tha exei ta onomata twn panepistimiwn,
                        # opote psaxnume to epomeno (find_next) td (pinakas apo links)
                        td_siblings = header.find_next('td', class_='infobox-data')

                        # mesa sto td pairnume kathe link 'a' to opoio einai kai to onoma tou panepistimiou,
                        # kai to kanume text kai to bazume stin lista education_info[]
                        a_tags = td_siblings.find_all('a')
                        for td_sibling in a_tags:
                            institutions_text = td_sibling.get_text(strip=True)
                            institutions = [inst.strip() for inst in institutions_text.split(',')]
                            for inst in institutions:
                                education_info.append(inst)

                else:
                    education_info.append(text2)
            else:
                education_info.append(text2)

            education_list.append(education_info)

            # twra psaxnume se olo swma tis selidas kai oxi ston pinaka mono.
            # psaxnume lista i opoia na periexei tin leksi award mesa
            content_div_scientist = soup_scientist.find('div', {'id': 'mw-content-text'})
            for li_element in content_div_scientist.find_all('li'):
                text = li_element.get_text(strip=True).lower()
                # ama iparxei i leksi award afksanume ton counter kata 1,
                # alliws menei 0 opws to exume arxikopoihsei pio panw
                if 'award' in text:
                    award_counter += 1
            award_list.append(award_counter)

education_set = []
for edu in education_list:
    for inner_edu in edu:
        if inner_edu not in education_set:
            education_set.append(inner_edu)


class Scientist:
    def __init__(self, name, awards, education):
        self.name = name
        self.awards = awards
        self.education = education

    def __str__(self):
        return f"Scientist Name: {self.name}, Awards: {self.awards}, University: {self.education}"

    def print_scientist(self):
        print("Name:", self.name)
        print("Awards:", self.awards)


def create_scientists_dict(scientist_dict):
    for name, awards, education_info in zip(name_list, award_list, education_list):
        scientist = Scientist(name, awards, education_info)
        for edu in education_info:
            if edu in scientist_dict:
                scientist_dict[edu].append(scientist)
            else:
                scientist_dict[edu] = [scientist]

    return scientist_dict


def print_scientists_dict(scientist_dict):
    for edu_key in scientist_dict:
        print(f"Education: {edu_key}")
        for scientist in scientist_dict[edu_key]:
            scientist.print_scientist()


def print_hashed_nodes(universities, hashed_node_id_mapping):
    print("---Hashed universities---")
    for university in universities:

        hashed_id = Node.hash_function(university)

        print(f"University: {university}")
        print("hashed id is:", hashed_id)
        hashed_node_id_mapping[university] = hashed_id


if __name__ == "__main__":
    node_id_mapping = {}
    hashed_node_id_mapping = {}
    scientist_dict = {}

    # kanume ena antikeimeno tipou Scientist kai hasharoume to university
    scientist_instance = Scientist(name_list, award_list, education_list)
    scientist_dict = create_scientists_dict(scientist_dict)
    print_scientists_dict(scientist_dict)
    print_hashed_nodes(education_set, hashed_node_id_mapping)
    print()

    start_time = time.time()
    # Arxikopoihsh twn nodes!!
    initial_node = Node(hashed_node_id_mapping['University of Malaya'], 'University of Malaya')
    initial_node.join(initial_node)

    for uni, hashed_id in hashed_node_id_mapping.items():
        print()
        print(f"Current University: {uni}, Hashed ID: {hashed_id}")
        if uni != 'University of Malaya':
            print("Joining the node for university:", uni)
            node = Node(hashed_id, uni)
            node.join(initial_node)

    for university, scientists_list in scientist_dict.items():
        for scientist in scientists_list:
            initial_node.add_scientist(scientist)
    end_time = time.time()

    execution_time = end_time - start_time
    print("execution time was:", execution_time, "sec")
    initial_node.print_ring()

    start_time2 = time.time()
    # Kanoume search gia ta panepistimia Harvard kai Cambridge ya minimum awards = 5
    hashed_uni1 = Node.hash_function("Harvard University")
    hashed_uni2 = Node.hash_function("MIT")
    min_awards = 5
    responsible_node_1 = initial_node.find_successor(hashed_uni1)
    responsible_node_2 = initial_node.find_successor(hashed_uni2)

    search_scientists = responsible_node_1.scientists.get("Harvard University", [])
    scientists_with_awards = [scientist for scientist in search_scientists if scientist.awards >= min_awards]
    end_time2 = time.time()

    execution_time2 = end_time2 - start_time2
    print("Search time was:", execution_time2, "sec")

    printed_scientists = set()

    print("Scientists from Harvard with at least 5 awards:")
    for scientist in scientists_with_awards:
        identifier = scientist.name
        if identifier not in printed_scientists:
            print(scientist)
            printed_scientists.add(identifier)
    if scientist not in scientists_with_awards:
        print("There was no such scientist!")

    print()
    print("The node responsible for this scientist is:", responsible_node_1.node_id)

    start_time3 = time.time()

    responsible_node_1.leave()
    end_time3 = time.time()

    leave_time = end_time3 - start_time3
    print("Leave time is:",leave_time,"sec")
    printed_scientists = set()
    new_responsible_node = initial_node.find_successor(hashed_uni1)

    print()
    print("Responsible node left, now new responsible node is:", new_responsible_node.node_id)

    for scientist in scientists_with_awards:
        identifier = scientist.name
        if identifier not in printed_scientists:
            print(scientist)
            printed_scientists.add(identifier)
        if scientist not in scientists_with_awards:
            print("There was no such scientist!")

    initial_node.print_ring()
