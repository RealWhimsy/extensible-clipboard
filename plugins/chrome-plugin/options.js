// Saves options to chrome.storage, taken from the Extension Tutorial
function save_options() {   
    var serverUrl = document.getElementById('serverUrl').value;
    chrome.storage.sync.set({
        serverUrl: serverUrl
    }, function() {
    // Update status to let user know options were saved.
    var status = document.getElementById('status');
    status.textContent = 'Options saved.';
    setTimeout(function() {
        status.textContent = '';
    }, 750);
  });
}

// Restores the options
function restore_options() {
    chrome.storage.sync.get({
        serverUrl: 'Enter URL here'
    }, function(items) {
        document.getElementById('serverUrl').value = items.serverUrl;
  });
}
document.addEventListener('DOMContentLoaded', restore_options);
document.getElementById('save').addEventListener('click',
    save_options);
