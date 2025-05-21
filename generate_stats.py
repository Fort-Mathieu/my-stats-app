import json
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime
import matplotlib.image as mpimg
import io
import cairosvg
import textwrap
import locale

# Format de date français
locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
today = datetime.now()
today_fr = today.strftime("%-d %B %Y")
today_str = today.strftime("%Y-%m-%d")

# Charger les données
with open("stats.json", "r") as f:
    data = json.load(f)

pdf_filename = f"statistiques_comptes_{today_str}_A4_pages.pdf"

# Dimensions A4
a4_width, a4_height = 8.27, 11.69

def add_graph_title(fig, title):
    fig.text(0.5, 0.95, title, ha='center', va='top', fontsize=18, fontweight='bold')

with PdfPages(pdf_filename) as pdf:
    # --- Page 1 : Couverture ---
    fig_cover = plt.figure(figsize=(a4_width, a4_height))
    plt.axis('off')

    # Titre principal (avec retour à la ligne si besoin)
    title_text = "Statistiques de l'espace client Sorégies"
    wrapper = textwrap.TextWrapper(width=40)
    wrapped_title = "\n".join(wrapper.wrap(title_text))

    plt.text(0.5, 0.65, wrapped_title,
             ha='center', va='center',
             fontsize=36, fontweight='bold',
             wrap=True)

    # Date en dessous du titre, plus petite et grisée
    plt.text(0.5, 0.55, today_fr,
             ha='center', va='center',
             fontsize=20, color='gray')

    # Logo SVG converti en PNG et affiché sous la date
    logo_svg_path = "logo.svg"  # modifie ce chemin si besoin
    try:
        png_data = cairosvg.svg2png(url=logo_svg_path)
        logo_img = mpimg.imread(io.BytesIO(png_data), format='png')

        # Taille du logo réduite de moitié (de 3 à 1.5 pouces)
        logo_size = 1.5

        # Position légèrement plus basse (0.2 au lieu de 0.25) pour ajouter de l’espace
        ax_logo = fig_cover.add_axes([0.5 - logo_size / a4_width / 2, 0.18, logo_size / a4_width, logo_size / a4_width], anchor='C')
        ax_logo.imshow(logo_img)
        ax_logo.axis('off')
    except Exception as e:
        print(f"⚠️ Impossible de charger le logo SVG : {e}")

    pdf.savefig(fig_cover)
    plt.close(fig_cover)

    # --- Page 2 : Répartition par source ---
    fig1 = plt.figure(figsize=(a4_width, a4_height))
    add_graph_title(fig1, "Répartition par source")

    ax1 = fig1.add_axes([0.2, 0.25, 0.6, 0.6])
    labels = [f"{k} ({v})" for k, v in data["source"].items()]
    values = list(data["source"].values())
    ax1.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
    fig1.tight_layout(pad=3)
    pdf.savefig(fig1)
    plt.close(fig1)

    # --- Page 3 : Comptes activés par source ---
    fig2 = plt.figure(figsize=(a4_width, a4_height))
    add_graph_title(fig2, "Comptes activés par source")

    ax2 = fig2.add_axes([0.2, 0.25, 0.6, 0.6])
    sources = list(data["accountActivation"]["bySource"].keys())
    activated = [data["accountActivation"]["bySource"][src]["activated"] for src in sources]
    not_activated = [data["accountActivation"]["bySource"][src]["notActivated"] for src in sources]

    bar_width = 0.35
    x = range(len(sources))
    ax2.bar(x, activated, width=bar_width, label='Activés', color='green')
    ax2.bar([i + bar_width for i in x], not_activated, width=bar_width, label='Non activés', color='red')

    ax2.set_xticks([i + bar_width / 2 for i in x])
    ax2.set_xticklabels(sources)
    ax2.set_ylabel("Nombre de comptes")
    ax2.legend()
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    for i in range(len(sources)):
        ax2.text(i, activated[i] + 1, str(activated[i]), ha='center')
        ax2.text(i + bar_width, not_activated[i] + 1, str(not_activated[i]), ha='center')

    fig2.tight_layout(pad=3)
    pdf.savefig(fig2)
    plt.close(fig2)

    # --- Page 4 : Activations dans le temps par source ---
    fig3 = plt.figure(figsize=(a4_width, a4_height))
    add_graph_title(fig3, "Activations dans le temps par source")

    ax3 = fig3.add_axes([0.15, 0.25, 0.7, 0.6])
    sources = list(data["source"].keys())
    dates = sorted(data["activationDate"].keys())
    date_objs = [datetime.strptime(date, "%Y-%m-%d") for date in dates]

    for source in sources:
        counts = [data["activationDate"].get(date, {}).get(source, 0) for date in dates]
        ax3.plot(date_objs, counts, marker='o', label=source)

    ax3.set_xticks(date_objs)
    ax3.set_xticklabels([d.strftime('%Y-%m-%d') for d in date_objs], rotation=45)
    ax3.set_xlabel("Date")
    ax3.set_ylabel("Nombre d'activations")
    ax3.grid(True)
    ax3.legend()
    fig3.tight_layout(pad=3)
    pdf.savefig(fig3)
    plt.close(fig3)

print(f"✅ PDF généré : {pdf_filename}")
