from math import ceil, floor

class Pagination(object):
    def __init__(self, active_page, item_count, limit=50):
        try:
            self.active_page = max(int(active_page),1)
        except (TypeError,ValueError):
            self.active_page = 1

        try:
            self.limit = max(int(limit),1)
        except (TypeError,ValueError):
            self.limit = 50

        self.item_count = item_count

        self.total_pages = max(int(ceil(self.item_count / self.limit)), 1)
        self.active_page = min(max(int(self.active_page),1), self.total_pages)

        self._update_pagination_data()

    def _update_pagination_data(self):

        pages_to_show = 7
        if self.total_pages > pages_to_show:
            endpoints = int(floor(pages_to_show/2))
            pages_to_show_start = self.active_page-1-endpoints
            pages_to_show_end = self.active_page+endpoints

            if pages_to_show_start<0:
                pages_to_show_end+=(pages_to_show_start*-1)
            if self.active_page+endpoints>self.total_pages:
                surplus = self.total_pages-self.active_page+endpoints
                pages_to_show_start-=surplus

            if pages_to_show_start < 0:
                pages_to_show_start = 0
            if pages_to_show_end > self.total_pages:
                pages_to_show_end = self.total_pages
        else:
            pages_to_show_start = 0
            pages_to_show_end = self.total_pages

        pages = [{'start':p*self.limit,'number':i+1} for i,p in enumerate(range(0,self.total_pages))]
        pages = pages[pages_to_show_start:pages_to_show_end]
        subset_start = (self.active_page-1)*self.limit
        subset_end = subset_start+self.limit

        self.subset_start = subset_start
        self.subset_end = subset_end
        self.item_count = self.item_count
        self.pages = pages
        self.is_last_page = self.active_page>=self.total_pages
        self.is_first_page = self.active_page<=1

        self.previous_page = max(self.active_page - 1,1)
        self.next_page = min(self.active_page+1, self.total_pages)

        self.start = self.active_page*self.limit
        self.next_page_start = self.next_page*self.limit
        self.previous_page_start = self.previous_page*self.limit

        self.prev_page = self.previous_page
        self.prev_page_start = self.previous_page_start
