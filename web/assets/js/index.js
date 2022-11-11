console.log('Hello');

var host = 'https://fejh6lq5n2.execute-api.us-east-1.amazonaws.com/dev-v1';

// var mysdk = null;
// function setSdk() {
//   if (mysdk == null) {
//     var api = document.querySelector('#api').value;
//     console.log('API:', api);

//     mysdk = apigClientFactory.newClient({
//       apiKey: api
//     });
//   }
// }

function getAPIKey() {
  return document.querySelector('#api').value;
}

function callSearchApi(query) {
  var xhr = new XMLHttpRequest();
  xhr.open('GET', host + '/search?q=' + query, true);
  xhr.setRequestHeader('x-api-key', getAPIKey());

  xhr.onload = function () {
    if (xhr.status == 200) {
      showImages(JSON.parse(xhr.response));
    } else {
      console.log('Error..');
      console.log(xhr.response);
    }
  };
  xhr.send();
}

window.addEventListener('load', function() {
  document.querySelector('#searchbtn').addEventListener('click', function() {
    var term = document.querySelector('#search').value;
    callSearchApi(term);
  });
});

function showImages(data) {
  document.getElementById('images').innerHTML = '';
  if (data.results.length == 0) {
    document.getElementById('images').innerHTML = '<h3>No Results Found</h3>';
  }

  for (let i = 0; i < data.results.length; i++) {
    url = data.results[i].url;
    tag = '<img src="' + url + '" alt="your image" height=200></br>';
    document.getElementById('images').innerHTML += tag
  }
}

window.addEventListener('load', function() {
  document.querySelector('#read-file').addEventListener('click', function() {
    if (document.querySelector('#file').value == '') {
      console.log('No file selected');
      return;
    }

    var username = document.querySelector('#username').value;
    var labels = document.querySelector('#labels').value;
    var file = document.querySelector('#file').files[0];
    var filename = username + '-' + file.name;
    var filetype = file.type;

    console.log(labels);
    console.log(filename, filetype);
    
    const formData = new FormData();
    formData.append('File', file);

    var xhr = new XMLHttpRequest();
    xhr.open('PUT', host + '/upload', true);
    xhr.setRequestHeader('x-api-key', getAPIKey());
    xhr.setRequestHeader('x-amz-meta-customLabels', labels);
    xhr.setRequestHeader('objkey', filename);
    xhr.setRequestHeader('Content-Type', filetype);

    xhr.onload = function () {
      if (xhr.status == 200) {
        console.log('Upload success..');
        console.log(xhr.response);
      } else {
        console.log('Error..');
        console.log(xhr.response);
      }
    };
    xhr.send(formData.get('File'));
  });
});
