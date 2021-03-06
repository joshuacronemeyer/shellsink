"""
This file is part of Shell-Sink.
Copyright Joshua Cronemeyer 2008, 2009

Shell-Sink is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Shell-Sink is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License v3 for more details.

You should have received a copy of the GNU General Public License
along with Shell-Sink.  If not, see <http://www.gnu.org/licenses/>.
"""
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
