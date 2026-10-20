/* =============================================================================
   web/static/systemlab.js  -  kleine Helfer im Browser (die Seite geht auch OHNE JavaScript)
   -----------------------------------------------------------------------------
   1) Hell/Dunkel-Knopf          Wahl wird im Browser gemerkt (localStorage)
   2) Ctrl+K                     springt ins Suchfeld
   3) Code-Beispiele             Reiter Python / C++ / C# statt alles untereinander, "Kopieren"-Knopf
   4) Interaktive Schaltpläne    Slider <-> Zahlenfeld, nach jeder Änderung nur den Plan neu holen
                                 (/schaltung/<id>/?...  -> web/wiki/views.py schaltung)
   5) Formulare mit data-sofort  schicken sich bei jeder Auswahl selbst ab (Farbcode-Rechner)
   6) Filterfeld                 blendet in der Rechner-Übersicht nicht passende Rechner aus
   7) Animationen                spielt die vorab gezeichneten Bilder ab (Trafo), Pause-Knopf
   ============================================================================= */
(function () {
  "use strict";

  // ---- 1) Hell / Dunkel -----------------------------------------------------
  var knopf = document.getElementById("modus-knopf");
  if (knopf) {
    knopf.addEventListener("click", function () {
      var jetzt = document.documentElement.dataset.modus ||
        (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dunkel" : "hell");
      var neu = jetzt === "dunkel" ? "hell" : "dunkel";
      document.documentElement.dataset.modus = neu;
      try { localStorage.setItem("systemlab-modus", neu); } catch (e) { /* privates Fenster: egal */ }
    });
  }

  // ---- 2) Ctrl+K -> Suche ------------------------------------------------------
  document.addEventListener("keydown", function (ev) {
    if ((ev.ctrlKey || ev.metaKey) && ev.key.toLowerCase() === "k") {
      var feld = document.getElementById("suchfeld");
      if (feld) { ev.preventDefault(); feld.focus(); feld.select(); }
    }
  });

  // ---- 3) Code: Reiter und Kopieren -------------------------------------------
  document.querySelectorAll("[data-reiter]").forEach(function (gruppe) {
    var bloecke = gruppe.querySelectorAll(".code-block");
    if (bloecke.length < 2) return;
    var leiste = document.createElement("div");
    leiste.className = "reiter-leiste";
    leiste.setAttribute("role", "tablist");
    bloecke.forEach(function (block, i) {
      var b = document.createElement("button");
      b.type = "button";
      b.textContent = block.dataset.sprache;
      b.setAttribute("role", "tab");
      b.addEventListener("click", function () { zeigen(i); });
      leiste.appendChild(b);
    });
    function zeigen(nummer) {
      bloecke.forEach(function (block, i) { block.classList.toggle("sichtbar", i === nummer); });
      leiste.querySelectorAll("button").forEach(function (b, i) { b.setAttribute("aria-selected", i === nummer); });
    }
    gruppe.insertBefore(leiste, gruppe.firstChild);
    gruppe.classList.add("aktiv");
    zeigen(0);
  });
  document.addEventListener("click", function (ev) {
    var b = ev.target.closest("[data-kopieren]");
    if (!b) return;
    var code = b.closest(".code-block").querySelector("code").innerText;
    if (navigator.clipboard) {
      navigator.clipboard.writeText(code).then(function () {
        b.textContent = "Kopiert ✓";
        setTimeout(function () { b.textContent = "Kopieren"; }, 1500);
      });
    }
  });

  // ---- 4) Interaktive Schaltpläne ---------------------------------------------
  function zahlText(wert, ganzzahl) {
    if (ganzzahl) return String(Math.round(wert));
    return String(Number(wert.toPrecision(4)));            // 4 gültige Stellen wie in der Desktop-App
  }

  function schaltungNeu(form, knopf) {
    var block = form.closest("[data-schaltung]");
    var daten = new FormData(form);
    if (knopf && knopf.name) daten.append(knopf.name, knopf.value);   // gedrückter Varianten-Knopf
    var adresse = "/schaltung/" + encodeURIComponent(block.dataset.schaltung) + "/?" +
      new URLSearchParams(daten).toString();
    block.classList.add("laedt");
    fetch(adresse).then(function (antwort) {
      if (!antwort.ok) throw new Error(antwort.status);
      return antwort.text();
    }).then(function (html) {
      var neu = document.createElement("div");
      neu.innerHTML = html.trim();
      var ersatz = neu.firstElementChild;
      var fokus = document.activeElement && document.activeElement.name;
      block.replaceWith(ersatz);
      schaltungVorbereiten(ersatz);
      if (fokus) {                                          // Fokus behalten (Tastatur, Slider)
        var f = ersatz.querySelector('[name="' + CSS.escape(fokus) + '"]');
        if (f) f.focus();
      }
    }).catch(function () {
      block.classList.remove("laedt");
      form.submit();                                        // Notfall: normal neu laden
    });
  }

  function schaltungVorbereiten(block) {
    animationStarten(block);
    var form = block.querySelector("form");
    if (!form) return;
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      schaltungNeu(form, ev.submitter);
    });
    form.addEventListener("change", function (ev) {
      if (ev.target.matches("[data-regler-slider]")) return;   // Slider: eigenes Ereignis unten
      schaltungNeu(form);
    });
    block.querySelectorAll(".regler").forEach(function (regler) {
      var slider = regler.querySelector("[data-regler-slider]");
      var feld = regler.querySelector("[data-regler-feld]");
      var einheit = regler.querySelector("[data-regler-einheit]");
      if (!slider || !feld || !einheit) return;
      var faktoren = JSON.parse(einheit.dataset.faktoren || "{}");
      var log = slider.dataset.log === "1", ganz = slider.dataset.ganzzahl === "1";
      var warte = null;
      slider.addEventListener("input", function () {
        var wert = Number(slider.value);
        if (log) wert = Number(Math.pow(10, wert).toPrecision(3));
        var name = einheit.value || einheit.textContent.trim();
        feld.value = zahlText(wert / (faktoren[name] || 1), ganz);
        clearTimeout(warte);                                 // beim Ziehen nicht jede Bewegung schicken
        warte = setTimeout(function () { schaltungNeu(form); }, 120);
      });
    });
  }
  document.querySelectorAll("[data-schaltung]").forEach(schaltungVorbereiten);

  // ---- 6b) Übungsblatt: drucken, ganzes Thema an-/abwählen ----------------------
  document.addEventListener("click", function (ev) {
    if (ev.target.closest("[data-drucken]")) window.print();
  });
  document.addEventListener("change", function (ev) {
    if (!ev.target.matches("[data-alle]")) return;
    var gruppe = ev.target.closest("[data-gruppe]");
    gruppe.querySelectorAll('input[name="art"]').forEach(function (k) { k.checked = ev.target.checked; });
  });

  // ---- 7) Animationen abspielen (Trafo) ------------------------------------------
  //   <div class="plan" data-animation data-ms="50"> enthält SVGs mit vielen <g class="bild">;
  //   gezeigt wird immer genau eines, alle data-ms Millisekunden das nächste (hell und dunkel im Gleichschritt).
  //   Nach dem letzten Bild geht es bei data-schleife-ab weiter: Die Bilder davor laufen nur einmal
  //   (Trafo DC: das Umschalten), danach wiederholt sich nur der Ruhezustand.
  //   Wer "Bewegung reduzieren" eingestellt hat, sieht zuerst ein stehendes Bild (Knopf "Abspielen").
  function animationStarten(block) {
    var plan = block.querySelector("[data-animation]");
    if (!plan) return;
    var ruhig = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var gruppen = Array.prototype.map.call(plan.querySelectorAll("svg"), function (svg) {
      return svg.querySelectorAll("g.bild");
    });
    var anzahl = gruppen.length ? gruppen[0].length : 0;
    var ms = Number(plan.dataset.ms) || 50;
    var schleifeAb = Number(plan.dataset.schleifeAb) || 0;    // Bilder davor laufen nur EINMAL (z.B. Umschalten)
    var knopf = block.querySelector("[data-animation-knopf]");
    var nochmal = block.querySelector("[data-animation-nochmal]");
    var nummer = 0, laeuft = !ruhig, letzte = 0;
    function zeigen(neu) {
      gruppen.forEach(function (bilder) {
        if (bilder[nummer]) bilder[nummer].style.display = "none";
        if (bilder[neu]) bilder[neu].style.display = "";
      });
      nummer = neu;
    }
    function knopfText() {
      if (!knopf) return;
      knopf.textContent = laeuft ? "⏸ Pause" : "▶ Abspielen";
      knopf.setAttribute("aria-pressed", String(!laeuft));
    }
    function schritt(zeit) {
      if (!document.body.contains(plan)) return;          // Block wurde ersetzt -> diese Schleife endet
      if (laeuft && !document.hidden && zeit - letzte >= ms) {
        letzte = zeit;
        zeigen(nummer + 1 < anzahl ? nummer + 1 : schleifeAb);
      }
      requestAnimationFrame(schritt);
    }
    if (knopf) knopf.addEventListener("click", function () { laeuft = !laeuft; knopfText(); });
    if (nochmal) nochmal.addEventListener("click", function () { zeigen(0); laeuft = true; knopfText(); });
    knopfText();
    if (anzahl > 1) requestAnimationFrame(schritt);
  }

  // ---- 6) Filterfeld (Rechner-Übersicht) --------------------------------------
  //   <input data-filter="#liste">  Einträge mit data-filter-text; Gruppen mit data-filter-gruppe
  //   verschwinden, wenn nichts darin passt. Alle Wörter müssen vorkommen (Gross/klein egal).
  document.querySelectorAll("[data-filter]").forEach(function (feld) {
    var liste = document.querySelector(feld.dataset.filter);
    var leer = document.querySelector("[data-filter-leer]");
    if (!liste) return;
    feld.addEventListener("input", function () {
      var woerter = feld.value.toLowerCase().split(/\s+/).filter(Boolean);
      var treffer = 0;
      liste.querySelectorAll("[data-filter-text]").forEach(function (e) {
        var text = e.dataset.filterText.toLowerCase();
        var passt = woerter.every(function (w) { return text.indexOf(w) >= 0; });
        e.hidden = !passt;
        if (passt) treffer++;
      });
      liste.querySelectorAll("[data-filter-gruppe]").forEach(function (g) {
        g.hidden = !g.querySelector("[data-filter-text]:not([hidden])");
      });
      if (leer) leer.hidden = treffer > 0;
    });
  });

  // ---- 5) Formulare, die sich selbst abschicken -------------------------------
  document.querySelectorAll("form[data-sofort]").forEach(function (form) {
    form.addEventListener("change", function () { form.requestSubmit ? form.requestSubmit() : form.submit(); });
  });
})();
