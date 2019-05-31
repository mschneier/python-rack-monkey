window.addEventListener("load", () => {
  const url = window.location.href;
  const select = document.getElementById("view");
  if (url.includes("asset")) {
    select.selectedIndex = 1;
  } else if (url.includes("extended")) {
    select.selectedIndex = 2;
  } else if (url.includes("unracked")) {
    select.selectedIndex = 3;
  } else if (url.includes("search")) {
    select.selectedIndex = -1;
  } else {
    select.selectedIndex = 0;
  }
});

document.getElementById("view").addEventListener("change", () => {
  const view = document.getElementById("view").value;
  const url_string = window.location.search;
  const searchParams = new URLSearchParams(url_string);
  const customer = searchParams.get("customer");
  const role = searchParams.get("role");
  const hardware = searchParams.get("hardware");
  const os = searchParams.get("os");
  const sort = searchParams.get("sort");
  window.location.href = `/view/devices/${view}/?sort=${sort}&customer=${customer}&role=${role}&hardware=${hardware}&os=${os}`;
});
