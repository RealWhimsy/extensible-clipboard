let changeColor = document.getElementById('changeColor');
changeColor.onclick = function(){
    chrome.runtime.sendMessage({greeting: "hello"}, function(response) {
        console.log(response.farewell);
    });
}
