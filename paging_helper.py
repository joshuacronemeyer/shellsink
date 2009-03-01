class PagingHelper:
  
  def __init__(self, page, root_url, url_params):
    if page == "":
      page = 1
    self.page = int(page)
    self.root_url = root_url
    self.url_params = url_params

  def has_next(self):
    return True

  def has_prev(self):
    return self.page > 1

  def url_builder(self, page_num):
    url = '/%(root)s?page=%(page_num)d' % {'root': self.root_url, 'page_num': page_num}
    for param in self.url_params:
      url = url + '&' + param
    return url

  def next_url(self):
    return self.url_builder(self.page + 1)

  def previous_url(self):
    return self.url_builder(self.page - 1)
