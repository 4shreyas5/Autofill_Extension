document.addEventListener('DOMContentLoaded', function() {
    const saveDataButton = document.getElementById('saveData');
    const autoFillButton = document.getElementById('autoFill');
    const inputData = document.getElementById('inputData');
  
    // Save data to storage
    saveDataButton.addEventListener('click', function() {
      const data = inputData.value;
      chrome.storage.sync.set({ 'storedData': data }, function() {
        console.log('Data saved:', data);
      });
    });
  
    // Autofill data from storage
    autoFillButton.addEventListener('click', function() {
      chrome.storage.sync.get(['storedData'], function(result) {
        const storedData = result.storedData;
        if (storedData) {
          // Autofill the input field on the active tab
          chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
            const activeTab = tabs[0];
            chrome.tabs.sendMessage(activeTab.id, { type: 'autofill', data: storedData });
          });
        } else {
          console.log('No data stored.');
        }
      });
    });
  });
  