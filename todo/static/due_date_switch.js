const switchbox = document.getElementById("due-date-switch");
const dateElement = document.getElementById("due-date");

switchbox.addEventListener("change", function(){
  if (this.checked) {
    dateElement.style.display = "block";
  } else {
    document.getElementById("due-date-input").value = "";
    dateElement.style.display = "none";
  }
});