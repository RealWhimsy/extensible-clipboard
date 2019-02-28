function onContextClick(info, tabs){
    let data, mimetype, src_app, src_url, dlr
    if ('selectionText' in info){
        data = info.selectionText;
        mimetype = 'text/plain';
    }
    else if ('mediaType' in info){
        data = info.srcUrl;
        mimetype = 'text/plain';
        dlr = 'true';
    }
    else if ('linkUrl' in info){
        data = '<a href="' + info.linkUrl + '">' + info.linkUrl + '</a>';
        mimetype = 'text/html';
    }
    src_url = info.pageUrl
    src_app = "Web browser"
    clipboardApi.saveClip(data, mimetype, src_url, src_app, dlr)
}

function initContextMenu(){
    var context_select = chrome.contextMenus.create({
        "id": "context_selection",
        "title": "Send to C2", 
        "contexts":["selection", "link", "image", "video", "audio"]
    });
}

function onStorageChanged(changes, areaName){
    if ( 'serverUrl' in changes ) {
        clipboardApi.onUrlChanged(changes.serverUrl.newValue)
    }
}

function initListeners(){
    chrome.contextMenus.onClicked.addListener(onContextClick)
    chrome.storage.onChanged.addListener(onStorageChanged)
}

function init() {
    initContextMenu();
    initListeners();
}

chrome.runtime.onInstalled.addListener(function() {
    init()
});

chrome.runtime.onStartup.addListener(function() {
    init()
});
