/* Dimensione testo e alto contrasto, ricordati nel browser. */
(function () {
  var r = document.documentElement, DIM = [16, 18, 20, 22, 25, 28, 32];
  function leggi(k, d) { try { return localStorage.getItem(k) || d; } catch (e) { return d; } }
  function scrivi(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  var i = Math.min(Math.max(parseInt(leggi("cal_dim", "2"), 10) || 2, 0), DIM.length - 1);
  var alto = leggi("cal_alto", "no") === "si";
  function applica() {
    r.style.setProperty("--fs", DIM[i] + "px");
    if (alto) r.setAttribute("data-contrasto", "alto"); else r.removeAttribute("data-contrasto");
    var b = document.getElementById("contrasto");
    if (b) b.setAttribute("aria-pressed", alto ? "true" : "false");
  }
  applica();
  document.addEventListener("DOMContentLoaded", function () {
    applica();
    document.getElementById("piu").addEventListener("click", function () {
      i = Math.min(i + 1, DIM.length - 1); scrivi("cal_dim", i); applica();
    });
    document.getElementById("meno").addEventListener("click", function () {
      i = Math.max(i - 1, 0); scrivi("cal_dim", i); applica();
    });
    document.getElementById("contrasto").addEventListener("click", function () {
      alto = !alto; scrivi("cal_alto", alto ? "si" : "no"); applica();
    });
  });
})();
