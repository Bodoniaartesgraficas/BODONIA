"""Fotos interiores de los catálogos: unas con un doble de páginas, otras con dos y una por libro con tres.

Cada foto es un fondo 3:4 (o amarillo liso si aún no hay fondo: None) con uno, dos o tres dobles de páginas apilados;
con tres se reducen para que quepan. Ninguna página se repite entre las fotos ni con el vídeo del libro. Un doble es un mockup sobre negro
(web/referencias-mockups/<carpeta>/N.jpg) o un par de páginas del PDF de interior (página izquierda N).
Uso: python3 web/scripts/montaje.py <santa-fe|primitivismo|tortajada|en-noir|coin>
"""
import sys, tempfile
from pathlib import Path
import numpy as np
from PIL import Image
import santa_fe_fondos as sf
import dobles_pdf

UP = Path("/mnt/user-data/uploads/hearth")
REF = Path(__file__).resolve().parents[1] / "referencias-mockups"
PDF_SF = "/mnt/project-files/Santa Fe_Mauthausen_Santa Fe ALTA.pdf"
PDF_AF = "/mnt/project-files/catálogo ARTE AFRICANO  24nov.pdf"
PDF_NOIR = "/mnt/user-data/uploads/hearth/71cd65f2-e535-42be-a1e9-27d99062cd95/71cd65f2-e535-42be-a1e9-27d99062cd95.pdf"
PDF_COIN = "/mnt/project-files/CRÓNICAS DE LA IGLESIA DE SANTA MARÍA DE COÍN ALTA copia.pdf"
PDF_TERR = "/mnt/project-files/Territorios de la mirada.pdf"

def f(uid): return next((UP / uid).glob("*.jp*g"))

CATALOGOS = {
    "santa-fe": ("03-santa-fe-mauthausen", "santa-fe-dobles", PDF_SF, [
        ("e0193c2e-0462-40e0-bb97-3fc43623ec49", ["m1", "m2"]),
        ("16486969-8684-40a8-a6b4-abcaaf781270", ["m3"]),
        ("61af4831-1489-4214-9d6d-b71583ff5b5f", ["m4", 25]),
        ("ead9bdce-0851-49f4-a38b-0e86c885cadf", [43]),
        ("12d77379-3de9-45b3-b817-49b3f76c5b76", [51, 61]),
        ("cb8ae9ba-65cb-40a8-a8b2-025c20cf8909", [31]),
        ("2745314f-c177-430d-92cd-5fa27bd27d66", [47, 39]),
        ("bb219595-2f42-429c-b41c-4c43874740aa", [13, 55, 59]),
    ]),
    "primitivismo": ("04-primitivismo-y-modernidad", "primitivismo-dobles", PDF_AF, [
        ("18c1e109-4d5f-4784-a830-1dc26dded669", ["m1", "m3"]),
        ("fe949059-04b5-43a7-861d-51cc584036bd", ["m2"]),
        ("aeb6fbea-72d8-4836-bc6b-67b3330e326e", ["m4", 60]),
        ("0a7aca49-6dab-465a-b971-1c54e98fc84f", [66]),
        ("e98dba43-383a-495d-9982-79d7d557a24e", [76, 118]),
        ("8a83a32c-recorte", [142]),
        ("1bd9fe0e-2f21-4f0a-8c56-3d9839cb18df", [216, 220]),
        ("f7e275a1-573f-4df3-9afc-f279a6346b8f", [50, 70, 158]),
    ]),
    # las fotos 1 a 3 salen de otro montaje; aquí se añaden desde la 4 (None = amarillo liso, sin fondo todavía)
    "tortajada": ("01-la-tortajada", "la-tortajada-dobles", None, [
        ("5e750332-124f-4079-a8be-7d5a2a962622", ["m1", "m2"]),
        ("a3a68449-3456-46bf-8aec-f2d9c589f4ec", ["m3"]),
        ("4fe16a7f-f3c3-4856-a9c0-c9c7849fd4cc", ["m7", "m5", "m6"]),
    ], 4),
    # En noir: las fotos 1 a 4 salen de en_noir_fondos.py; aquí se añaden desde la 5
    "en-noir": ("05-pedro-zamora-en-noir", "en-noir-dobles", PDF_NOIR, [
        ("aa991160-266a-46ab-b386-7ff18371c72e", [24]),
        ("d6acb69c-216f-47a8-9ab2-457b8543f74c", [30, 46]),
        ("5b99c650-recorte", [88]),
        ("e31b720e-0e4a-412c-b0cd-057bf5720833", [14, 36, 68]),
    ], 5),
    # Territorios: las fotos 1 y 2 salen de territorios_fondos.py (dobles 2 y 50); aquí se añaden desde la 3
    "territorios": ("02-territorios-de-la-mirada", "territorios-dobles", PDF_TERR, [
        ("76250e24-32cd-445e-9751-1a20f2b95838", [48]),
        ("1da734c8-982f-4129-a3b8-97714eb70063", [36, 98]),
        ("1c3410b7-b484-45f0-b9f2-1c1f753b1bc9", [82]),
        ("38f79aa5-3575-4fd9-9ea7-484398bd1f5e", [26, 112]),
        ("7a7cc6b6-900f-497d-825e-ee24d741e91b", [74, 124]),
    ], 3),
    # mezcladas: las del PDF entre los mockups, alternando suelta y doble
    "coin": ("06-santa-maria-de-coin", "santa-maria-coin-dobles", PDF_COIN, [
        ("23d9fb77-4e7c-4720-8d7b-062e5e25e1ee", [93]),
        ("1172d16d-e742-4f7e-9581-373da77dc44a", ["m2", "m3"]),
        ("9179e760-a2fa-47d0-b6f0-0f5ae283ab5e", [111]),
        ("8bbeb95b-303d-4154-a944-ff73c45d4b3a", [53, 129]),
        ("997ff50b-a9af-4475-8f22-6175f6e769e1", ["m1"]),
        ("9b9a6fed-841c-4da0-90d0-0737371dce5f", [67, 103]),
        ("00b5d91c-b5b1-4e04-a55e-8d452ca626d9", ["m4"]),
        ("bdcbab72-150f-419a-853e-6d001e2f60b2", [57, 143]),
        ("6a172977-db44-4ab5-90cd-4bb5c4c1cb15", [89, 107, 135]),
    ]),
}
QUITA_ABAJO = {"61af4831-1489-4214-9d6d-b71583ff5b5f": .07}  # marca de agua

