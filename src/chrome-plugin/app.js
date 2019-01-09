function genericOnClick(info, tabs){
    //https://stackoverflow.com/questions/6418220/javascript-send-json-object-with-ajax
    console.log(info)
    var xhr = new XMLHttpRequest()
    xhr.open("POST", "http://localhost:5000/clip/", true)
    xhr.setRequestHeader("Content-Type", "application/json", "charset=utf-8")
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4) {
            console.log(xhr.responseText)
        }
    }
    xhr.send(JSON.stringify({'clip': 'Test from Browser', 'mimetype': 'text/plain'}));
}

function initListeners(){
    var context_entry = chrome.contextMenus.create({
        "id": "context_selection",
        "title": "Send to C2", 
        "contexts":["selection"]});
}

chrome.runtime.onInstalled.addListener(function() {
    console.log('installed')
    initListeners()

    chrome.contextMenus.onClicked.addListener(
        genericOnClick
    )
});
