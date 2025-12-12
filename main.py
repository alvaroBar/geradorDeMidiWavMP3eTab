from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors

# ----------------------------------------------
# CONFIGURAÇÃO INICIAL
# ----------------------------------------------

pdf_path = "C:/Users/alvaro_barbosa/Documents/Musicas/musicas_para_violao_infantil_v2.pdf"
doc = SimpleDocTemplate(pdf_path, pagesize=letter)
styles = getSampleStyleSheet()
story = []

# Estilo para tablaturas (fonte monoespaçada)
tab_style = ParagraphStyle(
    'Tablatura',
    parent=styles['Code'],
    fontName='Courier',
    fontSize=9,
    leading=10,
    spaceAfter=5
)

# Título
header = """
<h1>Músicas Infantis para Violão (Melodia em 1 Corda)</h1>
<p>Lista completa com tablaturas, links e QR Codes para o YouTube.</p>
<br/><br/>
"""
story.append(Paragraph(header, styles["Title"]))

# ----------------------------------------------
# LISTA DE MÚSICAS
# ----------------------------------------------

songs = [
    ("Sapo Cururu",
     """e| -  -  -  0  -  -  -  -  0  -  0  0  -  0  1  -  -  -  -  -  -  -  - |
B| -  -  -  -  1  -  -  -  -  1  -  -  3  -  -  3  -  -  -  -  -  -  1 |
G| 0  2  0  -  -  0  2  0  -  -  -  -  -  -  -  -  3  0  3  3  2  3  - |""",
     "https://www.youtube.com/watch?v=vrkDOY5skTw"),

    ("Marcha Soldado",
     """E|--0--0--0--2--4--4--2--|
E|--4--4--2--4--2--0-----|""",
     "https://www.youtube.com/watch?v=Rmga0jzoSEo"),

    ("Brilha Brilha Estrelinha",
     """E|--0--0--7--7--9--9--7--
E|--5--5--4--4--2--2--0--
E|--7--7--5--5--4--4--2--
E|--7--7--5--5--4--4--2--
E|--0--0--7--7--9--9--7--
E|--5--5--4--4--2--2--0--""",
     "https://www.youtube.com/watch?v=XsTJPaNw2xE"),

    ("Parabéns Pra Você",
     """E|--0--0--2--0--5--4--
E|--0--0--2--0--7--5--
E|--0--0--12-9--5--4--
E|--10-10-9--5--7--5--""",
     "https://www.youtube.com/watch?v=cBcUm_mXVf0"),

    ("Atirei o Pau no Gato",
     """E|--0--0--0--2--4--4--4--2--0--
E|--4--4--4--5--7--7--5--4--2--
E|--4--4--4--5--7--7--5--4--2--0--""",
     "https://www.youtube.com/watch?v=RosdqBHm9ic"),

    ("Ciranda Cirandinha",
     """E|--0--2--4--5--4--2--4--5--
E|--0--2--4--5--4--2--0-----""",
     "https://www.youtube.com/watch?v=fe1rzigZQSk"),

    ("O Cravo Brigou com a Rosa",
     """E|--0--0--2--4--2--0--2--
E|--4--4--5--7--5--4--2--
E|--0--0--2--4--2--0-----""",
     "https://www.youtube.com/watch?v=GcIJfTCDbgM"),

    ("Cai Cai Balão",
     """E|--0--2--4--5--4--2--0--
E|--4--4--2--2--0--------""",
     "https://www.youtube.com/watch?v=FtKBboHCHNo"),

    ("Se Essa Rua Fosse Minha",
     """B|--0--2--3--2--0--3--2--
B|--0--2--3--2--0--------""",
     "https://www.youtube.com/watch?v=Lxc8tBjJ-6Y"),

    ("A Dona Aranha",
     """E|--0--0--0--2--4--4--2--0--
E|--4--4--4--5--7--7--5--4--
E|--0--0--0--2--4--4--2--0--""",
     "https://www.youtube.com/watch?v=wVpbXN-apac"),

    ("Baby Shark",
     """E|--0--0--0--2--4--4--4--2--0--
E|--4--4--4--5--7--7--7--5--4--""",
     "https://www.youtube.com/watch?v=9nG5m1K5zm8"),

    ("Let It Go – Frozen",
     """E|--7--7--7--9--7--5--4--
E|--4--5--7--5--4--2-----""",
     "https://www.youtube.com/watch?v=v5KHLPTEl_A"),

    ("Do You Want to Build a Snowman",
     """E|--0--2--4--5--4--2--0--
E|--0--0--2--4--2--0-----""",
     "https://www.youtube.com/watch?v=wiPhM7dplAY"),

    ("Aquarela – Toquinho",
     """E|--4--4--5--7--7--5--4--2--
E|--2--2--4--5--5--4--2--0--""",
     "https://www.youtube.com/watch?v=3g29f3kt_QE"),

    ("Un Poco Loco – Coco",
     """E|--0--2--4--5--4--2--0--
E|--5--5--4--4--2--2--0--""",
     "https://www.youtube.com/watch?v=IFDDCgiNaoc"),

    ("Remexe – Mundo Bita",
     """E|--0--2--4--4--2--0--
E|--4--5--7--7--5--4--""",
     "https://www.youtube.com/watch?v=_O1hM-k3a7U"),

    ("Fazendinha – Mundo Bita",
     """E|--4--4--5--7--7--5--4--2--
E|--0--2--4--5--4--2--0-----""",
     "https://www.youtube.com/watch?v=tE5IHj2jIMI"),

       
]

# ----------------------------------------------
# FUNÇÃO PARA CRIAR QR CODE ESCALADO
# ----------------------------------------------

def create_qrcode_drawing(url, size_cm):
    qr_code = qr.QrCodeWidget(url)
    qr_code.barWidth = 1
    qr_code.barHeight = 1

    bounds = qr_code.getBounds()
    qr_matrix_size = bounds[2]

    desired_size_pts = size_cm
    new_bar_size = desired_size_pts / qr_matrix_size

    qr_code.barWidth = new_bar_size
    qr_code.barHeight = new_bar_size

    d = Drawing(desired_size_pts, desired_size_pts)
    d.add(qr_code)

    return d

# ----------------------------------------------
# GERAR MÚSICAS
# ----------------------------------------------

for title, tab, link in songs:

    # QR Code
    qr_drawing = create_qrcode_drawing(link, 3.0 * cm)

    # Tablatura formatada
    tab_html = tab.replace("\n", "<br/>")
    tab_paragraph = Paragraph(tab_html, tab_style)

    link_paragraph = Paragraph(
        f"<a href='{link}' color='blue'><u>Link YouTube</u></a>",
        styles["Normal"]
    )

    col_left = [tab_paragraph, Spacer(1, 0.2 * cm), link_paragraph]

    data = [[col_left, qr_drawing]]

    table = Table(data, colWidths=[12 * cm, 3.5 * cm])
    table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
    ]))

    # 🔥 BLOCO COMPLETO (SEM QUEBRA)
    music_block = [
        Paragraph(f"<b>{title}</b>", styles["Heading2"]),
        table,
        Paragraph("<hr width='100%' color='#e0e0e0'/>", styles["Normal"]),
        Spacer(1, 0.5 * cm)
    ]

    story.append(KeepTogether(music_block))

# ----------------------------------------------
# GERAR PDF
# ----------------------------------------------

doc.build(story)

print(f"PDF gerado com sucesso em: {pdf_path}")
