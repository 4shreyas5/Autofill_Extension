document.addEventListener('DOMContentLoaded', function () {
    var sendButton = document.getElementById('sendButton');
  
    sendButton.addEventListener('click', function () {
      chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
        var currentUrl = tabs[0].url;
        sendUrlToServer(currentUrl);
      });
    });
  
    function sendUrlToServer(url) {
      var serverEndpoint = 'yha server endpoint jayega';
      
      fetch(serverEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url }),
      })
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to send URL to the server');
        }
        console.log('URL sent successfully!');
      })
      .catch(error => {
        console.error('Error:', error);
      });
    }
  });
  