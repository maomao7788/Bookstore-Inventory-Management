from .models import Book, Author
from django.http import JsonResponse
from django.db.models import Q,Prefetch
import requests
import threading
from queue import Queue

def edit_author(request):
    current_name = request.GET.get('current_name')
    new_name = request.GET.get('new_name')

    if not current_name or not new_name:
        return JsonResponse("Please provide both the current name and a new name", safe=False)
    if any(not c.isalnum() and c != " " for c in new_name):
        return JsonResponse("Please provide a valid name", safe=False)
    try:
        author = Author.objects.get(author_name=current_name)
    except Author.DoesNotExist:
        return JsonResponse("Author not found", safe=False)
    author.author_name = new_name
    author.save()
    return JsonResponse("Author updated successfully", safe=False)

def edit_book(request):
    book_id = request.GET.get('book_id')
    new_name = request.GET.get('name')
    new_price = request.GET.get('price')
    new_edition = request.GET.get('edition')
    new_description = request.GET.get('description')
    new_author_name = request.GET.get('author')
    
    try:
        int(book_id)
    except:
        return JsonResponse("Please provide a valid book ID", safe=False)
    try:
        book = Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return JsonResponse("Book not found", safe=False)
    if new_name:
        book.name = new_name
    if new_price:
        try:
            float(new_price)
        except:
            return JsonResponse("Please provide a valid price", safe=False)
        book.price = float(new_price)
    if new_edition:
        book.edition = new_edition
    if new_description:
        book.description = new_description
    if new_author_name:
        book.author.clear()
        author_names = [name.strip() for name in new_author_name.split(",")]
        for name in author_names:
            new_author_name, created = Author.objects.get_or_create(author_name=name)
            book.author.add(new_author_name)
    book.save()
    return JsonResponse("Book updated successfully", safe=False)

def addauthor(request):
    author_name = request.GET.get('name')
    author = Author.objects.filter(author_name=author_name)
    if author.exists():
        return JsonResponse("Author already exists", safe=False)
    if not author_name or any(not c.isalnum() and not c ==" " for c in author_name):
        return JsonResponse("Please provide a valid name", safe=False)
    else:
        Author.objects.create(author_name=author_name)
        return JsonResponse("Author added successfully", safe=False)
    
def addbook(request):
    book_name = request.GET.get('name')
    author_name = request.GET.get('author')
    book_price = request.GET.get('price')
    book_edition = request.GET.get('edition')
    book_description = request.GET.get('description')

    try:
        float(book_price)
    except:
        return JsonResponse("Please provide a valid price", safe=False)
    if  not (book_name and author_name and book_price and book_edition and book_description):
        return JsonResponse("Please provide all of the attributes", safe=False)
    author_names = [name.strip() for name in author_name.split(",")]
    existing_books = Book.objects.filter( name=book_name,price=book_price,edition=book_edition,description=book_description)
    for book in existing_books:
        existing_authors = set(book.author.values_list('author_name', flat=True))
        if existing_authors == set(author_names):
            return JsonResponse("Book already exists", safe=False)
    book = Book.objects.create(
        name=book_name,  
        price=book_price,
        edition=book_edition,
        description=book_description
        )
    for name in author_names:
        author, created = Author.objects.get_or_create(author_name=name)
        book.author.add(author)
    return JsonResponse("Book added successfully", safe=False)
    
def delete_author(request):
    author_id = request.GET.get('id')
    try:
        int(author_id)
    except ValueError:
        return JsonResponse( "Invalid author ID.", safe=False)
    author_to_delete = Author.objects.filter(id=author_id)
    if author_to_delete.exists():
        author_to_delete.delete()
        return JsonResponse( f"Author with ID {author_id} deleted successfully.", safe=False)
    else:
        return JsonResponse("author not found.", safe=False)

def delete_book(request):
    book_ids = request.GET.get('id')  # Get the comma-separated IDs from the query
    if not book_ids:
        return JsonResponse("No book IDs provided.", safe=False)

    try:
        book_ids = [int(book_id) for book_id in book_ids.split(',')]
    except ValueError:
        return JsonResponse("Invalid book IDs. All IDs must be integers.", safe=False)

    books_to_delete = Book.objects.filter(id__in=book_ids)
    if books_to_delete.exists():
        deleted_count = books_to_delete.count()
        books_to_delete.delete()
        return JsonResponse(f"{deleted_count} book(s) deleted successfully.", safe=False)
    else:
        return JsonResponse("No books found for the provided IDs.", safe=False)

def sort_alph(request):
    list_book = Book.objects.all().prefetch_related(Prefetch('author', to_attr='authors_list'))
    data = []
    for book in list_book:
        data.append({'id': book.id,'name': book.name,'authors': [author.author_name for author in book.authors_list], 'price': book.price,'edition': book.edition,'description': book.description,})
    if request.GET.get('order') == "desc":
        sorted_data = sorted(data, key=lambda x: x["name"], reverse=True)
    else:
        sorted_data = sorted(data, key=lambda x: x["name"])
    return JsonResponse(sorted_data, safe=False)

def sort_price(request):
    list_book = Book.objects.all().prefetch_related(Prefetch('author', to_attr='authors_list'))
    data = []
    for book in list_book:
        data.append({'id': book.id,'name': book.name,'authors': [author.author_name for author in book.authors_list], 'price': book.price,'edition': book.edition,'description': book.description,})
    if request.GET.get('order') == "desc":
        sorted_data = sorted(data, key=lambda x: x["price"], reverse=True)
    else:
        sorted_data = sorted(data, key=lambda x: x["price"])
    return JsonResponse(sorted_data, safe=False)

