chrome.runtime.onMessage.addListener(
    function(request, sender, sendResponse) {
        //https://stackoverflow.com/questions/1064089/inserting-a-text-where-cursor-is-using-javascript-jquery
        let activeElem = document.activeElement;
        let selStart = activeElem.selectionStart;
        let front = (activeElem.value).substring(0, selStart);
        let back = (activeElem.value).substring(selStart, activeElem.value.length);
        activeElem.value = front + request.data + back;
  }
);
