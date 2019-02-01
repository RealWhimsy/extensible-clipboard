function onMessageInc(request, sender, callback){
    if (request.msg == "sync"){
        console.log('app received call')
        console.log(callback)
        callback()
        clipboardApi.getAllClips()
    }
}

function onContextClick(info, tabs){
    let data, mimetype, src_url, src_app
    if ('selectionText' in info){
        console.log(info);
        data = info.selectionText;
        mimetype = 'text/plain';
    }
    else if ('linkUrl' in info){
        data = '<a href="' + info.linkUrl + '"></a>';
        mimetype = 'text/html';
    }
    else if ('mediaType' in info){
        console.log(info);
        return
    }
    
    src_url = info.pageUrl
    src_app = "Web browser"
    clipboardApi.saveClip(data, mimetype, src_url, src_app)
}

function initContextMenu(){
    var context_select = chrome.contextMenus.create({
        "id": "context_selection",
        "title": "Send to C2", 
        "contexts":["selection", "link", "image", "video", "audio"]
    });
}

function initListeners(){
    chrome.runtime.onMessage.addListener(onMessageInc)
    chrome.contextMenus.onClicked.addListener(onContextClick)
}

chrome.runtime.onInstalled.addListener(function() {
    initContextMenu();
    initListeners();
});
