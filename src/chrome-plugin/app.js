function onContextClick(info, tabs){
    clip = {}
    console.log(info)
    if ('selectionText' in info){
        console.log(info);
        clip.data = info.selectionText;
        clip.mimetype = 'text/plain';
    }
    else if ('mediaType' in info){
        clip.data = info.srcUrl;
        clip.mimetype = 'text/plain';
        clip.download_request = 'true';
    }
    else if ('linkUrl' in info){
        clip.data = '<a href="' + info.linkUrl + '"></a>';
        clip.mimetype = 'text/html';
    }
    clip.src_url = info.pageUrl
    clip.src_app = "Web browser"
    clipboardApi.saveClip(clip)
}

function initContextMenu(){
    var context_select = chrome.contextMenus.create({
        "id": "context_selection",
        "title": "Send to C2", 
        "contexts":["selection", "link", "image", "video", "audio"]
    });
}

function initListeners(){
    chrome.contextMenus.onClicked.addListener(onContextClick)
}

chrome.runtime.onInstalled.addListener(function() {
    initContextMenu();
    initListeners();
});
