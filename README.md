# Book Store Application

## Project Overview

This repository contains a Django-based web application designed as a project for Lancaster University.

## Project Participants
* Daniil Karbukov
* Ruochen Liao
* Jalal Mammadov

## Project Scope

**Initial Idea and Objectives**

- Develop an API-driven web application to manage a library of books and authors.  
- Support CRUD operations on authors and books, filtering, sorting, and reporting.  
- Implement bulk import of books from the Google Books API.  

**Anticipated Challenges**

- Handling asynchronous vs. synchronous bulk import reliably.  
- Ensuring data consistency when updating multiple related records (e.g., changing price or authors).  
- Designing API parameters for flexible filtering, sorting, and bulk operations.  

## Functional Requirements

_All endpoints accept HTTP GET and return JSON unless noted otherwise._

1. **Add Author**  
   `GET /addauthor?name=<author_name>`  
   - Creates a new author if `<author_name>` is valid and unique.

2. **Edit Author**  
   `GET /edit_author?current_name=<old>&new_name=<new>`  
   - Renames an existing author.

3. **Delete Author**  
   `GET /delete_author?id=<author_id>`  
   - Deletes the author with the specified ID.

4. **Add Book**  
   `GET /addbook?name=<title>&author=<comma_separated_names>&price=<float>&edition=<edition>&description=<text>`  
   - Creates a new book, associates authors, validates price, and prevents duplicates.

5. **Edit Book**  
   `GET /edit_book?book_id=<id>&[name=&price=&edition=&description=&author=]`  
   - Updates any provided fields; if `author` is given, clears existing links and reassigns.

6. **Delete Book(s)**  
   `GET /delete_book?id=<id1,id2,...>`  
   - Deletes one or more books by comma-separated IDs.

7. **Search Book**  
   `GET /search_book?name=<keywords>`  
   - Performs a case-insensitive, partial match on book titles.

8. **Search Author**  
   `GET /search_author?name=<keywords>`  
   - Finds authors by name and returns each author’s list of books.

9. **Sort Books**  
   - `GET /sort_alph?order=[asc|desc]` — Sort by title alphabetically.  
   - `GET /sort_price?order=[asc|desc]` — Sort by price numerically.

10. **Bulk Import Books**  
    `GET /add_books?query=<term>&total_books=<N>&api_key=<key>`  
    - Fetches up to `N` volumes from the Google Books API and adds unique entries based on volume ID.

11. **Generate Report**  
    `GET /generate_report`  
    - Returns a CSV containing:  
      - Total books  
      - Average book price  
      - Total authors  
      - Average books per author  
      - Detailed lists of all books and authors  

12. **Change Price**  
    `GET /change_price?[current_price=<float>]|[lower_than=<float>]|[higher_than=<float>]&new_price=<float>`  
    - Updates the price of all books matching the specified filter.

---

## System Architecture and Constraints

- Operating System: Windows, macOS, or Linux
- Python 3.X
- Django version 5.1.2
- **Database:** SQLite 
- **Design Constraints:**  
  - All API endpoints use HTTP GET and return `JsonResponse` or CSV.  
  - Parameter validation occurs in view functions.  
  - External HTTP calls via the `requests` library synchronously.

---

## Repository Structure

mysite/
├── mysite/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── bookstore/
│   ├── migrations/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── templates/
│   │   └── library/
│   └── tests.py
├── UMLs/
│   ├── Use Case Diagram.png
│   ├── Class Diagram.png
│   └── Sequence Diagram.png
├── manage.py
├── requirements.txt
└── README.md

## Installation Guide 
1. Install Django and dependencies:

- pip install django
   
2. database migration:

- python manage.py makemigrations
- python manage.py migrate

3. Run the server:

- python manage.py runserver

4. Access the application at `http://127.0.0.1:8000/`