def search_book(request):
    book_name = request.GET.get('name')
    try:
        words = book_name.split()
    except:
        words = ""
    query = Q()
    for word in words:
        query &= Q(name__icontains=word) 
    books = Book.objects.filter(query).prefetch_related(Prefetch('author', to_attr='authors_list'))
    if not books.exists():
        return JsonResponse("Book not found.", safe=False)
    data = []
    for book in books:
        data.append({'id': book.id,'name': book.name,'authors': [author.author_name for author in book.authors_list], 'price': book.price,'edition': book.edition,'description': book.description,})
    return JsonResponse(data, safe=False)

def search_author(request):
    authorname= request.GET.get("name")
    try:
        words = authorname.split()
    except:
        words = ""
    query = Q()
    for word in words:
        query &= Q(author_name__icontains=word) 
    results = Author.objects.filter(query)
    if not results.exists():
        return JsonResponse("author not found.", safe=False)
    response_data = []
    for author in results:
        response_data.append({
            "author_id" :author.id,
            'author_name': author.author_name,
            'books': author.list_of_books() 
        })
    return JsonResponse(response_data, safe=False)    


def add_books(request):
    if request.method != "GET":
        return JsonResponse("Only GET requests are supported", safe=False)
    query = request.GET.get("query", "")
    total_books = int(request.GET.get("total_books", 2000))
    api_key = request.GET.get("api_key", "your google book api")
    if not query:
        return JsonResponse( "Query parameter is required", safe=False)
    url = "https://www.googleapis.com/books/v1/volumes"
    max_results = 40
    start_index = 0
    fetched_books = 0
    added_books = 0
    skipped_books = 0
    while added_books < total_books:
        remaining_books = total_books - added_books
        current_max_results = min(max_results, remaining_books)
        params = {
            "q": query,
            "startIndex": start_index,
            "maxResults": current_max_results,
            "key": api_key,
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            return JsonResponse("Failed to access Google Books API", safe=False)
        data = response.json()
        items = data.get("items", [])
        if not items:
            break  
        total_item = data.get("totalItems")
        for item in items:
            volume_info = item.get("volumeInfo", {})
            sale_info = item.get("saleInfo", {})
            title = volume_info.get("title", "")
            authors = volume_info.get("authors", [])
            description = volume_info.get("description", "")
            edition = volume_info.get("edition", "")
            list_price = sale_info.get("listPrice", {}).get("amount", 0)
            bid = item.get("id", "")  
            if not title or not bid:
                skipped_books += 1
                continue  
            book, created = Book.objects.get_or_create(
                bid=bid,  
                defaults={
                    "name": title,
                    "description": description,
                    "price": list_price,
                    "edition": edition,
                }
            )
            for author_name in authors:
                author, _ = Author.objects.get_or_create(author_name=author_name)
                book.author.add(author)
            if created:
                book.save()
                added_books += 1
            else:
                skipped_books += 1
        fetched_books += len(items)
        start_index += current_max_results
        if len(items) < current_max_results:
            break  
    return JsonResponse({
        "message": f"Successfully added {added_books} books.",
        "fetched_books": fetched_books,
        "added_books": added_books,
        "skipped_books": skipped_books,
        "total_item":total_item,
    })



def generate_report(request):
    total_books = Book.objects.count()
    average_price = Book.objects.aggregate(avg_price=Avg('price'))['avg_price']
    total_authors = Author.objects.count()
    books_per_author = (
    Author.objects.annotate(num_books=Count('books'))
    .aggregate(avg_books=Avg('num_books'))['avg_books'])

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="report.csv"'
    writer = csv.writer(response)

    writer.writerow(['Statistic', 'Value'])
    writer.writerow(['Total Books', total_books])
    writer.writerow(['Average Book Price', f"${average_price:.2f}" if average_price else "N/A"])
    writer.writerow(['Total Authors', total_authors])
    writer.writerow(['Average Books per Author', f"{books_per_author:.2f}" if books_per_author else "N/A"])
    writer.writerow([])
    writer.writerow(['Book Details'])
    writer.writerow(['Name', 'Price', 'Authors', 'Edition', 'Description'])
    for book in Book.objects.all():
        authors = ", ".join(author.author_name for author in book.author.all())
        writer.writerow([book.name, f"${book.price:.2f}", authors, book.edition, book.description])

    writer.writerow([])
    writer.writerow(['Author Details'])
    writer.writerow(['Name', 'Number of Books'])
    for author in Author.objects.all():
        writer.writerow([author.author_name, author.books.count()])

    return response


def change_price(request):
    current_price = request.GET.get('current_price')
    new_price = request.GET.get('new_price')
    lower_than = request.GET.get('lower_than')
    higher_than = request.GET.get('higher_than')
    if new_price:
        try:
            float(new_price)
        except:
            return JsonResponse("Please provide a valid price", safe=False)
    if current_price:
        try:
            float(current_price)
        except:
            return JsonResponse("Please provide a valid price", safe=False)
        books = Book.objects.filter(price = current_price)
    if lower_than:
        try:
            float(lower_than)
        except:
            return JsonResponse("Please provide a valid price", safe=False)
        books = Book.objects.filter(price__lt = lower_than)
    if higher_than:
        try:
            float(higher_than)
        except:
            return JsonResponse("Please provide a valid price", safe=False)
        books = Book.objects.filter(price__gt = higher_than)
    books.update(price = new_price)
    for book in books:
        book.save()
    return JsonResponse("Book updated successfully", safe=False)
