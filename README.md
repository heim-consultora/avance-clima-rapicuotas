# Avance de participación · Encuesta de Clima Laboral RapiCuotas 2026

Tablero público (GitHub Pages) que muestra **solo conteos agregados de participación**: respuestas por día, por región y por antigüedad, tasa de respuesta, meta y comparación con 2025. Nunca publica respuestas individuales.

## Archivos

| Archivo | Qué es | ¿Quién lo toca? |
|---|---|---|
| `index.html` | La página (marca Heim Consultora) | Nadie, salvo cambios de diseño |
| `config.js` | Dotación total y por región, fechas, meta, datos 2025 | **Se edita a mano** (también desde github.com, botón del lápiz) |
| `data.js` | Conteos agregados | Lo genera la actualización automática |
| `scripts/actualizar.py` | Trae respuestas de SurveyMonkey y calcula los conteos | — |
| `.github/workflows/actualizar.yml` | Corre el script cada hora y publica | — |

## Puesta en marcha (una sola vez)

1. **Pages:** Settings → Pages → Source: **GitHub Actions**.
2. **Secretos:** Settings → Secrets and variables → Actions → New repository secret:
   - `SM_TOKEN`: el access token de la app privada de SurveyMonkey (lo genera Sigrid en developer.surveymonkey.com → My Apps → Private app, con los permisos *View Surveys* y *View Response Details*).
   - `SM_SURVEY_ID`: el ID de la encuesta 2026.
3. Actions → “Actualizar y publicar tablero” → **Run workflow** para la primera corrida.

Sin los secretos, la página se publica igual con el último `data.js` cargado a mano.

## Actualización manual (si no hay API)

Con un export CSV de SurveyMonkey **en tu computadora** (nunca lo subas al repo, está en `.gitignore`):

```bash
python scripts/actualizar.py --csv ~/Descargas/Encuesta_Clima_Laboral_2026.csv
git add data.js && git commit -m "Actualiza conteos" && git push
```

## Privacidad

- El repo y la página contienen solo totales. El export y el token nunca se suben.
- Cualquiera con el link puede ver la página (no aparece en buscadores: `noindex`).
- Antes de cruzar variables (por ejemplo región × antigüedad) revisar grupos chicos: la región Sur tiene pocas respuestas.
