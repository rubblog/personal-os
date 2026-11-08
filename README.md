# PERSONAL OS — PROYECTO COMPLETADO Y GUÍA DE USO

**Personal OS** está completamente configurado, probado y listo para funcionar.

---

## 1. Verificación Exitosa de la Prueba Integral

El pipeline se ha ejecutado de extremo a extremo con datos reales y reglas de negocio:

* **Meteorología real (Open-Meteo para El Osito):** Detectó temperatura matinal de 11°C y máxima de 20°C $\rightarrow$ redactó el consejo práctico exacto: *«Ahora hace fresco (11°C); lleva chaqueta para sacar a los perros, pero subirá hasta los 20°C, así que no te abrigues en exceso el resto del día»*.
* **Tráfico hacia la Base Militar:** *«El trayecto hacia la base militar está fluido, unos 15 minutos habituales»*.
* **Agenda:** Incluyó la cita médica en La Fe a las 16:00 y la entrega del trabajo universitario.
* **Radar Oficial y Empleo:** Avisó que no hay novedades en DOGV/BOE para tus especialidades, pero identificó dos vacantes relevantes en empleo: *Profesor FP Procesos Sanitarios (Mas Camarena, 12h)* y *Docente FP Sanitaria Online (15h)*.
* **Síntesis de Voz Neuronal:** Archivo de audio generado con éxito en [`static/audio/daily_briefing.mp3`](file:///c:/Users/rubbl/Desktop/Proyectos%20Antigravity/Planificador%20Personalizado/static/audio/daily_briefing.mp3) (voz española de alta fidelidad, nítida y fluida).

---

## 2. Cómo Iniciar y Utilizar la Aplicación

### En tu ordenador:
Para arrancar el servidor en local:
```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
* Abre tu navegador en: [http://localhost:8000](http://localhost:8000)

### En tu móvil Android (PWA instalable):
1. Asegúrate de que tu móvil esté conectado a la misma red WiFi que tu ordenador (o cuando esté desplegado en la nube).
2. Entra desde Google Chrome a la IP de tu equipo (ej. `http://192.168.1.XX:8000`).
3. Pulsa en el menú de Chrome de tres puntos y selecciona **«Añadir a pantalla de inicio»** o **«Instalar aplicación»**.
4. Se creará el icono de **Personal OS** en tu escritorio de Android y funcionará a pantalla completa como una app nativa.
5. Puedes pulsar **Play** para escuchar el audio de menos de 2 minutos, saltar con los botones de $\pm 10\text{s}$, leer la transcripción o pulsar los enlaces directos a las ofertas.

---

## 3. Despliegue en la Nube (24/7 sin encender el PC)

Para que el servidor trabaje mientras duermes y a las 07:00 AM todo esté listo:
* El proyecto cuenta con un [`Dockerfile`](file:///c:/Users/rubbl/Desktop/Proyectos%20Antigravity/Planificador%20Personalizado/Dockerfile) listo para desplegar en servicios gratuitos o de coste mínimo (como Render, Fly.io, Railway o VPS propio).
* A las 06:15 AM de lunes a viernes, el `APScheduler` interno despierta el pipeline, consulta el tiempo, el tráfico, la agenda y los boletines, y genera el archivo de audio.
