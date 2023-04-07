const url = document.currentScript.getAttribute('data-url');
let table_select = document.getElementById('tables');

table_select.onchange = function() {
  table = table_select.value;
  console.log(table)
  console.log(url)
  let data = new FormData()
  data.append("table", table)
  fetch(url, {
    "method": "POST",
    "body": data,
  })
  .then(response=> response.text())
  .then(function(text){
    document.getElementById("table-container").innerHTML = text;
});
}