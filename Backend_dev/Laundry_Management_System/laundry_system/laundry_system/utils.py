from math import ceil
from django.core.paginator import Paginator


def paginate(request, data=None, page=1, per_page=5):
    base_url = request.build_absolute_uri(request.path)
    total_items = len(data)
    total_pages = ceil(total_items / per_page)
    
    start = (page - 1) * per_page
    end = start + per_page
    parginated_item = data[start:end]

    next_page = page + 1 if page < total_pages else None
    previous_page = page - 1 if page > 1 else None

    result = {
        'page': page,
        'per_page': per_page,
        'total_page': total_pages,
        'total_items': total_items,
        'data': parginated_item,
        'next_page': next_page,
        'previous_page': previous_page
    }

    if base_url:
        result['next_page_url'] = f'{base_url}?page={next_page}' if next_page else None
        result['previous_page_url'] = f'{base_url}?page={previous_page}' if previous_page else None

    return result


def paginate_queryset(queryset, page=1, per_page=3):
    paginator = Paginator(queryset, per_page)
    page_obj = paginator.get_page(page)

    return {
        'page': page,
        'total_pages': paginator.num_pages,
        'total_items': paginator.count,
        'data': list(page_obj)
    }