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

    function saveClip(clip){
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

    that.saveClip = saveClip;
    that.getAllClips = getAllClips;


    return that;

}());


