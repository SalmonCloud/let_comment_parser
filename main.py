import csv
# import requests
# from urllib.parse import urlparse
from os.path import exists
from random import sample

OUTPUT_FILENAME = "username_comments.csv"


# def clean_up_url(url: str) -> str:
#     """Remove query string, and trailing / and page number in the path."""
#     parse_result = urlparse(url)
#     clean_path: str = parse_result.path
#     if parse_result.path.endswith("/"):
#         clean_path = clean_path[:-1]
#     path_tail = parse_result.path.split("/")[-1]
#     if path_tail.startswith("p"):
#         if path_tail[1:].isdecimal():
#             # The last path section is page number. Remove.
#             clean_path = "".join(clean_path.split("/")[:-1])
#     clean_url = parse_result.scheme + "://" + parse_result.netloc + clean_path
#     return clean_url
#
#
# def download_pages(url: str):
#     # page_exists = True
#     page_num = 1
#
#     # while page_exists:
#     response = requests.get(f"{url}/p{page_num}")
#     with open(f"page{page_num}.html", "wt") as file:
#         file.write(response.text)
#

def extract_info(file):
    line = ""
    while not line.startswith("<a title="):
        line = next(file)
    username = line.split('"', 2)[1]
    # print(username)

    while True:
        line = next(file)
        if line.startswith("<blockquote"):
            while not line.endswith("</blockquote>\n"):
                line = next(file)
        if line.startswith("<p>"):
            comment = ""
            while True:
                comment += line.strip("<p>").strip("</p>\n")
                if line.endswith("</p>\n"):
                    break
                line = next(file)
            # print(comment)
            break
    return username, comment


def write_csv_output(csv_file, *row):
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow([*row])


if __name__ == "__main__":
    # raw_url = input("Please enter the URL to the LET post:\n")
    # download_pages(clean_up_url(raw_url))
    print("Before using this program, please save every page "
          "of the post in the following format:")
    print("page?.html    (? stands for the page number)")
    print('When using Google Chrome, press Ctrl + S '
          'and select "Web Page, Complete."')
    print()

    max_page_num = int(
        input("Please the enter the maximum page number of the LET post: "))
    username_comments = dict()  # {"username": [comment1, comment2]}
    for i in range(1, max_page_num + 1):
        filename = f"page{i}.html"
        if not exists(filename):
            print(f"WARNING: {filename} does not exist. Please make sure "
                  "you have downloaded and named it properly.")
            continue
        with open(filename, "rt") as file:
            while True:
                try:
                    username, comment = extract_info(file)
                except StopIteration:
                    print(f"{filename} has been fully parsed.")
                    break
                else:
                    if username in username_comments:
                        username_comments[username].append(comment)
                    else:
                        username_comments[username] = [comment]

    file = open(OUTPUT_FILENAME, "wt", newline="")
    for line_num, username in enumerate(username_comments, 1):
        write_csv_output(file, line_num, username,
                         *username_comments[username])
    file.close()
    print(f"The results are saved in {OUTPUT_FILENAME}")

    while True:
        choice = input("Do you need a prize draw? [Y/n] : ")
        if choice in ("Y", "y", ""):
            prize_draw_needed = True
            break
        elif choice in ("N", "n"):
            prize_draw_needed = False
            break
        else:
            print("Invalid input. Please try again.")

    if prize_draw_needed:
        winner_num = int(input("Please enter the number of winners: "))
        # sample() does not accept AbstractSet anymore since 3.11.
        print(sample(list(username_comments.keys()), winner_num))
