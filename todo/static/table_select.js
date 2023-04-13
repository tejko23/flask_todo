const url = document.currentScript.getAttribute('data-url');
let table_select = document.getElementById('tables');

table_select.onchange = function() {
  table = table_select.value;
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

function checkDueDates() {
  var dueDates = document.querySelectorAll("td.td-due-date");

  for (var i = 0; i < dueDates.length; i++) {
    var dueDate = dueDates[i].textContent;

    if (dueDate.trim() !== "") {
      var dateToCompare = new Date(dueDate);
      var currentDate = new Date();
      dateToCompare.setHours(0, 0, 0, 0);
      currentDate.setHours(0, 0, 0, 0);

      if (currentDate.getTime() === dateToCompare.getTime()){
        dueDates[i].classList.add("text-warning");
      } else if (currentDate.getTime() > dateToCompare.getTime()) {
        dueDates[i].classList.add("text-danger");
      } else {}
    }
  }
};

window.addEventListener("load", checkDueDates);

let table_container = document.getElementById("table-container");
table_container.addEventListener("DOMSubtreeModified", checkDueDates);