def format_authors(authors):
    return ' | '.join(authors) if authors else 'Authors not found'

def format_categories(categories):
        return ' | '.join(categories) if categories else '-'

def format_short_description(description):
     return description[:350] if len(description) > 350 else description

def format_cover_image(imageLinks):
     no_cover_image = '/static/images/cover-not-availble-image.jpg'
     return imageLinks.get('thumbnail', no_cover_image) if imageLinks else no_cover_image

def sortSearchContent(results):
    results_list = []

    for item in results:
        volume_info = item.get('volumeInfo', {})
        results_list.append({
             'id' : item.get('id'),
            'title' : volume_info.get('title', 'Title not available'),
            'authors' : format_authors(volume_info.get('authors',[])),
            'short_description': format_short_description(volume_info.get('description', 'Description not available')),
            'description' : volume_info.get('description', 'Description not available'),
            'cover_image' : format_cover_image(volume_info.get('imageLinks', {})),
            'avg_rating' : volume_info.get('averageRating', '-'),
            'page_count' : volume_info.get('pageCount', '-'),
            'date_published' : volume_info.get('publishedDate', '-'),
            'publisher' : volume_info.get('publisher', '-'),
            'categories' : format_categories(volume_info.get('categories', []))
        })

    return results_list