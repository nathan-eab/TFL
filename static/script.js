const map = L.map("map", { zoomControl: false, inertia: true })
  .setView([51.5074, -0.1278], 14);

L.tileLayer(
  "https://tiles.stadiamaps.com/tiles/outdoors/{z}/{x}/{y}{r}.png",
  { maxZoom: 20, attribution: "&copy; OpenStreetMap" }
).addTo(map);

const drawer = document.getElementById("drawer");
const drawerContent = document.getElementById("drawerContent");
const toolbar = document.getElementById("toolbar");
const searchOverlay = document.getElementById("searchOverlay");
const searchInput = document.getElementById("searchInput");
const searchResults = document.getElementById("searchResults");

let stack = [];

function haptic() {
  navigator.vibrate?.(10);
}

function clearUI() {
  drawer.classList.remove("open");
  searchOverlay.classList.remove("open");
  drawerContent.innerHTML = "";
  searchResults.innerHTML = "";
  stack = [];
  toolbar.classList.remove("hidden");
}

function showDrawer(render, reset = false) {
  if (reset) stack = [];
  stack.push(render);
  drawerContent.innerHTML = "";
  render();
  drawer.classList.add("open");
  toolbar.classList.add("hidden");
}

function backDrawer() {
  stack.pop();
  if (!stack.length) {
    clearUI();
  } else {
    drawerContent.innerHTML = "";
    stack[stack.length - 1]();
  }
}

map.on("click", () => {
  if (searchOverlay.classList.contains("open")) {
    searchOverlay.classList.remove("open");
    toolbar.classList.remove("hidden");
  } else if (stack.length) {
    backDrawer();
  }
});

function openSearch() {
  haptic();
  clearUI();
  searchOverlay.classList.add("open");
  searchInput.focus();
  toolbar.classList.add("hidden");
}

/* SEARCH — SAME FLOW AS LOCATION */
searchInput.addEventListener("input", async (e) => {
  const q = e.target.value.trim();
  if (q.length < 2) return;

  const r = await fetch(`/search/${q}`);
  const groups = await r.json();

  searchResults.innerHTML = "";

  groups.forEach((g) => {
    const d = document.createElement("div");
    d.className = "search-item";
    d.textContent = g.name;
    d.onclick = () => {
      haptic();
      searchOverlay.classList.remove("open");
      showStopsGroup(g, true); // RESET STACK (CRITICAL)
    };
    searchResults.appendChild(d);
  });
});

function locateUser() {
  haptic();
  if (!navigator.geolocation) return;

  navigator.geolocation.getCurrentPosition((pos) => {
    const { latitude, longitude } = pos.coords;
    map.flyTo([latitude, longitude], 15, { duration: 1.2 });
    loadStops(latitude, longitude);
  });
}

async function loadStops(lat, lon) {
  const r = await fetch(`/stops/${lat}/${lon}`);
  const groups = await r.json();

  showDrawer(() => {
    drawerContent.innerHTML = "<h3>Nearby Stops</h3>";
    groups.forEach((g) => {
      const d = document.createElement("div");
      d.className = "stop";
      d.textContent = g.name;
      d.onclick = () => {
        haptic();
        showStopsGroup(g);
      };
      drawerContent.appendChild(d);
    });
  }, true);
}

/* STOP GROUP → STOP A / STOP B */
function showStopsGroup(group, reset = false) {
  showDrawer(() => {
    drawerContent.innerHTML = `<h3>${group.name}</h3>`;

    group.stops.forEach((s) => {
      const d = document.createElement("div");
      d.className = "stop";
      d.textContent = s.letter ? `Stop ${s.letter}` : "Stop";
      d.onclick = () => {
        haptic();
        loadArrivals(s.id, group.name);
      };
      drawerContent.appendChild(d);
    });
  }, reset);
}

/* ARRIVALS */
async function loadArrivals(id, name) {
  const r = await fetch(`/arrivals/${id}`);
  const data = await r.json();

  showDrawer(() => {
    drawerContent.innerHTML = `<h3>${name}</h3>`;
    data.forEach((a) => {
      const d = document.createElement("div");
      d.className = "arrival";
      d.innerHTML = `
        <span>${a.line} → ${a.destination}</span>
        <span class="badge">${a.minutes} min</span>
      `;
      drawerContent.appendChild(d);
    });
  });
}
