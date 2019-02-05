var clipboardApi = (function(){

    that = {}
    const BASE_URL = 'http://localhost:5000/'
    const BASE_CLIP_URL = BASE_URL.concat('clip/')

    function onClipSent(data, textStatus, jqXHR){
        if (jqXHR.status === 201 ){
            let i = new Object();
            i[data._id] = data
            chrome.storage.local.set(i) 
        }
    }

    function saveClip(data, mimetype, src_url=null, src_app=null, download_request=false){
        let clip = {};
        clip.data = data;
        clip.mimetype = mimetype;
        if (src_url) { clip.src_url = src_url };
        if (src_app) { clip.src_app = src_app };
        if (download_request) { clip.download_request = download_request };
        console.log(clip)
        $.ajax(BASE_CLIP_URL, {
            contentType: 'application/json',
            data: JSON.stringify(clip),
            method: 'POST',
        }).done(onClipSent)
    }

    function getAllClips(context, callback){
        $.ajax(BASE_CLIP_URL, {
            contentType: 'application/json',
            context: context,
        }).done(callback)
    }

    function deleteClip(_id, callback) {
        $.ajax(BASE_CLIP_URL + _id + '/', {
            contentType: 'application/json',
            method: 'DELETE',
        }).done(callback)
    }

    that.saveClip = saveClip;
    that.getAllClips = getAllClips;
    that.deleteClip = deleteClip;


    return that;

}());


