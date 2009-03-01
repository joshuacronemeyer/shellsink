/**
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
**/
function showQuickTag(index) {
  element = $('quick-tag'+index);
  if (element.style.display == 'none')
    element.style.display = 'inline';
  else
    element.style.display = 'none';
  return;
}

function editAnnotation(index) {
  $('annotation'+index).style.display = 'none';
  $('annotation-input-div'+index).style.display = 'block';
}

function updateTag(index) {
  new Ajax.Updater('tags'+index, '/addTag',{ method:'post', parameters: {tag: $('tagvalue'+index).value, id: $('id'+index).value}});
  showQuickTag(index);
  $('tagvalue'+index).value = "";
}

function updateFilter(id) {
  new Ajax.Request('/setAtomPreference',{ method:'post', parameters: {filter: $('filter').value, id: id}});
}

function disableAtom(id) {
  new Ajax.Request('/setAtomPreference',{ method:'post', parameters: {disable_atom: $('disable_atom').checked, id: id}});
}

function updateAnnotation(index) {
  new Ajax.Updater('annotation-block'+index, '/addAnnotation', {method:'post', parameters: {annotation: $('annotation-input'+index).value, id: $('id'+index).value}});
}

function limitSearchTerms(element) {
  terms = element.value.split(" ");
  if (terms.length > 2) {
    $('search message').update('<a href="http://shell-sink.blogspot.com/2008/12/why-search-terms-are-limited-to-two.html" class="red">Shellsink cannot accept more than 2 search keywords.</a>');
  }
  else {
    $('search message').update();
  }
}

function disableAtomSelect(element, id) {
  if (element.checked == true) {
    $('filter').disabled = true;
  }
  else {
    $('filter').disabled = false;
  }
  disableAtom(id);
}
