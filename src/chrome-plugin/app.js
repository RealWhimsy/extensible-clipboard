/**
 * This script acts as the background script and gets called whenever
 * the extension is started. It initializes the context menu.
*/

function onContextClick(info, tabs){
    /**
     * Called when user clicks on the context entry.
     * Decides if the target was either a selection, a media or a link
     * and acts accordingly. Send data to the remote server
    */
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
    /**
     * Creates the context entry. Note that there is no (simple?) way to
     * create an entry for the omnibox
    */
    var context_select = chrome.contextMenus.create({
        "id": "context_selection",
        "title": "Send to C2", 
        "contexts":["selection", "link", "image", "video", "audio"]
    });
}

function onStorageChanged(changes, areaName){
    /**
     * Updates the class responsible for sending requests whenever the user
     * enters a different URL via the options page
    */
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
