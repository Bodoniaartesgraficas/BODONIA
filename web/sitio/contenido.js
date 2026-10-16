/*
  TEXTOS E IMÁGENES DE LA WEB DE BODONIA
  ======================================
  Aquí se cambia todo lo que se lee y se ve en la web, sin tocar el diseño.

  Reglas para no romper nada:
  - Cambia solo lo que está entre comillas "así".
  - Si un texto lleva comillas dentro, usa las tipográficas: «así» o “así”.
  - Deja la coma del final de cada línea.
  - Para un salto de línea dentro de un texto, escribe \n
  - Las fotos van en la carpeta fotos/proyectos/. Escribe aquí su nombre exacto.
*/

window.CONTENIDO = {

  // Pestaña del navegador y resultados de Google
  pagina: {
    titulo: "Bodonia Artes Gráficas · Imprenta en La Zubia, Granada",
    lema: "Diseño · Maquetación · Impresión",
  },

  // Franja final de la página, debajo de las fotos
  pie: {
    titulo: "Somos imprenta.",
    subtitulo: "Diseñamos, maquetamos e imprimimos.",
    texto: "Más de 35 años en La Zubia, Granada, llevando cada trabajo del archivo al papel: diseño, maquetación e impresión en offset y digital, en el mismo taller.",
    palabras: ["Diseño", "Maquetación", "Impresión"],
  },

  // Botones de arriba a la derecha
  menu: {
    taller: "El taller",
    servicios: "Qué hacemos",
    contacto: "Hablemos",
  },

  // Ventana «El taller»
  taller: {
    antetitulo: "Imprenta en Granada desde hace más de 35 años",
    titulo: "Tú traes la idea.",
    subtitulo: "Nosotros, más de 35 años de imprenta.",
    texto: "Bodonia Artes Gráficas es un taller de Granada al que se puede venir con un archivo terminado o con solo una intención. Te ayudamos a elegir formato, papel y acabado, lo diseñamos y maquetamos, y lo imprimimos en offset o en digital según lo que pida el trabajo.",
    frase: "Lo que entregamos es lo que nos gustaría recibir.",
    enlace: "Contacta con el taller",
  },

  // Ventana «Qué hacemos»: un producto por línea: { nombre }
  servicios: {
    antetitulo: "Diseño · Maquetación · Impresión",
    titulo: "Todo lo que",
    subtitulo: "diseñamos e imprimimos.",
    lista: [
      { nombre: "Libros" },
      { nombre: "Catálogos" },
      { nombre: "Revistas" },
      { nombre: "Facsímiles" },
      { nombre: "Desplegables" },
      { nombre: "Cartelería" },
      { nombre: "Mupis" },
      { nombre: "Folletos" },
      { nombre: "Trípticos" },
      { nombre: "Tarjetas" },
      { nombre: "Postales" },
      { nombre: "Papelería" },
      { nombre: "Diseño gráfico" },
      { nombre: "Diseño editorial" },
      { nombre: "Maquetación" },
    ],
    pie: "Y lo que se te ocurra.",
  },

  // Ventana «Hablemos»
  contacto: {
    antetitulo: "Te ayudamos a diseñarlo, maquetarlo e imprimirlo",
    titulo: "Hablemos de tu proyecto.",
    correo: "info@bodonia.es",
    telefono: "648 82 32 50",
    direccion: "C/ Gredos nº 27\n18140 La Zubia, Granada, España",
    horario: "Lunes a viernes, 9:00–20:00\nSábado y domingo, cerrado",
    mapa: "https://www.google.com/maps/search/?api=1&query=37.10948,-3.591575",
    textoMapa: "Ver en el mapa",
  },

  // Formulario de la ventana «Hablemos»
  formulario: {
    nombre: "Nombre",
    correo: "Correo electrónico",
    mensaje: "Mensaje",
    boton: "Enviar",
    nota: "Usaremos tus datos solo para responderte. Más información en la",
    enlaceNota: "política de privacidad",
    enviando: "Enviando…",
    enviado: "Gracias. Hemos recibido tu mensaje y te responderemos lo antes posible.",
    error: "No se ha podido enviar. Escríbenos a info@bodonia.es o llámanos al 648 82 32 50.",
  },

  /*
    TRABAJOS DE LA GALERÍA: dos filas, de arriba abajo, y dentro de cada fila en el orden en que aparecen.
    Para cambiar un trabajo de fila, corta su bloque { ... } y pégalo dentro de la otra fila.
    El titulo de cada fila es el rótulo pequeño que se ve encima.
    Para añadir uno, copia un bloque { ... }, pégalo donde quieras que salga y cambia sus datos.
    Para quitar uno, borra su bloque entero (desde { hasta },).

    titulo    Nombre del trabajo.
    tipo      Libro, Catálogo, Revista, Cartel...
    portada   Foto que se ve en la galería (vertical, proporción 4:5).
    detalle   Foto que aparece al pasar el ratón por encima. Opcional.
    completa  Foto que se abre al pulsar el trabajo. Opcional: si no está, se usa la portada.
    escenas   Lista de fotos que salen en fila al pulsar el trabajo, detrás de la portada. Opcional: si no está, se usan detalle y completa.
    encuadre  Opcional. Qué parte de la portada se ve si no es 4:5: "50% 50%" es el centro;
              el primer número mueve a izquierda/derecha y el segundo arriba/abajo.
  */
  filas: [
    {
      titulo: "Catálogos, libros y revistas",
      velocidad: 20.16, // píxeles por segundo: más bajo = más lento
      proyectos: [
      {
        titulo: "¡Con lo que ha sido! La Tortajada",
        tipo: "Libro",
        portada: "fotos/proyectos/01-la-tortajada-portada.jpg",
        detalle: "fotos/proyectos/01-la-tortajada-detalle.jpg",
        completa: "fotos/proyectos/01-la-tortajada-completa.jpg",
        escenas: ["fotos/proyectos/01-la-tortajada-interior-4.jpg","fotos/proyectos/01-la-tortajada-interior-6.jpg","fotos/proyectos/01-la-tortajada-interior-5.jpg","fotos/proyectos/01-la-tortajada-interior-3.jpg","fotos/proyectos/01-la-tortajada-interior-2.jpg","fotos/proyectos/01-la-tortajada-interior-1.jpg","fotos/proyectos/01-la-tortajada-video.mp4"],
      },
      {
        titulo: "Territorios de la mirada",
        tipo: "Catálogo",
        portada: "fotos/proyectos/02-territorios-de-la-mirada-portada.jpg",
        detalle: "fotos/proyectos/02-territorios-de-la-mirada-detalle.jpg",
        completa: "fotos/proyectos/02-territorios-de-la-mirada-completa.jpg",
        escenas: ["fotos/proyectos/02-territorios-de-la-mirada-interior-1.jpg","fotos/proyectos/02-territorios-de-la-mirada-interior-6.jpg","fotos/proyectos/02-territorios-de-la-mirada-interior-2.jpg","fotos/proyectos/02-territorios-de-la-mirada-interior-4.jpg","fotos/proyectos/02-territorios-de-la-mirada-interior-7.jpg","fotos/proyectos/02-territorios-de-la-mirada-interior-5.jpg","fotos/proyectos/02-territorios-de-la-mirada-interior-3.jpg","fotos/proyectos/02-territorios-de-la-mirada-video.mp4"],
      },
      {
        titulo: "Santa Fe—Mauthausen—Santa Fe",
        tipo: "Libro",
        portada: "fotos/proyectos/03-santa-fe-mauthausen-portada.jpg",
        detalle: "fotos/proyectos/03-santa-fe-mauthausen-detalle.jpg",
        completa: "fotos/proyectos/03-santa-fe-mauthausen-completa.jpg",
        mosaico: "vertical",
        escenas: ["fotos/proyectos/03-santa-fe-mauthausen-interior-1.jpg","fotos/proyectos/03-santa-fe-mauthausen-interior-2.jpg","fotos/proyectos/03-santa-fe-mauthausen-interior-3.jpg","fotos/proyectos/03-santa-fe-mauthausen-interior-8.jpg","fotos/proyectos/03-santa-fe-mauthausen-interior-7.jpg","fotos/proyectos/03-santa-fe-mauthausen-interior-4.jpg","fotos/proyectos/03-santa-fe-mauthausen-interior-5.jpg","fotos/proyectos/03-santa-fe-mauthausen-interior-6.jpg","fotos/proyectos/03-santa-fe-mauthausen-video.mp4"],
      },
      {
        titulo: "Primitivismo y modernidad",
        tipo: "Catálogo",
        portada: "fotos/proyectos/04-primitivismo-y-modernidad-portada.jpg",
        detalle: "fotos/proyectos/04-primitivismo-y-modernidad-detalle.jpg",
        completa: "fotos/proyectos/04-primitivismo-y-modernidad-completa.jpg",
        mosaico: "horizontal",
        escenas: ["fotos/proyectos/04-primitivismo-y-modernidad-interior-5.jpg","fotos/proyectos/04-primitivismo-y-modernidad-interior-1.jpg","fotos/proyectos/04-primitivismo-y-modernidad-interior-4.jpg","fotos/proyectos/04-primitivismo-y-modernidad-interior-7.jpg","fotos/proyectos/04-primitivismo-y-modernidad-interior-2.jpg","fotos/proyectos/04-primitivismo-y-modernidad-interior-3.jpg","fotos/proyectos/04-primitivismo-y-modernidad-interior-6.jpg","fotos/proyectos/04-primitivismo-y-modernidad-video.mp4"],
        encuadre: "50% 65%",
      },
      {
        titulo: "Pedro Zamora. En noir",
        tipo: "Catálogo",
        portada: "fotos/proyectos/05-pedro-zamora-en-noir-portada.jpg",
        detalle: "fotos/proyectos/05-pedro-zamora-en-noir-detalle.jpg",
        completa: "fotos/proyectos/05-pedro-zamora-en-noir-completa.jpg",
        escenas: ["fotos/proyectos/05-pedro-zamora-en-noir-interior-6.jpg","fotos/proyectos/05-pedro-zamora-en-noir-interior-7.jpg","fotos/proyectos/05-pedro-zamora-en-noir-interior-5.jpg","fotos/proyectos/05-pedro-zamora-en-noir-interior-1.jpg","fotos/proyectos/05-pedro-zamora-en-noir-interior-2.jpg","fotos/proyectos/05-pedro-zamora-en-noir-interior-3.jpg","fotos/proyectos/05-pedro-zamora-en-noir-interior-4.jpg","fotos/proyectos/05-pedro-zamora-en-noir-video.mp4"],
      },
      {
        titulo: "Iglesia y Convento de Santa María de Coín",
        tipo: "Libro",
        portada: "fotos/proyectos/06-santa-maria-de-coin-portada.jpg",
        detalle: "fotos/proyectos/06-santa-maria-de-coin-detalle.jpg",
        completa: "fotos/proyectos/06-santa-maria-de-coin-completa.jpg",
        escenas: ["fotos/proyectos/06-santa-maria-de-coin-interior-4.jpg","fotos/proyectos/06-santa-maria-de-coin-interior-6.jpg","fotos/proyectos/06-santa-maria-de-coin-interior-7.jpg","fotos/proyectos/06-santa-maria-de-coin-interior-5.jpg","fotos/proyectos/06-santa-maria-de-coin-interior-9.jpg","fotos/proyectos/06-santa-maria-de-coin-interior-8.jpg","fotos/proyectos/06-santa-maria-de-coin-interior-1.jpg","fotos/proyectos/06-santa-maria-de-coin-interior-3.jpg","fotos/proyectos/06-santa-maria-de-coin-interior-2.jpg","fotos/proyectos/06-santa-maria-de-coin-video.mp4"],
      },
      ],
    },
  ],
};
