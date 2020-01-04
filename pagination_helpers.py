from math import ceil, floor

from django.core.paginator import Paginator


class Pagination(Paginator):
    def __init__(self,
                 current_page_index,
                 object_list,
                 per_page=50,
                 orphans=15,
                 allow_empty_first_page=True,
                 pages_to_show=7
                 ):
        self.pages_to_show = pages_to_show
        self.current_page_index = int(current_page_index)

        super(Pagination, self).__init__(object_list=object_list,
                                         per_page=per_page,
                                         orphans=orphans,
                                         allow_empty_first_page=allow_empty_first_page)
    def get_active_page(self):
        return self.get_page(self.current_page_index)

    def get_last_page(self):
        return self.get_page(-1)

    def get_first_page(self):
        return self.get_page(1)

    def get_visible_pages(self):
        pages_to_show = self.pages_to_show

        if not self.count:
            return []

        if self.num_pages > pages_to_show:
            endpoints = int(floor(pages_to_show/2))
            pages_to_show_start = self.current_page_index-1-endpoints
            pages_to_show_end = self.current_page_index+endpoints

            if pages_to_show_start<0:
                pages_to_show_end+=(pages_to_show_start*-1)
            if pages_to_show_end>self.num_pages:
                pages_to_show_start=self.num_pages-pages_to_show

            pages_to_show_start = max(0,pages_to_show_start)
            pages_to_show_end = min(self.num_pages, pages_to_show_end)

        else:
            pages_to_show_start = 0
            pages_to_show_end = self.num_pages

        return [self.get_page(i) for i in self.page_range[pages_to_show_start:pages_to_show_end]]
