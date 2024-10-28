def format_authors(authors):
    """ Format the list of authors returned by Google API into single string with seperator | """
    return ' | '.join(authors) if authors else 'Authors not found' # Return authors or message if not found

def format_categories(categories):
    """ Format the list of categories returned by Google API into single string with seperator | """
    return ' | '.join(categories) if categories else '-' # Return categories or a '-' if not found

def format_short_description(description):
    """ Take long description from Google API and trim it to a max of 350 characters """
    return description[:350] if len(description) > 350 else description #Return the shortened description of the original if it is less that 350 chars

def format_cover_image(imageLinks):
     """ Get the cover image thumbnail or return a placeholder if thumbnail does not exist """
     no_cover_image = '/static/images/cover-not-availble-image.jpg'  # placeholder image
     return imageLinks.get('thumbnail', no_cover_image) if imageLinks else no_cover_image

def sortSearchContent(results):
    results_list = []  # initialize array to hold results of API results

    # Iterate through each item in the results.  Get the needed information from the volumeInfo or return a placeholder if the data is missing.
    for item in results:
        volume_info = item.get('volumeInfo', {}) # Extract the volume information or empty dictionary if not found
        results_list.append({
             'id' : item.get('id'),
            'title' : volume_info.get('title', 'Title not available'),
            'authors' : format_authors(volume_info.get('authors',[])),
            'short_description': format_short_description(volume_info.get('description', 'Description not available')),
            'description' : volume_info.get('description', 'Description not available'),
            'cover_image' : format_cover_image(volume_info.get('imageLinks', {})),
            'avg_rating' : volume_info.get('averageRating', 0.0),
            'page_count' : volume_info.get('pageCount', '-'),
            'date_published' : volume_info.get('publishedDate', '-'),
            'publisher' : volume_info.get('publisher', '-'),
            'categories' : format_categories(volume_info.get('categories', []))
        })

    return results_list