def mockup(carpeta, n):
    im = Image.open(REF / carpeta / f"{n}.jpg").convert("RGB")
    ys, xs = np.where(np.asarray(im).max(axis=2) > 28)
    return im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))

def main(nombre):
    pref, carpeta, pdf, fotos, *inicio = CATALOGOS[nombre]
    with tempfile.TemporaryDirectory() as tmp:
        for i, (fondo, piezas) in enumerate(fotos, inicio[0] if inicio else 1):
            ims = [mockup(carpeta, p[1:]) if isinstance(p, str) else dobles_pdf.doble(pdf, p, tmp) for p in piezas]
            # sin fondo todavía: amarillo liso, para ver cuáles faltan
            b = sf.fondo(f(fondo), QUITA_ABAJO.get(fondo, 0)) if fondo else Image.new("RGB", (sf.W, sf.H), (246, 214, 64))
            sep = 110 if len(ims) < 3 else 80
            ancho = sf.ANCHO
            hs = [p.height * sf.W * ancho / p.width for p in ims]
            libre = sf.H - 2 * 150 - sep * (len(hs) - 1)   # tres dobles no caben a tamaño normal: se reducen
            if sum(hs) > libre:
                ancho *= libre / sum(hs); hs = [h * libre / sum(hs) for h in hs]
            y = sf.H / 2 - (sum(hs) + sep * (len(hs) - 1)) / 2
            for p, h in zip(ims, hs):
                sf.pon(b, p, y + h / 2, ancho); y += h + sep
            b.save(sf.SITIO / f"{pref}-interior-{i}.jpg", quality=86, optimize=True, progressive=True)
    print(nombre, len(fotos), "fotos")

if __name__ == "__main__":
    main(sys.argv[1])
