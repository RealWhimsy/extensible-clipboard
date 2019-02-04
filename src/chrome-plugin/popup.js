var app = (function(){
    var that = {};
    var syncButton = null;
    var clipTemplate = null;
    var $table = null;

    function onSyncButtonClick(){
        $("#clipList").empty()
        clipboardApi.getAllClips(app, onClipsGet)
    }

    function onClipsGet(data, textStatus, jqXHR){
        if (jqXHR.status === 200 ){
            var clips = [];
            var clipList = document.getElementById('clipList');
            for (var i = 0; i < data.length; i++){
                clip = {};
                clip.clipText = data[i].data.toString()
                clip.clipType = data[i].mimetype
                if (data[i].mimetype === 'text/html'){
                    a = $(clip.clipText).attr('href')
                    clip.clipText = clip.clipText.replace('<a ', '<a target="_blank" ')
                    clip.clipText = clip.clipText.replace('</a>', a + '</a>')
                }
                clips.push(clip);
            }
            var _new = this.clipTemplate({clips: clips})
            this.$table.append(_new)
        }
    }

    function init(){
        this.clipTemplate = Handlebars.compile(
            $("#clipTemplate").html()
        )
        this.$table = $('#clipTable tbody')

        this.syncButton = $('#syncButton')
        this.syncButton.click(onSyncButtonClick)
    }

    that.init = init;
    that.loadClips = onSyncButtonClick

    return that;
}());
