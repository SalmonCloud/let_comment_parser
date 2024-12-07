import csv
from typing import TextIO, Union
from os.path import exists
from random import sample

HtmlTagList = list[Union[str, tuple[str]]]

OUTPUT_FILENAME = "username_comments.csv"


def descend_into_html_tags(html_tag_list: HtmlTagList, file: TextIO):
    line = next(file)
    for tag in html_tag_list:
        if type(tag) is str:
            while tag not in line:
                line = next(file)
        elif type(tag) is tuple:
            no_tag_option_found = True
            while no_tag_option_found:
                for tag_option in tag:
                    if tag_option in line:
                        no_tag_option_found = False
                        break
                else:
                    line = next(file)


def extract_username(file: TextIO) -> str:
    line = next(file)
    title_atrribute = line.strip().split(' ')[1]
    username = title_atrribute.split("=")[1].strip('"')
    return username


def extract_comment(file: TextIO) -> str:
    comment = ""
    line = next(file)
    while "</div>" not in line:
        # Skip user's quote.
        if '<blockquote class="UserQuote">' in line:
            while "</blockquote>" not in line:
                line = next(file)
        else:
            comment += line.strip().strip("<p>").strip("</p>")
        line = next(file)
    return comment


def write_csv_output(csv_file: TextIO, *row):
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow([*row])


if __name__ == "__main__":
    print("Before using this program, please save every page "
          "of the post in the following format:")
    print("page?.html    (? stands for the page number)")
    print('When using Google Chrome, press Ctrl + S '
          'and select "Web Page, Complete."')
    print()

    max_page_num = int(
        input("Please the enter the maximum page number of the LET post: "))
    username_comments = dict()  # {"username": [comment1, comment2]}
    html_tag_list_username: HtmlTagList = [
        ('<li class="Item ItemComment', '<li class="Item Alt ItemComment'),
        '<div class="Comment">',
        '<div class="Item-Header CommentHeader">',
        '<div class="AuthorWrap">',
        '<span class="Author">'
    ]
    html_tag_list_comment: HtmlTagList = [
        '<div class="Item-BodyWrap">',
        '<div class="Item-Body">',
        '<div class="Message userContent">',
    ]

    for i in range(1, max_page_num + 1):
        filename = f"page{i}.html"
        if not exists(filename):
            print(f"WARNING: {filename} does not exist. Please make sure "
                  "you have downloaded and named it properly.")
            continue

        with open(filename, "rt") as file:
            # Find the start of comment section.
            descend_into_html_tags(list('<div class="CommentsWrap">'), file)

            while True:
                try:
                    # Find the line before the one
                    # where username can be extracted.
                    descend_into_html_tags(html_tag_list_username, file)
                except StopIteration:
                    print(f"{filename} has been fully parsed.")
                    break
                else:
                    username = extract_username(file)

                    # Find the line before the one
                    # where user's quote or comment can be found.
                    descend_into_html_tags(html_tag_list_comment, file)
                    comment = extract_comment(file)

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
