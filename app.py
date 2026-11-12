import streamlit as st
import pandas as pd
from datetime import datetime
import altair as alt
import os
import json
import gspread
from gspread.exceptions import WorksheetNotFound
from streamlit_option_menu import option_menu

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Gestionale GGM.EARTH", page_icon="⚙️", layout="wide")

# --- STILE ESTETICO MODERNO (SAAS UI) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {background-color: rgba(244, 247, 251, 0.8); backdrop-filter: blur(8px);}

    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    .stApp { background-color: #f1f5f9; }
    [data-testid="stSidebar"] { 
        background-color: #ffffff; 
        border-right: 1px solid #e2e8f0; 
        box-shadow: 2px 0 12px rgba(15, 23, 42, 0.03);
    }

    h1 { color: #0f172a !important; font-weight: 800 !important; letter-spacing: -0.8px; font-size: 2.1rem !important; margin-bottom: 0.2rem !important; }
    h2, h3 { color: #1e293b !important; font-weight: 700 !important; letter-spacing: -0.3px; }

    /* Card contornate */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff !important;
        border-radius: 16px !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 4px 20px rgba(15, 23, 42, 0.04) !important;
        padding: 18px !important;
    }

    /* KPI Metrics */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 14px;
        padding: 16px 22px;
        border: 1px solid #e2e8f0;
        border-left: 5px solid #2563eb;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03);
        transition: all 0.25s ease;
    }
    [data-testid="stMetric"]:hover { 
        transform: translateY(-3px); 
        box-shadow: 0 10px 25px rgba(37, 99, 235, 0.12); 
    }
    [data-testid="stMetricLabel"] { font-weight: 600 !important; color: #64748b !important; font-size: 0.9rem !important; }
    [data-testid="stMetricValue"] { font-weight: 800 !important; color: #0f172a !important; }

    /* Tabs moderne */
    .stTabs [data-baseweb="tab-list"] { 
        background-color: #ffffff; 
        border-radius: 12px; 
        padding: 6px; 
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03); 
        gap: 6px; 
    }
    .stTabs [data-baseweb="tab"] { 
        border-radius: 8px; 
        padding: 8px 18px; 
        font-weight: 600;
        color: #64748b;
        transition: all 0.2s ease; 
    }
    .stTabs [aria-selected="true"] { 
        background-color: #eff6ff !important; 
        color: #2563eb !important; 
        font-weight: 700; 
    }

    /* Bottoni primari */
    button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); 
        border: none; 
        border-radius: 10px;
        color: white; 
        font-weight: 600; 
        letter-spacing: 0.3px; 
        padding: 10px 24px; 
        transition: all 0.25s ease; 
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.25);
    }
    button[kind="primary"]:hover { 
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4); 
        transform: translateY(-1px); 
    }

    /* Expander e Tabelle */
    [data-testid="stExpander"] { 
        border: 1px solid #e2e8f0 !important; 
        background-color: #ffffff; 
        border-radius: 12px !important; 
        margin-bottom: 8px; 
    }
    [data-testid="stDataFrame"], [data-testid="stDataEditor"] { 
        border-radius: 12px; 
        overflow: hidden; 
        border: 1px solid #cbd5e1; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DI ACCESSO CON PASSWORD (CARD LOGIN) ---
PASSWORD_AZIENDALE = "GGM2026"

if "autenticato" not in st.session_state:
    st.session_state.autenticato = False

if not st.session_state.autenticato:
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col_login, _ = st.columns([1.2, 1.6, 1.2])
    with col_login:
        with st.container(border=True):
            c_logo1, c_logo2, c_logo3 = st.columns([1, 1.2, 1])
            with c_logo2:
                if os.path.exists("logo.png"):
                    st.image("logo.png", use_container_width=True)
                elif os.path.exists("logo.jpg"):
                    st.image("logo.jpg", use_container_width=True)
                else:
                    st.markdown("<div style='text-align:center; font-size:48px;'>⚙️</div>", unsafe_allow_html=True)
            
            st.markdown("<h2 style='text-align:center; margin-top:5px;'>HUB Gestionale GGM</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align:center; color:#64748b; font-size:0.92rem; margin-bottom:20px;'>Area riservata al personale autorizzato. Inserisci le credenziali di accesso.</p>", unsafe_allow_html=True)
            
            pwd = st.text_input("Password aziendale:", type="password", placeholder="••••••••")
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
            if st.button("Accedi al Gestionale", type="primary", use_container_width=True):
                if pwd == PASSWORD_AZIENDALE:
                    st.session_state.autenticato = True
                    st.rerun()
                else:
                    st.error("❌ Password non valida. Verifica e riprova.")
    st.stop()

# --- DA QUI IN POI IL CODICE VIENE ESEGUITO SOLO SE AUTENTICATI ---

NOME_DATABASE = "Database_GGM"

# --- RUBRICA FORNITORI E LABORATORI ---
RUBRICA_FORNITORI = {
    "Agreto": {"tel": "+43 7248 64484", "email": "office@agreto.com"},
    "Ambrogeo": {"tel": "0522 331180", "email": "info@ambrogeo.it"},
    "Autel Robotics": {"tel": "Assistenza Ufficiale", "email": "support@autelrobotics.com"},
    "Codevintec (MALÅ)": {"tel": "02 4830 2175", "email": "info@codevintec.it"},
    "E-Survey": {"tel": "Assistenza Partner IT", "email": "support@esurvey-gnss.com"},
    "EMFAD": {"tel": "+49 2241 846460", "email": "info@emfad.de"},
    "Emlid": {"tel": "Supporto Ufficiale", "email": "support@emlid.com"},
    "Faro": {"tel": "02 9394 541", "email": "italia@faro.com"},
    "Geomax": {"tel": "071 213251", "email": "info@geomax-positioning.it"},
    "Geophex": {"tel": "+1 919 839 8515", "email": "geophex@geophex.com"},
    "Geosystem S.r.l.": {"tel": "06 1234567", "email": "assistenza@geosystem.it"},
    "IDS GeoRadar": {"tel": "050 8934100", "email": "support.georadar@idsgeoradar.com"},
    "MAE Civile & Geofisica": {"tel": "0425 474477", "email": "info@mae-srl.it"},
    "PASI Geophysics": {"tel": "011 965 4700", "email": "info@pasigeophysics.com"},
    "Sensys": {"tel": "+49 33631 59650", "email": "info@sensys.de"}
}

# --- CONNESSIONE GOOGLE SHEETS (CLOUD + LOCALE) ---
@st.cache_resource
def connetti_gsheets():
    if "google_oauth" in st.secrets:
        with open("client_secrets.json", "w") as f:
            f.write(st.secrets["google_oauth"]["credentials"])
        with open("token.json", "w") as f:
            f.write(st.secrets["google_oauth"]["token"])
    elif "gcp_service_account" in st.secrets:
        return gspread.service_account_from_dict(st.secrets["gcp_service_account"])
        
    return gspread.oauth(
        credentials_filename="client_secrets.json",
        authorized_user_filename="token.json"
    )

gc = connetti_gsheets()

# --- FUNZIONI DI CARICAMENTO DATI DA SHEETS ---
@st.cache_data(show_spinner=False)
def carica_foglio(nome_foglio):
    try:
        sh = gc.open(NOME_DATABASE)
        worksheet = sh.worksheet(nome_foglio)
        dati = worksheet.get_all_records()
        return pd.DataFrame(dati) if dati else pd.DataFrame()
    except WorksheetNotFound:
        return pd.DataFrame()

def carica_dati_strumenti():
    df = carica_foglio("Registro_Strumenti_ISO")
    if df.empty or "Strumento / Modello" not in df.columns:
        return pd.DataFrame(columns=["Categoria", "Marca", "Strumento / Modello", "Seriale / ID", "Stato Funzionamento", "Note Malfunzionamento", "Tipo di Controllo", "Frequenza (Mesi)", "Ultima Data", "Scadenza", "Stato Attuale", "Link Certificato"])
    return df.dropna(subset=["Strumento / Modello"])

def carica_dati_flotta():
    df = carica_foglio("Flotta Automezzi")
    if df.empty or "Targa" not in df.columns:
        return pd.DataFrame(columns=["Targa", "Veicolo", "Assegnatario", "Scadenza Assicurazione", "Scadenza Revisione", "Scadenza Bollo", "Stato Mezzo", "Note"])
    return df.dropna(subset=["Targa"])

def carica_dati_personale():
    df = carica_foglio("Personale e Sicurezza")
    if df.empty or "Cognome" not in df.columns:
        return pd.DataFrame(columns=["Cognome", "Nome", "Ruolo", "Scadenza Visita Medica", "Note"])
    return df.dropna(subset=["Cognome"])

def carica_dati_attestati():
    df = carica_foglio("Attestati")
    if df.empty or "Nome Corso" not in df.columns:
        return pd.DataFrame(columns=["ID_Dipendente", "Nome Corso", "Data Rilascio", "Validità (Anni)", "Note"])
    return df.dropna(subset=["Nome Corso"])

# --- FUNZIONE SALVATAGGIO SICURO SU SHEETS ---
def salva_su_excel(df_da_salvare, nome_foglio):
    mappa_fogli = {
        "Registro Strumenti": "Registro_Strumenti_ISO",
        "Registro_Strumenti_ISO": "Registro_Strumenti_ISO",
        "Flotta Automezzi": "Flotta Automezzi",
        "Personale": "Personale e Sicurezza",
        "Personale e Sicurezza": "Personale e Sicurezza",
        "Attestati": "Attestati"
    }
    nome_reale = mappa_fogli.get(nome_foglio, nome_foglio)
    
    try:
        sh = gc.open(NOME_DATABASE)
        try:
            worksheet = sh.worksheet(nome_reale)
        except WorksheetNotFound:
            worksheet = sh.add_worksheet(title=nome_reale, rows="1000", cols="26")
        
        df_export = df_da_salvare.copy()
        
        for col in df_export.columns:
            if pd.api.types.is_datetime64_any_dtype(df_export[col]):
                df_export[col] = df_export[col].dt.strftime('%d/%m/%Y')
        
        df_export = df_export.fillna("")
        df_export = df_export.astype(str)
        df_export = df_export.replace(['nan', 'NaN', 'NaT', 'None', '<NA>'], '')

        worksheet.clear()
        worksheet.update([df_export.columns.values.tolist()] + df_export.values.tolist())
        return True
    except Exception as e:
        st.error(f"Errore di salvataggio su Google Sheets: {e}")
        return False

# --- FUNZIONE SUPPORTO UNIONE DATI ---
def unisci_e_salva_dati(df_originale, df_modificato):
    df_completo = df_originale.copy()
    
    for col in df_modificato.columns:
        if col not in df_completo.columns:
            df_completo[col] = ""

    esistenti = df_modificato[df_modificato.index.isin(df_completo.index)]
    nuove_righe = df_modificato[~df_modificato.index.isin(df_completo.index)]
    
    for col in esistenti.columns:
        df_completo[col] = df_completo[col].astype(object)
        df_completo.loc[esistenti.index, col] = esistenti[col]
        
    if not nuove_righe.empty:
        df_completo = pd.concat([df_completo, nuove_righe], ignore_index=True)
        
    return df_completo

# ==========================================
# --- MENU DI NAVIGAZIONE LATERALE (HUB) ---
# ==========================================
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    elif os.path.exists("logo.jpg"):
        st.image("logo.jpg", use_container_width=True)
    else:
        st.markdown("<h3 style='text-align:center; color:#2563eb;'>⚙️ GGM.EARTH</h3>", unsafe_allow_html=True)
        
    st.markdown("<p style='font-size:0.75rem; font-weight:700; color:#94a3b8; text-transform:uppercase; letter-spacing:1px; margin-top:10px; margin-bottom:5px;'>Reparti Aziendali</p>", unsafe_allow_html=True)
    
    modulo_scelto = option_menu(
        menu_title=None,
        options=["Registro Strumenti", "Flotta Automezzi", "Personale e Sicurezza"],
        icons=["speedometer2", "truck", "shield-check"],
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#2563eb", "font-size": "17px"}, 
            "nav-link": {
                "font-size": "14px",
                "font-weight": "600",
                "color": "#334155",
                "text-align": "left",
                "margin": "3px 0px",
                "border-radius": "10px",
                "padding": "10px 14px",
            },
            "nav-link-selected": {
                "background-color": "#eff6ff",
                "color": "#1d4ed8",
                "font-weight": "700",
            },
        }
    )
    st.markdown("---")

