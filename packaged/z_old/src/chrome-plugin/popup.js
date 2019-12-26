/**
 * This script controls various aspects of the pop-up like rendering
 * its design, filling templates and reacting to clicks.
 * The popup is supposed to show an overview of the current visible
 * tiems on the server in a decently human-readable form.
*/

let app = (function(){
    let that = {};
    let syncButton = null;
    let clipTemplate = null;
    let $table = null;

    function onSyncButtonClick(){
        /**
         * Empties the list and reloads it from the server
        */
        $('#clipList').empty();
        clipboardApi.getAllClips(app, onClipsGet);
    }

    function createClip(dataItem) {
        /**
         * Creates a clip item. A clip in this context means a
         * Javascript object containing all information necessary
         * to display it correctly in the popup representing its state
         * on the server.
        */
        clip = {};
        clip._id = dataItem._id;
        clip.clipType = dataItem.mimetype;
        clip.parent = dataItem.parent;
        clip.children = [];
        date = new Date(dataItem.creation_date)
        options = {year: '2-digit', month: '2-digit', day: 'numeric',
                   timezone: 'UTC+1', hour: 'numeric', minute: 'numeric'};
        clip.date = date.toLocaleString('de-DE', options);
        return clip
    
    }

    function onClipsGet(data, textStatus, jqXHR){
        /**
         * Called when the request of all items from the server returns.
         * If successful, it populates the popup with all items in a
         * chronologically sorted, hierachical view
        */
        if (jqXHR.status === 200 ){
            let clips = [];
            let clipList = document.getElementById('clipList');
            // builds a list of parents
            for (let i = 0; i < data.length; i++){
                if (!( 'parent' in data[i] )) {
                    clips.push(createClip(data[i]));
                }
            }
            // inserts children into parents
            for (let i = 0; i < data.length; i++) {
                if ( 'parent' in data[i] ) {
                    for (let j = 0; j < clips.length; j++) {
                        if ( data[i].parent === clips[j]._id ) {
                            clips[j].children.push(createClip(data[i]))
                            break;
                        }
                    }
                }
            }
            // flattens nested list for display
            let flattened = [];
            for (let i = clips.length-1; i >= 0; i--) {
                flattened.push(clips[i]) 
                for ( let j = 0; j < clips[i].children.length; j++ ) {
                    flattened.push(clips[i].children[j])
                }
            }
            let context = {"clips": flattened}
            $('#clipList').append(this.clipTemplate(context))
            $('.clipDelete').click(onDeleteClick)
            $('.clipPaste').click(onPasteClick)
            $('.clipOpen').click(onOpenClick)
            $('.clipType').click(onOpenClick)
        }
        else {
            console.log(data)
        }
    }

    function onClipDeleted(data, textStatus, jqXHR) {
        /**
         * Called when the request to delete an item from the server returns
        */
        $("[data-id=" + data._id + "]").remove()
    }

    function onDeleteClick(e){
        /**
         * User clicked on the delete-button, issues request to server
         * for deltion of clicked item
        */
        _id = $(e.currentTarget).parent().data('id');
        clipboardApi.deleteClip(_id, onClipDeleted)
    }

    function onOpenClick(e) {
        /**
         * User clicked on open-button. Opens a new tab with the Url
         * representing the item on the server
        */
        _id = $(e.currentTarget).parent().data('id');
        if ( _id !== undefined ) {
            clipboardApi.openLink(_id)
        }
    }

    function onClipGet(data, textStatus, jqXHR){
        /**
         * When a single clip was received. Forwards the clip to the content
         * script so that it can be inserted into the currently displayed page
        */
        if ( jqXHR.status === 200 ) {
            chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
                chrome.tabs.sendMessage(tabs[0].id, {data: data},);
            });
        }
    }

    function onPasteClick(e){
        /**
         * User clicked on pase-button. Request the complete clip from the
         * server and then sends it to the content-script
        */
        _id = $(e.currentTarget).parent().data('id');
        clipboardApi.getClip(_id, onClipGet)
    }

    function init(){
        let source = document.getElementById("clipTemplate2").innerHTML;
        this.clipTemplate = Handlebars.compile(source)
        this.syncButton = $('#syncButton')
        this.syncButton.click(onSyncButtonClick)

        onSyncButtonClick()
    }

    that.init = init;
    that.loadClips = onSyncButtonClick

    return that;
}());
