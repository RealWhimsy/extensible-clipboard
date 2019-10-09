/**
 * This class is used in various contexts and is resposible to send a clip
 * to the remote server specified in base_url via the options-page.
 * It provides different functionalities as they are required by different
 * parts of the extension such as requesting a list of clips or deleting one.
*/

var clipboardApi = (function(){

    that = {}
    let base_url = 'http://localhost:5000/'
    let base_clip_url = base_url.concat('clip/')

    function onUrlChanged(url) {
        /**
         * This method needs to be called when the URL which requests are
         * supposed to be made to needs to be changed.
         * It can either be called with a string or an Object as the
         * URL is saved in the storage.
        */
        if ( url instanceof Object ){
            url = url.serverUrl;
        }
        if ( url === undefined ) {
            return
        }
        base_url = url;
        base_clip_url = base_url.concat('clip/');
    }

    function saveClip(data, mimetype, src_url=null, src_app=null, download_request=false){
        /**
         * Sends a clip to the server. Data and Mimetype need to be specified, everything
         * else is optional and can be added if need be.
         * Metadata will be written into the request header since the API change
        */
        let headers = {};
        if (src_url) { headers['X-C2-src_url'] = src_url };
        if (src_app) { headers['X-C2-src_app'] = src_app };
        if (download_request) { headers['X-C2-download_request'] = download_request };
        $.ajax(base_clip_url, {
            contentType: mimetype,
            data:data,
            method:'POST',
            headers:headers,
        });
    }

    function getAllClips(context, callback){
        /**
         * Returns all visible clips from the server.
         * Please note that the data themselves will not be returned as this
         * request is informational by nature. To get the data for a specific
         * clip, it has to be requested via getClip
        */
        $.ajax(base_clip_url, {
            contentType: 'application/json',
            context: context,
        }).done(callback)
    }

    function deleteClip(_id, callback) {
        /**
         * Prompts the server to delete the clip specified by _id.
        */
        $.ajax(base_clip_url + _id + '/', {
            contentType: 'application/json',
            method: 'DELETE',
        }).done(callback)
    }

    function getClip(_id, callback){
        /**
         * Queries a specific clip from the database.
         * This will include its data.
        */
        $.ajax(base_clip_url + _id + '/', {
            contentType: 'application/json',
            method: 'GET'
        }).done(callback)
    }

    function openLink(_id) {
        /**
         * Builds an URL for the remote server under which
         * the resource specified by _id can be found
        */
        window.open(base_clip_url + _id + '/', '_blank')
    }

    that.saveClip = saveClip;
    that.getAllClips = getAllClips;
    that.getClip = getClip;
    that.deleteClip = deleteClip;
    that.onUrlChanged = onUrlChanged;
    that.openLink = openLink;
    url = chrome.storage.sync.get('serverUrl', onUrlChanged)
    return that;

}());