# ==========================================
# --- MODULO 1: REGISTRO STRUMENTI ISO ---
# ==========================================
if modulo_scelto == "Registro Strumenti":
    df = carica_dati_strumenti()

    if not df.empty:
        for col_drop in ['Contatti Utili', 'Requisiti ISO / Laboratorio', 'Dettaglio Requisiti ISO']:
            if col_drop in df.columns:
                df = df.drop(columns=[col_drop])
        
        if 'Tipo di Controllo' not in df.columns: df['Tipo di Controllo'] = ""
        else: df['Tipo di Controllo'] = df['Tipo di Controllo'].fillna("").astype(str).replace(["nan", "None"], "")
        
        if 'Link Certificato' not in df.columns: df['Link Certificato'] = ""
        else:
            df['Link Certificato'] = df['Link Certificato'].replace(["Inserisci Link PDF", "Inserire Link PDF", "nan", "None"], "")
            df['Link Certificato'] = df['Link Certificato'].fillna("").astype(str)
        
        if 'Marca' not in df.columns: df['Marca'] = ""
        else: df['Marca'] = df['Marca'].fillna("").astype(str).replace(["nan", "None"], "")
        
        if 'Stato Funzionamento' not in df.columns: df['Stato Funzionamento'] = "✅ Funzionante"
        else: df['Stato Funzionamento'] = df['Stato Funzionamento'].fillna("✅ Funzionante").astype(str)
        
        if 'Note Malfunzionamento' not in df.columns: df['Note Malfunzionamento'] = ""
        else: df['Note Malfunzionamento'] = df['Note Malfunzionamento'].fillna("").astype(str).replace(["nan", "None"], "")
        
        if 'Ultima Data' in df.columns: df['Ultima Data'] = pd.to_datetime(df['Ultima Data'], errors='coerce').dt.date
        
        scadenze = []
        for index, row in df.iterrows():
            if pd.notnull(row.get('Ultima Data')) and pd.notnull(row.get('Frequenza (Mesi)')):
                try:
                    freq = str(row['Frequenza (Mesi)']).replace(',', '.')
                    if freq.strip() != "":
                        scad_calc = pd.to_datetime(row['Ultima Data']) + pd.DateOffset(months=int(float(freq)))
                        scadenze.append(scad_calc.date())
                    else:
                        scadenze.append(pd.NaT)
                except: scadenze.append(pd.NaT)
            else: scadenze.append(pd.NaT)
        df['Scadenza'] = scadenze
        
        oggi = datetime.now().date()
        stati_dinamici = []
        for scadenza in df['Scadenza']:
            if pd.isnull(scadenza): 
                stati_dinamici.append("⚪")
            else:
                giorni_rimanenti = (scadenza - oggi).days
                if giorni_rimanenti < 0: 
                    stati_dinamici.append("🔴")
                elif giorni_rimanenti <= 60: 
                    stati_dinamici.append("🟡")
                else: 
                    stati_dinamici.append("🟢")
        df['Stato Attuale'] = stati_dinamici

        with st.sidebar:
            st.markdown("<p style='font-size:0.75rem; font-weight:700; color:#94a3b8; text-transform:uppercase; letter-spacing:1px;'>Ricerca & Filtri</p>", unsafe_allow_html=True)
            testo_ricerca = st.text_input("Cerca strumento:", placeholder="Marca, modello, seriale...", label_visibility="collapsed")
            
            with st.expander("⚙️ Filtri Avanzati"):
                stato_selezionato = st.selectbox("Stato ISO:", ["Tutti", "🟢 In Regola", "🟡 In Scadenza (60gg)", "🔴 Scaduto", "⚪ Incompleto"])
                funzionamento_selezionato = st.selectbox("Funzionamento:", ["Tutti", "✅ Funzionante", "⚠️ Malfunzionamento Lieve", "❌ Guasto / In Riparazione"])
                if 'Categoria' in df.columns:
                    categorie_esistenti = ["Tutte"] + sorted(list(df['Categoria'].replace(["nan", "None", ""], pd.NA).dropna().unique()))
                    categoria_selezionata = st.selectbox("Categoria:", categorie_esistenti)
                else: 
                    categoria_selezionata = "Tutte"

            st.markdown("---")
            st.markdown("<p style='font-size:0.75rem; font-weight:700; color:#94a3b8; text-transform:uppercase; letter-spacing:1px;'>📞 Rubrica Assistenza</p>", unsafe_allow_html=True)
            for nome_azienda in sorted(RUBRICA_FORNITORI.keys()):
                dati = RUBRICA_FORNITORI[nome_azienda]
                with st.expander(nome_azienda):
                    st.markdown(f"**Tel:** {dati['tel']}\n\n**Email:** {dati['email']}")

        df_view = df.copy()
        mappa_filtri_stato = {"🟢 In Regola": "🟢", "🟡 In Scadenza (60gg)": "🟡", "🔴 Scaduto": "🔴", "⚪ Incompleto": "⚪"}
        if stato_selezionato != "Tutti":
            df_view = df_view[df_view['Stato Attuale'] == mappa_filtri_stato[stato_selezionato]]
            
        if 'Stato Funzionamento' in df_view.columns and funzionamento_selezionato != "Tutti": 
            df_view = df_view[df_view['Stato Funzionamento'] == funzionamento_selezionato]
        if 'Categoria' in df_view.columns and categoria_selezionata != "Tutte": 
            df_view = df_view[df_view['Categoria'] == categoria_selezionata]
        if testo_ricerca: 
            df_view = df_view[df_view.apply(lambda row: row.astype(str).str.contains(testo_ricerca, case=False).any(), axis=1)]

        st.title("📊 Registro Tarature e Qualità ISO")
        st.markdown("<p style='color:#64748b; margin-bottom:20px;'>Monitoraggio scadenze di calibrazione, certificati e stato operativo della strumentazione.</p>", unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["📈 Dashboard", "🚨 Scadenze Urgenti", "📝 Database Completo"])

        with tab1:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Totale Strumenti", len(df_view))
            if 'Stato Attuale' in df_view.columns:
                c2.metric("🟢 Operativi", len(df_view[df_view['Stato Attuale'] == '🟢']))
                c3.metric("🟡 In Scadenza (≤60gg)", len(df_view[df_view['Stato Attuale'] == '🟡']))
                c4.metric("🔴 Fermi / Scaduti", len(df_view[df_view['Stato Attuale'] == '🔴']))
                
                st.markdown("<div style='height:15px;'></div>", unsafe_allow_html=True)
                col_grafico1, col_grafico2 = st.columns(2)
                
                with col_grafico1:
                    with st.container(border=True):
                        st.subheader("Stato Certificazioni ISO")
                        conteggio_stati = df_view['Stato Attuale'].value_counts().reset_index()
                        conteggio_stati.columns = ['Stato', 'Conteggio']
                        if not conteggio_stati.empty:
                            base = alt.Chart(conteggio_stati).encode(
                                theta=alt.Theta(field="Conteggio", type="quantitative", stack=True),
                                color=alt.Color(field="Stato", type="nominal", scale=alt.Scale(domain=["🟢", "🟡", "🔴", "⚪"], range=["#10b981", "#f59e0b", "#ef4444", "#cbd5e1"]), legend=alt.Legend(title="Legenda", orient="bottom")),
                                tooltip=['Stato', 'Conteggio']
                            )
                            donut = base.mark_arc(innerRadius=68, outerRadius=110, cornerRadius=6, padAngle=0.02)
                            testo_centro = alt.Chart(pd.DataFrame({'tot': [str(len(df_view))]})).mark_text(size=28, fontWeight='bold', color='#0f172a').encode(text='tot:N')
                            st.altair_chart((donut + testo_centro).properties(height=300).configure_view(strokeWidth=0), use_container_width=True)
                    
                with col_grafico2:
                    with st.container(border=True):
                        st.subheader("Condizione Hardware")
                        if 'Stato Funzionamento' in df_view.columns:
                            conteggio_funz = df_view['Stato Funzionamento'].value_counts().reset_index()
                            conteggio_funz.columns = ['Funzionamento', 'Conteggio']
                            if not conteggio_funz.empty:
                                base_f = alt.Chart(conteggio_funz).encode(
                                    theta=alt.Theta(field="Conteggio", type="quantitative", stack=True),
                                    color=alt.Color(field="Funzionamento", type="nominal", scale=alt.Scale(domain=["✅ Funzionante", "⚠️ Malfunzionamento Lieve", "❌ Guasto / In Riparazione"], range=["#2563eb", "#f59e0b", "#ef4444"]), legend=alt.Legend(title="Condizione", orient="bottom")),
                                    tooltip=['Funzionamento', 'Conteggio']
                                )
                                donut_f = base_f.mark_arc(innerRadius=68, outerRadius=110, cornerRadius=6, padAngle=0.02)
                                testo_centro_f = alt.Chart(pd.DataFrame({'tot': [str(len(df_view))]})).mark_text(size=28, fontWeight='bold', color='#0f172a').encode(text='tot:N')
                                st.altair_chart((donut_f + testo_centro_f).properties(height=300).configure_view(strokeWidth=0), use_container_width=True)

        with tab2:
            with st.container(border=True):
                st.subheader("Bacheca Urgenze")
                st.markdown("Strumenti scaduti o in scadenza entro i prossimi **60 giorni**.")
                df_allarmi = df_view[df_view['Stato Attuale'].isin(['🔴', '🟡'])].copy()
                
                if df_allarmi.empty:
                    st.success("🎉 Tutto in regola! Nessuno strumento richiede intervento immediato.")
                else:
                    colonne_urgenze = ["Stato Attuale", "Marca", "Strumento / Modello", "Seriale / ID", "Scadenza", "Tipo di Controllo"]
                    colonne_urgenze_presenti = [c for c in colonne_urgenze if c in df_allarmi.columns]
                    st.dataframe(df_allarmi[colonne_urgenze_presenti], use_container_width=False, hide_index=True)

        with tab3:
            with st.container(border=True):
                st.markdown("Modifica i dati direttamente nelle celle e clicca su **Salva Modifiche Strumenti**.")
                
                configurazione_colonne = {
                    "Stato Attuale": st.column_config.TextColumn("Stato", width="small", disabled=True), 
                    "Strumento / Modello": st.column_config.TextColumn("Strumento / Modello", width="medium"),
                    "Scadenza": st.column_config.DateColumn("Scadenza", format="DD/MM/YYYY", disabled=True, width="small"),
                    "Stato Funzionamento": st.column_config.SelectboxColumn("Condizione", options=["✅ Funzionante", "⚠️ Malfunzionamento Lieve", "❌ Guasto / In Riparazione"], width="medium", required=True),
                    "Categoria": st.column_config.TextColumn("Categoria", width="small"),
                    "Marca": st.column_config.TextColumn("Marca", width="small"), 
                    "Seriale / ID": st.column_config.TextColumn("Seriale / ID", width="small"),
                    "Ultima Data": st.column_config.DateColumn("Ultima Data", format="DD/MM/YYYY", width="small"),
                    "Frequenza (Mesi)": st.column_config.NumberColumn("Mesi", width="small"),
                    "Tipo di Controllo": st.column_config.TextColumn("Tipo Controllo", width="small"),
                    "Link Certificato": st.column_config.LinkColumn("Certificato", display_text="🔗 PDF", width="small"), 
                    "Note Malfunzionamento": st.column_config.TextColumn("Note Guasto", width="medium")
                }
                
                ordine_desiderato = [
                    "Stato Attuale", "Strumento / Modello", "Scadenza", "Stato Funzionamento", 
                    "Categoria", "Marca", "Seriale / ID", "Ultima Data", "Frequenza (Mesi)", 
                    "Tipo di Controllo", "Link Certificato", "Note Malfunzionamento"
                ]
                
                colonne_visibili = [col for col in ordine_desiderato if col in df_view.columns]
                for col in df_view.columns:
                    if col not in colonne_visibili and col != "Stato": 
                        colonne_visibili.append(col)
                
                df_editato = st.data_editor(
                    df_view[colonne_visibili], 
                    height=580, 
                    use_container_width=False, 
                    hide_index=True, 
                    num_rows="dynamic", 
                    column_config=configurazione_colonne
                )

                st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
                if st.button("💾 Salva Modifiche Strumenti", type="primary"):
                    df_completo = unisci_e_salva_dati(df, df_editato)
                    df_da_salvare = df_completo.drop(columns=['Stato Attuale', 'Scadenza'], errors='ignore')
                    if salva_su_excel(df_da_salvare, "Registro_Strumenti_ISO"):
                        st.success("✅ Modifiche Strumenti salvate con successo su Google Sheets!")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("⚠️ Errore durante il salvataggio su Google Sheets.")

    else:
        st.info("👋 Benvenuto! La tabella è vuota. Aggiungi nuove righe manualmente.")


