library = {}

def add_book():
    isbn = input("Enter ISBN: ")
    title = input("Enter book title: ")
    author = input("Enter author name: ")

    library[isbn] = {"title": title, "author": author}

    print("Book added!\n")

def search_book():
    isbn = input("Enter ISBN to search: ")

    if isbn in library:
        print("Book found!")
        print("Title:", library[isbn]["title"])
        print("Author:", library[isbn]["author"])
    else:
        print("Book not found.")
    print()

def delete_book():
    isbn = input("Enter ISBN to delete: ")

    if isbn in library:
        del library[isbn]
        print("Book deleted.")
    else:
        print("Book not found.")
    print()

def show_books():
    if len(library) == 0:
        print("Library is empty.\n")
    else:
        print("All books in library:")
        for isbn in library:
            print(isbn, "->", library[isbn])
    print()

while True:
    print("1. Add Book")
    print("2. Search Book")
    print("3. Delete Book")
    print("4. Show Books")
    print("5. Exit")

    choice = input("Enter choice: ")

    if choice == '1':
        add_book()
    elif choice == '2':
        search_book()
    elif choice == '3':
        delete_book()
    elif choice == '4':
        show_books()
    elif choice == '5':
        break
    else:
        print("Wrong choice, try again.\n")