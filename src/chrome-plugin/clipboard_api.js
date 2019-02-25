var clipboardApi = (function(){

    that = {}
    let base_url = 'http://localhost:5000/'
    let base_clip_url = base_url.concat('clip/')

    function onClipSent(data, textStatus, jqXHR){
        if (jqXHR.status === 201 ){
            let i = new Object();
            i[data._id] = data
            chrome.storage.local.set(i) 
        }
    }

    function onUrlChanged(url) {
        if ( url instanceof Object ){
            url = url.serverUrl;
        }
        console.log(url)
        base_url = url;
        base_clip_url = base_url.concat('clip/');
    }

    function saveClip(data, mimetype, src_url=null, src_app=null, download_request=false){
        console.log('saving')
        let headers = {};
        if (src_url) { headers['X-C2-src_url'] = src_url };
        if (src_app) { headers['X-C2-src_app'] = src_app };
        if (download_request) { headers['X-C2-download_request'] = download_request };
        console.log(headers)
        $.ajax(base_clip_url, {
            contentType: mimetype,
            data:data,
            method:'POST',
            headers:headers,
        }).done(onClipSent)
    }

    function getAllClips(context, callback){
        $.ajax(base_clip_url, {
            contentType: 'application/json',
            context: context,
        }).done(callback)
    }

    function deleteClip(_id, callback) {
        $.ajax(base_clip_url + _id + '/', {
            contentType: 'application/json',
            method: 'DELETE',
        }).done(callback)
    }

    function getClip(_id, callback){
        $.ajax(base_clip_url + _id + '/', {
            contentType: 'application/json',
            method: 'GET'
        }).done(callback)
    }

    that.saveClip = saveClip;
    that.getAllClips = getAllClips;
    that.getClip = getClip;
    that.deleteClip = deleteClip;
    that.onUrlChanged = onUrlChanged;
    url = chrome.storage.sync.get('serverUrl', onUrlChanged)
    return that;

}());