# ==========================================
# --- MODULO 2: FLOTTA AUTOMEZZI ---
# ==========================================
elif modulo_scelto == "Flotta Automezzi":
    df_flotta = carica_dati_flotta()
    
    if not df_flotta.empty:
        if 'Note' not in df_flotta.columns: df_flotta['Note'] = ""
        df_flotta['Note'] = df_flotta['Note'].fillna("").astype(str).replace(["nan", "None"], "")
        
        for col_data in ["Scadenza Assicurazione", "Scadenza Revisione", "Scadenza Bollo"]:
            if col_data in df_flotta.columns:
                df_flotta[col_data] = pd.to_datetime(df_flotta[col_data], errors='coerce').dt.date
                
        if 'Stato Mezzo' not in df_flotta.columns: df_flotta['Stato Mezzo'] = "🟢 In uso"

        oggi = datetime.now().date()
        stati_allerta = []
        
        for index, row in df_flotta.iterrows():
            date_scadenza = []
            for col in ["Scadenza Assicurazione", "Scadenza Revisione", "Scadenza Bollo"]:
                if pd.notnull(row.get(col)): date_scadenza.append(row[col])
                
            if not date_scadenza:
                stati_allerta.append("⚪")
                continue
                
            peggior_stato = "🟢"
            for d in date_scadenza:
                giorni_rimanenti = (d - oggi).days
                if giorni_rimanenti < 0:
                    peggior_stato = "🔴"
                    break 
                elif giorni_rimanenti <= 30:
                    peggior_stato = "🟡"
            stati_allerta.append(peggior_stato)
            
        df_flotta['Allerta Scadenze'] = stati_allerta

        with st.sidebar:
            st.markdown("<p style='font-size:0.75rem; font-weight:700; color:#94a3b8; text-transform:uppercase; letter-spacing:1px;'>Filtri Flotta</p>", unsafe_allow_html=True)
            testo_ricerca_auto = st.text_input("Cerca Targa o Modello:", placeholder="Es. AB123CD...")
            filtro_allerta = st.selectbox("Stato Scadenze:", ["Tutti", "🟢 In Regola", "🟡 In Scadenza (30gg)", "🔴 Scaduto"])
            
        df_view_flotta = df_flotta.copy()
        mappa_filtri_flotta = {"🟢 In Regola": "🟢", "🟡 In Scadenza (30gg)": "🟡", "🔴 Scaduto": "🔴"}
        if filtro_allerta != "Tutti": 
            df_view_flotta = df_view_flotta[df_view_flotta['Allerta Scadenze'] == mappa_filtri_flotta[filtro_allerta]]
        if testo_ricerca_auto: 
            df_view_flotta = df_view_flotta[df_view_flotta.apply(lambda row: row.astype(str).str.contains(testo_ricerca_auto, case=False).any(), axis=1)]

        st.title("🚗 Gestione Flotta Automezzi")
        st.markdown("<p style='color:#64748b; margin-bottom:20px;'>Controllo assicurazioni, revisioni, bolli e assegnazione veicoli aziendali.</p>", unsafe_allow_html=True)
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Totale Veicoli", len(df_view_flotta))
        c2.metric("🟢 Scadenze OK", len(df_view_flotta[df_view_flotta['Allerta Scadenze'] == '🟢']))
        c3.metric("🟡 In Scadenza (≤30gg)", len(df_view_flotta[df_view_flotta['Allerta Scadenze'] == '🟡']))
        c4.metric("🔴 Scaduti", len(df_view_flotta[df_view_flotta['Allerta Scadenze'] == '🔴']))

        st.markdown("<div style='height:15px;'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            config_colonne_flotta = {
                "Allerta Scadenze": st.column_config.TextColumn("Stato", disabled=True, width="small"),
                "Targa": st.column_config.TextColumn("Targa", required=True, width="small"),
                "Veicolo": st.column_config.TextColumn("Veicolo", width="medium"),
                "Assegnatario": st.column_config.TextColumn("Assegnatario", width="medium"),
                "Stato Mezzo": st.column_config.SelectboxColumn("Stato Mezzo", options=["🟢 In uso", "🟡 In Officina", "🔴 Fermo"], required=True, width="small"),
                "Scadenza Assicurazione": st.column_config.DateColumn("Scadenza Ass.", format="DD/MM/YYYY", width="small"),
                "Scadenza Revisione": st.column_config.DateColumn("Scadenza Rev.", format="DD/MM/YYYY", width="small"),
                "Scadenza Bollo": st.column_config.DateColumn("Scadenza Bollo", format="DD/MM/YYYY", width="small"),
                "Note": st.column_config.TextColumn("Note", width="medium")
            }

            ordine_flotta = ["Allerta Scadenze", "Targa", "Veicolo", "Assegnatario", "Stato Mezzo", "Scadenza Assicurazione", "Scadenza Revisione", "Scadenza Bollo", "Note"]
            colonne_visibili_flotta = [col for col in ordine_flotta if col in df_view_flotta.columns]

            df_flotta_editato = st.data_editor(
                df_view_flotta[colonne_visibili_flotta], 
                height=580, 
                use_container_width=False, 
                hide_index=True, 
                num_rows="dynamic", 
                column_config=config_colonne_flotta
            )
            
            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
            if st.button("💾 Salva Flotta sul Database", type="primary"):
                df_completo_flotta = unisci_e_salva_dati(df_flotta, df_flotta_editato)
                df_da_salvare_f = df_completo_flotta.drop(columns=['Allerta Scadenze']) if 'Allerta Scadenze' in df_completo_flotta.columns else df_completo_flotta
                
                if salva_su_excel(df_da_salvare_f, "Flotta Automezzi"):
                    st.success("✅ Flotta aggiornata e salvata con successo su Google Sheets!")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("⚠️ Errore durante il salvataggio su Google Sheets.")
    else:
        st.info("Tabella flotta vuota. Aggiungi veicoli.")

