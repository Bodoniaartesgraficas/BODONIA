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
  },

  // Botones de arriba a la derecha
  menu: {
    taller: "El taller",
    servicios: "Qué hacemos",
    contacto: "Hablemos",
  },

  // Ventana «El taller»
  taller: {
    titulo: "Tú traes la idea.\nNosotros, más de 35 años\nde imprenta.",
    texto: "Bodonia Artes Gráficas es un taller de La Zubia al que se puede venir con un archivo terminado o con solo una intención. Te ayudamos a elegir formato, papel y acabado, lo diseñamos y maquetamos, y lo imprimimos en offset o en digital según lo que pida el trabajo.",
    frase: "Lo que entregamos es lo que nos gustaría recibir.",
    enlace: "Contacta con el taller",
  },

  // Ventana «Qué hacemos»: añade o quita bloques { nombre, detalle }
  servicios: {
    titulo: "Todo lo que diseñamos e imprimimos.",
    lista: [
      { nombre: "Damos forma", detalle: "Diseño gráfico, diseño editorial y maquetación." },
      { nombre: "Hacemos libros", detalle: "Libros, catálogos, revistas y facsímiles." },
      { nombre: "Llenamos paredes y manos", detalle: "Cartelería, mupis, folletos, desplegables y trípticos." },
      { nombre: "Y lo de cada día", detalle: "Tarjetas, postales y papelería." },
    ],
    pie: "Y lo que se te ocurra.",
  },

  // Ventana «Hablemos»
  contacto: {
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
    encuadre  Opcional. Qué parte de la portada se ve si no es 4:5: "50% 50%" es el centro;
              el primer número mueve a izquierda/derecha y el segundo arriba/abajo.
  */
  filas: [
    {
      titulo: "Catálogos, libros y revistas",
      proyectos: [
      {
        titulo: "¡Con lo que ha sido! La Tortajada",
        tipo: "Libro",
        portada: "fotos/proyectos/01-la-tortajada-portada.jpg",
        detalle: "fotos/proyectos/01-la-tortajada-detalle.jpg",
        completa: "fotos/proyectos/01-la-tortajada-completa.jpg",
        encuadre: "50% 72%",
      },
      {
        titulo: "Territorios de la mirada",
        tipo: "Catálogo",
        portada: "fotos/proyectos/02-territorios-de-la-mirada-portada.jpg",
        detalle: "fotos/proyectos/02-territorios-de-la-mirada-detalle.jpg",
        completa: "fotos/proyectos/02-territorios-de-la-mirada-completa.jpg",
      },
      {
        titulo: "Santa Fe—Mauthausen—Santa Fe",
        tipo: "Libro",
        portada: "fotos/proyectos/03-santa-fe-mauthausen-portada.jpg",
        detalle: "fotos/proyectos/03-santa-fe-mauthausen-detalle.jpg",
        completa: "fotos/proyectos/03-santa-fe-mauthausen-completa.jpg",
      },
      {
        titulo: "Primitivismo y modernidad",
        tipo: "Catálogo",
        portada: "fotos/proyectos/04-primitivismo-y-modernidad-portada.jpg",
        detalle: "fotos/proyectos/04-primitivismo-y-modernidad-detalle.jpg",
        completa: "fotos/proyectos/04-primitivismo-y-modernidad-completa.jpg",
        encuadre: "50% 65%",
      },
      {
        titulo: "Pedro Zamora. En noir",
        tipo: "Catálogo",
        portada: "fotos/proyectos/05-pedro-zamora-en-noir-portada.jpg",
        detalle: "fotos/proyectos/05-pedro-zamora-en-noir-detalle.jpg",
        completa: "fotos/proyectos/05-pedro-zamora-en-noir-completa.jpg",
      },
      {
        titulo: "Iglesia y Convento de Santa María de Coín",
        tipo: "Libro",
        portada: "fotos/proyectos/06-santa-maria-de-coin-portada.jpg",
        detalle: "fotos/proyectos/06-santa-maria-de-coin-detalle.jpg",
        completa: "fotos/proyectos/06-santa-maria-de-coin-completa.jpg",
      },
      {
        titulo: "Yauco. Esencia y patrimonio cultural",
        tipo: "Libro",
        portada: "fotos/proyectos/07-yauco-portada.jpg",
        detalle: "fotos/proyectos/07-yauco-detalle.jpg",
        completa: "fotos/proyectos/07-yauco-completa.jpg",
      },
      {
        titulo: "RDG. Colegio de Dentistas de Granada",
        tipo: "Revista",
        portada: "fotos/proyectos/08-revista-rdg-portada.jpg",
        detalle: "fotos/proyectos/08-revista-rdg-detalle.jpg",
        completa: "fotos/proyectos/08-revista-rdg-completa.jpg",
      },
      {
        titulo: "Pequeño Oso y la montaña de hielo",
        tipo: "Revista",
        portada: "fotos/proyectos/09-pequeno-oso-portada.jpg",
        detalle: "fotos/proyectos/09-pequeno-oso-detalle.jpg",
        completa: "fotos/proyectos/09-pequeno-oso-completa.jpg",
      },
      ],
    },
    {
      titulo: "Otros trabajos",
      proyectos: [
      {
        titulo: "En torno a Santa Fe",
        tipo: "Díptico",
        portada: "fotos/proyectos/10-diptico-en-torno-a-santa-fe-portada.jpg",
        detalle: "fotos/proyectos/10-diptico-en-torno-a-santa-fe-detalle.jpg",
        completa: "fotos/proyectos/10-diptico-en-torno-a-santa-fe-completa.jpg",
      },
      {
        titulo: "Pedro Zamora",
        tipo: "Díptico",
        portada: "fotos/proyectos/11-diptico-pedro-zamora-portada.jpg",
        detalle: "fotos/proyectos/11-diptico-pedro-zamora-detalle.jpg",
        completa: "fotos/proyectos/11-diptico-pedro-zamora-completa.jpg",
      },
      {
        titulo: "534 aniversario de las Capitulaciones",
        tipo: "Cartel",
        portada: "fotos/proyectos/12-cartel-capitulaciones-portada.jpg",
        detalle: "fotos/proyectos/12-cartel-capitulaciones-detalle.jpg",
        completa: "fotos/proyectos/12-cartel-capitulaciones-completa.jpg",
      },
      {
        titulo: "III Festival de Literatura Histórica",
        tipo: "Cartel",
        portada: "fotos/proyectos/13-cartel-festival-literatura-portada.jpg",
        detalle: "fotos/proyectos/13-cartel-festival-literatura-detalle.jpg",
        completa: "fotos/proyectos/13-cartel-festival-literatura-completa.jpg",
      },
      {
        titulo: "Haiku. Pliegos del Azul",
        tipo: "Pliego",
        portada: "fotos/proyectos/14-haiku-pliegos-del-azul-portada.jpg",
        detalle: "fotos/proyectos/14-haiku-pliegos-del-azul-detalle.jpg",
        completa: "fotos/proyectos/14-haiku-pliegos-del-azul-completa.jpg",
      },
      {
        titulo: "Calendario de sobremesa 2027",
        tipo: "Calendario",
        portada: "fotos/proyectos/15-calendario-2027-portada.jpg",
        detalle: "fotos/proyectos/15-calendario-2027-detalle.jpg",
        completa: "fotos/proyectos/15-calendario-2027-completa.jpg",
      },
      {
        titulo: "Clínica dental be&sa",
        tipo: "Tarjetas",
        portada: "fotos/proyectos/16-tarjetas-besa-portada.jpg",
        detalle: "fotos/proyectos/16-tarjetas-besa-detalle.jpg",
        completa: "fotos/proyectos/16-tarjetas-besa-completa.jpg",
      },
      {
        titulo: "Papelería Bodonia",
        tipo: "Papelería",
        portada: "fotos/proyectos/17-papeleria-bodonia-portada.jpg",
        detalle: "fotos/proyectos/17-papeleria-bodonia-detalle.jpg",
        completa: "fotos/proyectos/17-papeleria-bodonia-completa.jpg",
      },
      ],
    },
  ],
};
