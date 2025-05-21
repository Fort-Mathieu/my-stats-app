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

data["isAccountActivated"] = {
    True: data["isAccountActivated"]["true"],
    False: data["isAccountActivated"]["false"]
}

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

    ax1 = fig1.add_axes([0.2, 0.25, 0.6, 0.6])  # graphique centré verticalement
    labels = [f"{k} ({v})" for k, v in data["source"].items()]
    values = list(data["source"].values())
    ax1.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
    fig1.tight_layout(pad=3)
    pdf.savefig(fig1)
    plt.close(fig1)

    # --- Page 3 : Comptes activés ---
    fig2 = plt.figure(figsize=(a4_width, a4_height))
    add_graph_title(fig2, "Comptes activés vs non activés")

    ax2 = fig2.add_axes([0.2, 0.25, 0.6, 0.6])
    labels = ['Activés', 'Non activés']
    sizes = [data["isAccountActivated"][True], data["isAccountActivated"][False]]
    bars = ax2.bar(labels, sizes, color=['green', 'red'])

    ax2.set_ylabel("Nombre de comptes")
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width() / 2, height + 3, str(height), ha='center')

    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    fig2.tight_layout(pad=3)
    pdf.savefig(fig2)
    plt.close(fig2)

    # --- Page 4 : Activations par date ---
    fig3 = plt.figure(figsize=(a4_width, a4_height))
    add_graph_title(fig3, "Activations dans le temps")

    ax3 = fig3.add_axes([0.15, 0.25, 0.7, 0.6])
    dates = [datetime.strptime(k, "%Y-%m-%d") for k in data["activationDate"].keys()]
    counts = list(data["activationDate"].values())
    ax3.plot(dates, counts, marker='o', linestyle='-', color='blue')

    ax3.set_xticks(dates)
    ax3.set_xticklabels([d.strftime('%Y-%m-%d') for d in dates], rotation=45)
    ax3.grid(True)

    ax3.set_xlabel("Date")
    ax3.set_ylabel("Nombre d'activations")
    ax3.yaxis.set_label_coords(-0.1, 1.02)
    ax3.xaxis.set_label_coords(1.02, -0.12)

    y_max = max(counts)
    ax3.set_ylim(0, y_max * 1.3)

    for x, y in zip(dates, counts):
        ax3.text(x, y + y_max * 0.05, str(y), ha='center', va='bottom', fontsize=9)

    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    fig3.tight_layout(pad=3)
    pdf.savefig(fig3)
    plt.close(fig3)

print(f"✅ PDF généré : {pdf_filename}")