# ==========================================
# --- MODULO 3: PERSONALE E SICUREZZA ---
# ==========================================
elif modulo_scelto == "Personale e Sicurezza":
    df_personale = carica_dati_personale()
    df_attestati = carica_dati_attestati()
    
    if not df_personale.empty:
        if 'Note' not in df_personale.columns: df_personale['Note'] = ""
        df_personale['Note'] = df_personale['Note'].fillna("").astype(str).replace(["nan", "None"], "")
        
        if 'Note' not in df_attestati.columns: df_attestati['Note'] = ""
        df_attestati['Note'] = df_attestati['Note'].fillna("").astype(str).replace(["nan", "None"], "")
        
        df_personale['ID_Dipendente'] = df_personale['Cognome'].fillna('').astype(str) + " " + df_personale['Nome'].fillna('').astype(str)
        
        if "Scadenza Visita Medica" in df_personale.columns:
            df_personale["Scadenza Visita Medica"] = pd.to_datetime(df_personale["Scadenza Visita Medica"], errors='coerce').dt.date

        if "Data Rilascio" in df_attestati.columns:
            df_attestati["Data Rilascio"] = pd.to_datetime(df_attestati["Data Rilascio"], errors='coerce').dt.date

        oggi = datetime.now().date()
        stati_sicurezza = []
        
        for index, row in df_personale.iterrows():
            id_dip = row['ID_Dipendente']
            cert_dip = df_attestati[df_attestati['ID_Dipendente'] == id_dip]
            
            date_da_controllare = []
            
            if pd.notnull(row.get('Scadenza Visita Medica')): 
                date_da_controllare.append(row['Scadenza Visita Medica'])
                
            for _, cert in cert_dip.iterrows():
                if pd.notnull(cert.get('Data Rilascio')) and pd.notnull(cert.get('Validità (Anni)')):
                    try:
                        validita = str(cert['Validità (Anni)']).replace(',', '.')
                        if validita.strip() != "":
                            scad = pd.to_datetime(cert['Data Rilascio']) + pd.DateOffset(years=int(float(validita)))
                            date_da_controllare.append(scad.date())
                    except:
                        pass
                
            if not date_da_controllare:
                stati_sicurezza.append("⚪")
                continue
                
            peggior_stato = "🟢"
            for d in date_da_controllare:
                giorni_rimanenti = (d - oggi).days
                if giorni_rimanenti < 0:
                    peggior_stato = "🔴"
                    break 
                elif giorni_rimanenti <= 60:
                    peggior_stato = "🟡"
                    
            stati_sicurezza.append(peggior_stato)
            
        df_personale['Stato Sicurezza'] = stati_sicurezza

        with st.sidebar:
            st.markdown("<p style='font-size:0.75rem; font-weight:700; color:#94a3b8; text-transform:uppercase; letter-spacing:1px;'>Filtri Personale</p>", unsafe_allow_html=True)
            testo_ricerca_pers = st.text_input("Cerca Nome, Cognome o Ruolo:", placeholder="Digita per filtrare...")
            filtro_sicurezza = st.selectbox("Stato Sicurezza:", ["Tutti", "🟢 In Regola", "🟡 In Scadenza (60gg)", "🔴 Scaduto"])
            
        df_view_personale = df_personale.copy()
        mappa_filtri_sicurezza = {"🟢 In Regola": "🟢", "🟡 In Scadenza (60gg)": "🟡", "🔴 Scaduto": "🔴"}
        if filtro_sicurezza != "Tutti": 
            df_view_personale = df_view_personale[df_view_personale['Stato Sicurezza'] == mappa_filtri_sicurezza[filtro_sicurezza]]
        if testo_ricerca_pers: 
            df_view_personale = df_view_personale[df_view_personale.apply(lambda row: row.astype(str).str.contains(testo_ricerca_pers, case=False).any(), axis=1)]

        st.title("🦺 Gestione Personale e Attestati")
        st.markdown("<p style='color:#64748b; margin-bottom:20px;'>Anagrafica dipendenti, scadenze visite mediche e registro formazione sicurezza.</p>", unsafe_allow_html=True)

        tab_anagrafica, tab_fascicolo = st.tabs(["👥 Anagrafica e Stato Generale", "🎓 Fascicolo Attestati"])

        with tab_anagrafica:
            with st.container(border=True):
                st.subheader("Elenco Dipendenti")
                
                if "ruoli_custom" not in st.session_state:
                    st.session_state.ruoli_custom = []

                ruoli_base = ["Dipendente", "Titolare", "CEO", "Amministrativo", "Tecnico", "Responsabile"]
                ruoli_storici = df_personale['Ruolo'].replace(["nan", "None", ""], pd.NA).dropna().unique().tolist()
                lista_ruoli = sorted(list(set(ruoli_base + ruoli_storici + st.session_state.ruoli_custom)))

                with st.expander("➕ Crea un nuovo Ruolo per la tendina"):
                    col_r1, col_r2 = st.columns([3, 1])
                    nuovo_ruolo = col_r1.text_input("Digita il nuovo ruolo (es. Consulente, Stagista):", label_visibility="collapsed", placeholder="Es. Consulente, Stagista...")
                    if col_r2.button("Aggiungi al menù", type="secondary", use_container_width=True):
                        if nuovo_ruolo and nuovo_ruolo.strip() not in lista_ruoli:
                            st.session_state.ruoli_custom.append(nuovo_ruolo.strip())
                            st.rerun()

                config_colonne_personale = {
                    "Stato Sicurezza": st.column_config.TextColumn("Stato", disabled=True, width="small"),
                    "Cognome": st.column_config.TextColumn("Cognome", required=True, width="medium"),
                    "Nome": st.column_config.TextColumn("Nome", required=True, width="medium"),
                    "Ruolo": st.column_config.SelectboxColumn("Ruolo", options=lista_ruoli, width="medium"),
                    "Scadenza Visita Medica": st.column_config.DateColumn("Scad. Visita Medica", format="DD/MM/YYYY", width="small"),
                    "Note": st.column_config.TextColumn("Note", width="large")
                }

                ordine_personale = ["Stato Sicurezza", "Cognome", "Nome", "Ruolo", "Scadenza Visita Medica", "Note"]
                colonne_visibili_personale = [col for col in ordine_personale if col in df_view_personale.columns]

                df_personale_editato = st.data_editor(
                    df_view_personale[colonne_visibili_personale], 
                    height=550,
                    use_container_width=False, 
                    hide_index=True, 
                    num_rows="dynamic",
                    column_config=config_colonne_personale
                )
                
                st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
                if st.button("💾 Salva Anagrafica", type="primary"):
                    df_completo_personale = unisci_e_salva_dati(df_personale, df_personale_editato)
                    colonne_da_rimuovere = ['Stato Sicurezza', 'ID_Dipendente']
                    df_da_salvare_p = df_completo_personale.drop(columns=[col for col in colonne_da_rimuovere if col in df_completo_personale.columns])
                    
                    if salva_su_excel(df_da_salvare_p, "Personale e Sicurezza"):
                        st.success("✅ Anagrafica salvata con successo su Google Sheets!")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("⚠️ Errore durante il salvataggio su Google Sheets.")

        with tab_fascicolo:
            with st.container(border=True):
                lista_dipendenti = df_personale['ID_Dipendente'].tolist()
                
                if not lista_dipendenti:
                    st.info("Aggiungi prima un dipendente nella scheda 'Anagrafica' per potergli assegnare dei corsi.")
                else:
                    dipendente_selezionato = st.selectbox("Seleziona il dipendente di cui gestire il fascicolo:", lista_dipendenti)
                    st.subheader(f"Attestati di: {dipendente_selezionato}")
                    
                    lista_corsi_base = [
                        "Sicurezza Lavoratori (Base)", "Sicurezza Lavoratori (Specifica)", "Addetto Antincendio", 
                        "Primo Soccorso", "Lavori in Quota / DPI 3° cat.", "Spazi Confinati", "PES / PAV", 
                        "Carrelli Elevatori (Muletto)", "Preposto", "Dirigente", "Altro"
                    ]
                    corsi_storici = df_attestati["Nome Corso"].dropna().unique().tolist()
                    tutti_i_corsi = sorted(list(set(lista_corsi_base + corsi_storici)))

                    with st.expander("➕ Inserisci un nuovo tipo di corso non in lista"):
                        c1, c2, c3 = st.columns([2, 1, 1])
                        corso_custom = c1.text_input("Nome del nuovo corso:")
                        data_custom = c2.date_input("Data di Rilascio:", format="DD/MM/YYYY")
                        anni_custom = c3.number_input("Validità (Anni):", min_value=1, value=5, step=1)
                        
                        if st.button("Assegna e Impara Corso", type="primary", key="btn_custom"):
                            if corso_custom:
                                nuova_riga = pd.DataFrame([{
                                    "ID_Dipendente": dipendente_selezionato,
                                    "Nome Corso": corso_custom.strip(),
                                    "Data Rilascio": data_custom,
                                    "Validità (Anni)": anni_custom,
                                    "Note": ""
                                }])
                                df_finale = pd.concat([df_attestati, nuova_riga], ignore_index=True)
                                if salva_su_excel(df_finale, "Attestati"):
                                    st.success(f"✅ '{corso_custom}' aggiunto al fascicolo!")
                                    st.cache_data.clear()
                                    st.rerun()
                            else:
                                st.warning("Inserisci il nome del corso!")
                    
                    df_att_filtrato = df_attestati[df_attestati['ID_Dipendente'] == dipendente_selezionato].copy()
                    
                    scadenze_visive = []
                    stati_visivi = []
                    oggi_calc = datetime.now().date()
                    
                    for _, row in df_att_filtrato.iterrows():
                        if pd.notnull(row.get('Data Rilascio')) and pd.notnull(row.get('Validità (Anni)')):
                            try:
                                validita = str(row['Validità (Anni)']).replace(',', '.')
                                if validita.strip() != "":
                                    scad = pd.to_datetime(row['Data Rilascio']) + pd.DateOffset(years=int(float(validita)))
                                    scadenze_visive.append(scad.date())
                                    
                                    giorni_rimanenti = (scad.date() - oggi_calc).days
                                    if giorni_rimanenti < 0:
                                        stati_visivi.append("🔴")
                                    elif giorni_rimanenti <= 60:
                                        stati_visivi.append("🟡")
                                    else:
                                        stati_visivi.append("🟢")
                                else:
                                    scadenze_visive.append(pd.NaT)
                                    stati_visivi.append("⚪")
                            except:
                                scadenze_visive.append(pd.NaT)
                                stati_visivi.append("⚪")
                        else:
                            scadenze_visive.append(pd.NaT)
                            stati_visivi.append("⚪")
                            
                    df_att_filtrato['Scadenza (Calcolata)'] = scadenze_visive
                    df_att_filtrato['Stato'] = stati_visivi

                    config_attestati = {
                        "Stato": st.column_config.TextColumn("Stato", disabled=True, width="small"),
                        "Nome Corso": st.column_config.SelectboxColumn("Corso Frequentato", options=tutti_i_corsi, required=True, width="medium"),
                        "Data Rilascio": st.column_config.DateColumn("Data Rilascio", format="DD/MM/YYYY", required=True, width="small"),
                        "Validità (Anni)": st.column_config.NumberColumn("Durata (Anni)", default=5, min_value=1, required=True, width="small"),
                        "Scadenza (Calcolata)": st.column_config.DateColumn("Scadenza Prevista", format="DD/MM/YYYY", disabled=True, width="small"),
                        "Note": st.column_config.TextColumn("Note", width="large")
                    }
                    
                    colonne_attestati = ["Stato", "Nome Corso", "Data Rilascio", "Validità (Anni)", "Scadenza (Calcolata)", "Note"]
                    
                    df_att_editato = st.data_editor(
                        df_att_filtrato[colonne_attestati],
                        height=550,
                        use_container_width=False,
                        hide_index=True,
                        num_rows="dynamic",
                        column_config=config_attestati
                    )
                    
                    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
                    if st.button(f"💾 Salva Fascicolo di {dipendente_selezionato}", type="primary"):
                        df_att_da_salvare = df_att_editato.drop(columns=['Scadenza (Calcolata)', 'Stato'], errors='ignore')
                        df_att_da_salvare['ID_Dipendente'] = dipendente_selezionato
                        
                        df_attestati_pulito = df_attestati[df_attestati['ID_Dipendente'] != dipendente_selezionato]
                        df_finale = pd.concat([df_attestati_pulito, df_att_da_salvare], ignore_index=True)
                        
                        if salva_su_excel(df_finale, "Attestati"):
                            st.success(f"✅ Fascicolo aggiornato su Google Sheets!")
                            st.cache_data.clear()
                            st.rerun()
    else:
         st.info("Nessun dipendente trovato. Aggiungili manualmente.")