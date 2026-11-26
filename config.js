// ============================================================
// CONFIGURACIÓN DEL TABLERO — editable a mano (también desde la web de GitHub)
// Este archivo NO lo toca la actualización automática.
// Usá null cuando un dato todavía no está confirmado.
// ============================================================
window.CONFIG = {
  cliente: "RapiCuotas",
  edicion: "2026",

  // Período de campo (formato AAAA-MM-DD)
  fechaInicio: "2026-11-24",
  fechaCierre: "2026-12-11",     // cierre del campo → activa el ritmo diario necesario

  // Dotación (personas invitadas a responder)
  dotacionTotal: 400,
  dotacionConfirmada: false,    // true cuando RapiCuotas confirme el número

  // Dotación por región: completar para ver la tasa de respuesta de cada una.
  // Los nombres tienen que coincidir con las opciones de la encuesta.
  dotacionPorRegion: {
    "La Plata y alrededores": null,
    "Buenos Aires Interior": null,
    "Norte": null,
    "Litoral": null,
    "Cuyo y Centro": null,
    "Sur": null
  },

  // Meta de participación (% sobre la dotación). 53 = igualar la edición anterior.
  metaTasa: 53,

  // Edición anterior, para comparar (informe 2025)
  anterior: {
    nombre: "Edición 2025",
    periodo: "17 dic 2024 – 10 ene 2025",
    respuestas: 165,
    tasa: 53,
    dias: 24
  }
};
