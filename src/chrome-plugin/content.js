/**
 * Content script (running in tab)
 * Called when paste is clicked for an item and pastes its content
 * into the current selected element of the DOM. Works technically
 * well for input-boxes but a does not work on every website because
 * of the JS-bloat apparently
*/

chrome.runtime.onMessage.addListener(
    function(request, sender, sendResponse) {
        //https://stackoverflow.com/questions/1064089/inserting-a-text-where-cursor-is-using-javascript-jquery
        let activeElem = document.activeElement;
        let selStart = activeElem.selectionStart;
        let front = (activeElem.value).substring(0, selStart);
        let back = (activeElem.value).substring(selStart, activeElem.value.length);
        if ( request.data instanceof Object ) {
            request.data = JSON.stringify(request.data)
        }
        activeElem.value = front + request.data + back;
  }
);
