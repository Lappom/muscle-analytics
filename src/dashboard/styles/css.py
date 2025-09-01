"""
Styles CSS nettoyés et optimisés pour le dashboard Streamlit
"""

def get_main_css() -> str:
    """Retourne le CSS principal optimisé pour le dashboard"""
    return """
    <style>
        /* Variables CSS principales */
        :root {
            --primary-color: #1f77b4;
            --secondary-color: #ff7f0e;
            --success-color: #2ecc71;
            --warning-color: #f39c12;
            --danger-color: #e74c3c;
            --background-light: #f8f9fa;
            --background-white: #ffffff;
            --text-dark: #1a1a1a;
            --text-very-dark: #000000;
            --text-muted: #6c757d;
            --border-radius: 0.75rem;
            --shadow: 0 2px 8px rgba(0,0,0,0.1);
            --shadow-hover: 0 4px 16px rgba(0,0,0,0.15);
            --transition: all 0.2s ease;
        }
        
        /* En-tête principal */
        .main-header {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            padding: 1rem 2rem;
            border-radius: var(--border-radius);
            color: white;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: var(--shadow);
        }
        
        /* Sidebar - Design général */
        .stSidebar {
            background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
            border-right: 1px solid #e9ecef;
            box-shadow: 2px 0 8px rgba(0,0,0,0.08);
        }
        
        .sidebar-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 16px;
            margin-bottom: 1.5rem;
            text-align: center;
            box-shadow: var(--shadow);
        }
        
        .sidebar-section {
            padding: 1.5rem 0;
            margin-bottom: 2rem;
            border-bottom: 1px solid rgba(0,0,0,0.06);
        }
        
        .sidebar-section:last-child {
            border-bottom: none;
        }
        
        .sidebar-section h3 {
            color: var(--text-dark);
            margin-bottom: 1.25rem;
            font-size: 1.15rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding-bottom: 0.75rem;
            background: linear-gradient(90deg, var(--primary-color), var(--secondary-color)) left bottom / 40% 3px no-repeat;
        }
        
        /* Statut API */
        .api-status {
            display: inline-flex;
            align-items: center;
            font-size: 0.9rem;
            font-weight: 600;
            padding: 0.6rem 1rem;
            border-radius: 12px;
            box-shadow: var(--shadow);
            transition: var(--transition);
        }
        
        .api-status:hover {
            transform: translateY(-1px);
            box-shadow: var(--shadow-hover);
        }
        
        .api-status.connected {
            background: rgba(46, 204, 113, 0.15);
            color: var(--success-color);
            border: 2px solid rgba(46, 204, 113, 0.3);
        }
        
        .api-status.disconnected {
            background: rgba(231, 76, 60, 0.15);
            color: var(--danger-color);
            border: 2px solid rgba(231, 76, 60, 0.3);
        }
        
        /* Groupes de filtres */
        .filter-group {
            margin-bottom: 1.5rem;
            padding: 1.25rem;
            background: linear-gradient(135deg, rgba(248, 249, 250, 0.8) 0%, rgba(255, 255, 255, 0.9) 100%);
            border-radius: 16px;
            border: 2px solid #e9ecef;
            transition: var(--transition);
            box-shadow: var(--shadow);
        }
        
        .filter-group:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-hover);
            border-color: rgba(31, 119, 180, 0.3);
        }
        
        .filter-label {
            font-weight: 600;
            color: var(--text-dark);
            margin-bottom: 0.75rem;
            font-size: 0.95rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .filter-label::before {
            content: '';
            width: 4px;
            height: 4px;
            background: var(--primary-color);
            border-radius: 50%;
            transition: var(--transition);
        }
        
        .filter-group:hover .filter-label::before {
            width: 6px;
            height: 6px;
            background: var(--secondary-color);
        }
        
        /* Actions rapides */
        .quick-actions {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.75rem;
            margin-top: 1.5rem;
            padding: 1rem;
            background: rgba(248, 249, 250, 0.5);
            border-radius: 16px;
            border: 1px solid rgba(233, 236, 239, 0.6);
        }
        
        .action-button {
            padding: 0.6rem;
            border-radius: calc(var(--border-radius) - 0.25rem);
            border: 1px solid var(--primary-color);
            background: var(--background-white);
            color: var(--primary-color);
            font-weight: 500;
            font-size: 0.85rem;
            cursor: pointer;
            transition: var(--transition);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.25rem;
        }
        
        .action-button:hover {
            background: var(--primary-color);
            color: white;
            transform: translateY(-1px);
            box-shadow: var(--shadow);
        }
        
        /* Chips de présélection */
        .preset-chip {
            display: inline-block;
            padding: 0.4rem 0.8rem;
            background: linear-gradient(135deg, var(--primary-color) 0%, #2980b9 100%);
            color: white;
            border-radius: 16px;
            font-size: 0.75rem;
            font-weight: 600;
            margin: 0.2rem;
            box-shadow: 0 2px 6px rgba(31, 119, 180, 0.25);
            transition: var(--transition);
        }
        
        .preset-chip:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(31, 119, 180, 0.35);
        }
        
        /* Cartes de métriques */
        .metric-card {
            background: var(--background-white);
            padding: 1.5rem;
            border-radius: var(--border-radius);
            border-left: 4px solid var(--primary-color);
            margin: 0.5rem 0;
            box-shadow: var(--shadow);
            transition: var(--transition);
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-hover);
        }
        
        /* Alertes */
        .alert-warning {
            background: rgba(243, 156, 18, 0.1);
            border: 1px solid var(--warning-color);
            border-left: 4px solid var(--warning-color);
            padding: 1rem;
            border-radius: var(--border-radius);
            margin: 1rem 0;
            color: var(--text-dark);
        }
        
        .alert-success {
            background: rgba(46, 204, 113, 0.1);
            border: 1px solid var(--success-color);
            border-left: 4px solid var(--success-color);
            padding: 1rem;
            border-radius: var(--border-radius);
            margin: 1rem 0;
            color: var(--text-dark);
        }
        
        /* Résumé des filtres */
        .filter-summary {
            background: linear-gradient(135deg, rgba(248, 249, 250, 0.9) 0%, rgba(255, 255, 255, 1) 100%);
            padding: 1.25rem;
            border-radius: 16px;
            margin-top: 1.5rem;
            border: 2px solid rgba(233, 236, 239, 0.6);
            font-size: 0.9rem;
            color: var(--text-muted);
            box-shadow: var(--shadow);
            transition: var(--transition);
            position: relative;
        }
        
        .filter-summary::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background: linear-gradient(90deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        }
        
        .filter-summary:hover {
            border-color: rgba(31, 119, 180, 0.3);
            box-shadow: var(--shadow-hover);
            transform: translateY(-1px);
        }
        
        /* Styles pour composants Streamlit spécifiques */
        .stApp {
            background-color: #ffffff;
            color: var(--text-dark);
        }
        
        /* Forcer l'entête/toolbar et le conteneur principal en mode CLAIR */
        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stAppViewContainer"] {
            background: #ffffff !important;
            background-image: none !important;
            color: var(--text-dark) !important;
            color-scheme: light !important;
        }

        [data-testid="stHeader"] *,
        [data-testid="stToolbar"] * {
            color: var(--text-dark) !important;
            fill: var(--text-dark) !important; /* icônes SVG */
        }

        /* Dans certains builds Streamlit, un wrapper peut imposer un fond sombre via une classe emotion */
        .stApp .st-emotion-cache-13k62yr,
        .stApp .st-emotion-cache-gquqoo {
            background: #ffffff !important;
            background-image: none !important;
            color: var(--text-dark) !important;
            color-scheme: light !important;
        }

        /* FileUploader (dropzone) en mode clair */
        [data-testid="stFileUploaderDropzone"] {
            background: #ffffff !important;
            border: 2px dashed #e9ecef !important;
            border-radius: 12px !important;
            color: var(--text-dark) !important;
            box-shadow: var(--shadow);
            height: auto !important;
        }

        /* Contenu de la dropzone */
        [data-testid="stFileUploaderDropzone"] *,
        [data-testid="stFileUploaderDropzoneInstructions"] span {
            color: var(--text-dark) !important;
        }

        /* Bouton Parcourir en clair */
        [data-testid="stFileUploaderDropzone"] [data-testid="stBaseButton-secondary"],
        [data-testid="stFileUploaderDropzone"] button {
            background: #ffffff !important;
            color: var(--text-dark) !important;
            border: 1px solid #e9ecef !important;
            border-radius: 10px !important;
            transition: var(--transition);
        }
        [data-testid="stFileUploaderDropzone"] [data-testid="stBaseButton-secondary"]:hover,
        [data-testid="stFileUploaderDropzone"] button:hover {
            background: var(--primary-color) !important;
            color: #ffffff !important;
            border-color: var(--primary-color) !important;
            box-shadow: var(--shadow-hover);
            transform: translateY(-1px);
        }

        /* Correction: forcer les couleurs de texte en MODE CLAIR
           (utile si l'utilisateur a un thème Streamlit sombre global)
           On cible uniquement le mode clair via la détection de fond non sombre */
        .stApp:not([style*="rgb(14, 17, 23)"]) p,
        .stApp:not([style*="rgb(14, 17, 23)"]) span,
        .stApp:not([style*="rgb(14, 17, 23)"]) li,
        .stApp:not([style*="rgb(14, 17, 23)"]) a,
        .stApp:not([style*="rgb(14, 17, 23)"]) label,
        .stApp:not([style*="rgb(14, 17, 23)"]) small,
        .stApp:not([style*="rgb(14, 17, 23)"]) strong,
        .stApp:not([style*="rgb(14, 17, 23)"]) em,
        .stApp:not([style*="rgb(14, 17, 23)"]) h1,
        .stApp:not([style*="rgb(14, 17, 23)"]) h2,
        .stApp:not([style*="rgb(14, 17, 23)"]) h3,
        .stApp:not([style*="rgb(14, 17, 23)"]) h4,
        .stApp:not([style*="rgb(14, 17, 23)"]) h5,
        .stApp:not([style*="rgb(14, 17, 23)"]) h6,
        .stApp:not([style*="rgb(14, 17, 23)"]) code,
        .stApp:not([style*="rgb(14, 17, 23)"]) pre,
        .stApp:not([style*="rgb(14, 17, 23)"]) [data-testid="stMarkdownContainer"],
        .stApp:not([style*="rgb(14, 17, 23)"]) [data-testid="stMarkdownContainer"] * {
            color: var(--text-dark) !important;
        }
        
        /* Champs de formulaire en mode clair */
        .stApp:not([style*="rgb(14, 17, 23)"]) input,
        .stApp:not([style*="rgb(14, 17, 23)"]) textarea,
        .stApp:not([style*="rgb(14, 17, 23)"]) select {
            color: var(--text-dark) !important;
        }
        
        /* Contrôles de formulaire - Sidebar */
        .stSidebar * {
            color: var(--text-dark);
        }
        
        .stSidebar .stSelectbox > div > div,
        .stSidebar .stMultiSelect > div > div {
            background: var(--background-white);
            color: var(--text-dark);
            border: 2px solid #e9ecef;
            border-radius: 12px;
            box-shadow: var(--shadow);
            transition: var(--transition);
        }
        
        .stSidebar .stSelectbox > div > div:hover,
        .stSidebar .stMultiSelect > div > div:hover {
            border-color: var(--primary-color);
            box-shadow: 0 4px 8px rgba(31, 119, 180, 0.15);
            transform: translateY(-1px);
        }
        
        .stSidebar .stSelectbox label,
        .stSidebar .stMultiSelect label {
            color: #374151;
            font-weight: 600;
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
        }
        
        /* Boutons - Sidebar */
        .stSidebar .stButton > button {
            background: var(--background-white);
            color: var(--text-dark);
            border: 2px solid #e9ecef;
            border-radius: 12px;
            font-weight: 600;
            padding: 0.75rem 1rem;
            transition: var(--transition);
            box-shadow: var(--shadow);
        }
        
        .stSidebar .stButton > button:hover {
            background: var(--primary-color);
            color: white;
            border-color: var(--primary-color);
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(31, 119, 180, 0.25);
        }
        
        /* Checkboxes */
        .stSidebar .stCheckbox > label {
            color: #374151;
            font-weight: 500;
            font-size: 0.9rem;
        }
        
        .stSidebar .stCheckbox input[type="checkbox"] {
            background: var(--background-white);
            border: 2px solid #e9ecef;
            border-radius: 6px;
            transition: var(--transition);
        }
        
        .stSidebar .stCheckbox input[type="checkbox"]:checked {
            background: var(--primary-color);
            border-color: var(--primary-color);
        }
        
        /* Sliders */
        .stSidebar .stSlider label {
            color: #374151;
            font-weight: 600;
            font-size: 0.9rem;
            margin-bottom: 0.75rem;
        }
        
        /* Expanders */
        .stSidebar .stExpander {
            background: var(--background-white);
            border: 2px solid #e9ecef;
            border-radius: 16px;
            margin: 1rem 0;
            box-shadow: var(--shadow);
            transition: var(--transition);
            overflow: hidden;
        }
        
        .stSidebar .stExpander:hover {
            border-color: var(--primary-color);
            box-shadow: var(--shadow-hover);
            transform: translateY(-2px);
        }
        
        /* Header des expandeurs (fermés) */
        .stSidebar .stExpander summary {
            background: #f8f9fa;
            color: var(--text-dark);
            border-radius: 14px;
            padding: 1rem 1.25rem;
            font-weight: 700;
            font-size: 1rem;
            border-bottom: none;
            transition: var(--transition);
            margin: 0;
        }
        
        /* Header des expandeurs (ouverts) */
        .stSidebar .stExpander[open] summary {
            background: #f8f9fa;
            color: var(--text-dark);
            border-radius: 14px 14px 0 0;
            padding: 1rem 1.25rem;
            font-weight: 700;
            font-size: 1rem;
            border-bottom: 1px solid #e9ecef;
            transition: var(--transition);
        }
        
        .stSidebar .stExpander summary:hover {
            background: #e9f4ff;
            color: var(--primary-color);
        }
        
        /* Styles supplémentaires pour les expandeurs Streamlit */
        .stSidebar .streamlit-expanderHeader {
            background: #f8f9fa !important;
            border-radius: 14px !important;
            border-bottom: none !important;
            transition: var(--transition) !important;
        }
        
        .stSidebar .streamlit-expanderHeader:hover {
            background: #e9f4ff !important;
            color: var(--primary-color) !important;
        }
        
        /* Expandeur ouvert */
        .stSidebar [data-testid="stExpander"][aria-expanded="true"] .streamlit-expanderHeader,
        .stSidebar .stExpander[data-testid="stExpander"][aria-expanded="true"] summary {
            border-radius: 14px 14px 0 0 !important;
            border-bottom: 1px solid #e9ecef !important;
        }
        
        /* Expandeur fermé */
        .stSidebar [data-testid="stExpander"][aria-expanded="false"] .streamlit-expanderHeader,
        .stSidebar .stExpander[data-testid="stExpander"][aria-expanded="false"] summary {
            border-radius: 14px !important;
            border-bottom: none !important;
        }
        
        /* Classes emotion-cache pour les expandeurs */
        .stSidebar [class*="st-emotion-cache"] details summary {
            background: #f8f9fa !important;
            border-radius: 14px !important;
            border-bottom: none !important;
            transition: var(--transition) !important;
        }
        
        .stSidebar [class*="st-emotion-cache"] details[open] summary {
            border-radius: 14px 14px 0 0 !important;
            border-bottom: 1px solid #e9ecef !important;
        }
        
        .stSidebar [class*="st-emotion-cache"] details summary:hover {
            background: #e9f4ff !important;
            color: var(--primary-color) !important;
        }
            color: var(--primary-color);
        }
        
        /* Dates */
        .stSidebar .stDateInput > div > div {
            background: var(--background-white);
            color: var(--text-dark);
            border: 2px solid #e9ecef;
            border-radius: 12px;
            box-shadow: var(--shadow);
            transition: var(--transition);
            padding: 0.75rem;
        }
        
        .stSidebar .stDateInput > div > div:hover {
            border-color: var(--primary-color);
            box-shadow: 0 4px 8px rgba(31, 119, 180, 0.15);
            transform: translateY(-1px);
        }
        
        .stSidebar .stDateInput label {
            color: #374151;
            font-weight: 600;
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
        }
        
        /* Métriques principales */
        .stMetric {
            background-color: #ffffff !important;
            padding: 1.2rem !important;
            border-radius: 12px !important;
            border: 2px solid #e9ecef !important;
            box-shadow: var(--shadow);
            transition: var(--transition);
        }
        
        .stMetric:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-hover);
            border-color: #3498db !important;
        }
        
        .stMetric > div {
            color: #000000 !important;
            background-color: #ffffff !important;
        }
        
        .stMetric label {
            color: #2c3e50 !important;
            font-weight: 700 !important;
            font-size: 1rem !important;
        }
        
        .stMetric [data-testid="metric-value"] {
            color: #000000 !important;
            font-weight: 900 !important;
            font-size: 2.2rem !important;
            text-shadow: none !important;
        }
        
        /* Sélecteurs alternatifs pour forcer les couleurs */
        [data-testid="stMetricValue"] {
            color: #000000 !important;
        }
        
        [data-testid="stMetricValue"] div {
            color: #000000 !important;
            font-weight: 900 !important;
        }
        
        [data-testid="stMetricValue"] * {
            color: #000000 !important;
        }
        
        .stMetric [data-testid="metric-delta"] {
            color: #6c757d !important;
            font-weight: 600 !important;
        }
        
        /* Styles spécifiques pour les deltas positifs/négatifs */
        .stMetric [data-testid="metric-delta"][title*="+"]:not([title*="-"]) {
            color: #27ae60 !important;
            font-weight: 700 !important;
        }
        
        .stMetric [data-testid="metric-delta"][title*="-"] {
            color: #c0392b !important;
            font-weight: 700 !important;
        }
        
        /* Force les couleurs sur tous les éléments de métriques */
        .stMetric div[data-testid="metric-value"] div {
            color: #000000 !important;
        }
        
        .stMetric div[data-testid="metric-label"] {
            color: #2c3e50 !important;
        }
        
        /* Force les couleurs sur les classes internes de Streamlit */
        .stMetric .st-emotion-cache-1q82h82 {
            color: #000000 !important;
            font-weight: 900 !important;
        }
        
        .stMetric .st-emotion-cache-efbu8t {
            color: #000000 !important;
        }
        
        .stMetric .st-emotion-cache-efbu8t div {
            color: #000000 !important;
            font-weight: 900 !important;
        }
        
        /* Force tous les div dans les métriques */
        .stMetric div div {
            color: #000000 !important;
        }
        
        /* Sélecteur très spécifique pour les valeurs de métriques */
        div[data-testid="stMetric"] div[data-testid="stMetricValue"] div {
            color: #000000 !important;
            font-weight: 900 !important;
            font-size: 2.2rem !important;
        }
        
        /* Force calendriers popup en mode clair */
        [data-baseweb="calendar"] {
            background-color: var(--background-white);
            border: 1px solid #e9ecef;
            box-shadow: var(--shadow-hover);
        }
        
        [data-baseweb="calendar"] * {
            background-color: var(--background-white);
            color: var(--text-dark);
        }
        
        [data-baseweb="calendar"] [aria-selected="true"] {
            background-color: var(--primary-color);
            color: white;
        }
        
        /* Force dropdown menus */
        [data-baseweb="popover"] {
            background-color: var(--background-white);
        }
        
        [data-baseweb="popover"] * {
            background-color: var(--background-white);
            color: var(--text-dark);
        }
        
        [role="listbox"] {
            background-color: var(--background-white);
            border: 1px solid #e9ecef;
            box-shadow: var(--shadow-hover);
        }
        
        [role="option"] {
            background-color: var(--background-white);
            color: var(--text-dark);
        }
        
        [role="option"]:hover {
            background-color: #f8f9fa;
            color: var(--text-dark);
        }
        
        /* Badges de filtres */
        .filter-badge {
            display: inline-block;
            background: linear-gradient(135deg, var(--primary-color) 0%, #2980b9 100%);
            color: white;
            padding: 0.5rem 0.75rem;
            border-radius: 16px;
            font-size: 0.75rem;
            font-weight: 600;
            box-shadow: 0 2px 6px rgba(31, 119, 180, 0.25);
            margin: 0.25rem;
            transition: var(--transition);
        }
        
        .filter-badge:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(31, 119, 180, 0.35);
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .stSidebar {
                font-size: 0.9rem;
            }
            
            .sidebar-section {
                padding: 1rem 0;
            }
            
            .sidebar-section h3 {
                font-size: 1rem;
                gap: 0.5rem;
            }
            
            .quick-actions {
                grid-template-columns: 1fr;
                gap: 0.5rem;
                padding: 0.75rem;
            }
            
            .filter-group {
                padding: 1rem;
                margin-bottom: 1rem;
            }
        }
        
        @media (max-width: 480px) {
            .sidebar-header {
                padding: 1rem;
                margin-bottom: 1rem;
            }
            
            .filter-group {
                padding: 0.75rem;
            }
            
            .quick-actions {
                padding: 0.5rem;
            }
            
            .action-button {
                padding: 0.5rem 0.75rem;
                font-size: 0.75rem;
            }
        }
        
        /* STYLES FORCÉS POUR METRICS - PRIORITÉ MAXIMALE */
        /* Mode clair uniquement */
        .stApp:not([style*="rgb(14, 17, 23)"]) .stMetric *,
        .stApp[style*="rgb(255, 255, 255)"] .stMetric *,
        body:not([style*="rgb(14, 17, 23)"]) .stMetric * {
            color: #000000 !important;
        }
        
        /* Force spécifiquement les valeurs numériques en mode clair */
        .stApp:not([style*="rgb(14, 17, 23)"]) .stMetric [data-testid="stMetricValue"] div,
        .stApp[style*="rgb(255, 255, 255)"] [data-testid="stMetricValue"] div,
        body:not([style*="rgb(14, 17, 23)"]) .stMetric .st-emotion-cache-1q82h82,
        body:not([style*="rgb(14, 17, 23)"]) .stMetric .st-emotion-cache-efbu8t div {
            color: #000000 !important;
            font-weight: 900 !important;
            font-size: 2.2rem !important;
        }
        
        /* Labels en mode clair */
        .stApp:not([style*="rgb(14, 17, 23)"]) .stMetric [data-testid="stMetricLabel"],
        body:not([style*="rgb(14, 17, 23)"]) .stMetric label {
            color: #2c3e50 !important;
        }
    </style>
    
    <script>
        // Force les couleurs des métriques via JavaScript selon le thème
        function forceMetricsColors() {
            const metrics = document.querySelectorAll('[data-testid="stMetric"]');
            
            // Détection du thème sombre
            const isDarkTheme = document.body.style.backgroundColor === 'rgb(14, 17, 23)' ||
                               document.querySelector('.st-emotion-cache-13k62yr') !== null ||
                               document.body.classList.contains('dark') ||
                               window.getComputedStyle(document.body).backgroundColor === 'rgb(14, 17, 23)';
            
            metrics.forEach(metric => {
                const values = metric.querySelectorAll('[data-testid="stMetricValue"] div, .st-emotion-cache-1q82h82, .st-emotion-cache-efbu8t div');
                values.forEach(value => {
                    if (isDarkTheme) {
                        value.style.color = '#ffffff';
                        value.style.textShadow = '0 2px 6px rgba(0, 0, 0, 0.4)';
                    } else {
                        value.style.color = '#000000';
                        value.style.textShadow = 'none';
                    }
                    value.style.fontWeight = '900';
                    value.style.fontSize = '2.2rem';
                });
                
                const labels = metric.querySelectorAll('[data-testid="stMetricLabel"]');
                labels.forEach(label => {
                    if (isDarkTheme) {
                        label.style.color = '#b0b0b0';
                    } else {
                        label.style.color = '#2c3e50';
                    }
                    label.style.fontWeight = '700';
                });
            });
        }
        
        // Exécuter au chargement
        document.addEventListener('DOMContentLoaded', forceMetricsColors);
        
        // Observer les changements dans le DOM
        const observer = new MutationObserver(forceMetricsColors);
        observer.observe(document.body, { childList: true, subtree: true, attributes: true, attributeFilter: ['style', 'class'] });
        
        // Forcer toutes les 500ms
        setInterval(forceMetricsColors, 500);
    </script>
    """

def get_dark_theme_css() -> str:
    """Retourne le CSS pour le thème sombre (simplifié)"""
    return """
    <style>
        /* Variables pour le mode sombre */
        :root {
            --primary-color-dark: #4a9eff;
            --secondary-color-dark: #ff9f40;
            --success-color-dark: #4ecdc4;
            --warning-color-dark: #ffd93d;
            --danger-color-dark: #ff6b6b;
            --background-dark: #0E1117;
            --background-card-dark: #262730;
            --text-light: #ffffff;
            --text-light-muted: #a0a0a0;
            --border-dark: #404040;
        }
        
        .stApp {
            background-color: var(--background-dark) !important;
            color: var(--text-light) !important;
        }
        
        .main-header {
            background: linear-gradient(135deg, #1f4e79, #2c5f8a);
            color: white;
            padding: 1rem 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        
        /* Métriques en mode sombre */
        .stMetric {
            background-color: var(--background-card-dark) !important;
            border: 1px solid var(--border-dark) !important;
            padding: 1.2rem !important;
            border-radius: 12px !important;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3) !important;
        }
        
        .stMetric:hover {
            box-shadow: 0 6px 24px rgba(0, 0, 0, 0.4) !important;
            transform: translateY(-3px) !important;
        }
        
        .stMetric > div {
            background-color: var(--background-card-dark) !important;
        }
        
        /* Styles spécifiques pour les métriques seulement */
        .stMetric label {
            color: #b0b0b0 !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
        }
        
        .stMetric [data-testid="metric-value"],
        .stMetric [data-testid="stMetricValue"] {
            color: #ffffff !important;
            font-weight: 800 !important;
            font-size: 2.2rem !important;
            text-shadow: 0 2px 6px rgba(0, 0, 0, 0.4) !important;
        }
        
        .stMetric [data-testid="metric-value"] div,
        .stMetric [data-testid="stMetricValue"] div {
            color: #ffffff !important;
        }
        
        .stMetric [data-testid="metric-delta"] {
            color: var(--text-light-muted) !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
        }
        
        /* Deltas colorés pour le mode sombre */
        .stMetric [data-testid="metric-delta"][title*="+"]:not([title*="-"]) {
            color: #2ecc71 !important;
            font-weight: 700 !important;
            text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3) !important;
        }
        
        .stMetric [data-testid="metric-delta"][title*="-"] {
            color: #e74c3c !important;
            font-weight: 700 !important;
            text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3) !important;
        }
        
        /* Cartes de métriques personnalisées en mode sombre */
        .metric-card {
            background-color: var(--background-card-dark) !important;
            border: 1px solid var(--border-dark) !important;
            color: var(--text-light) !important;
            border-left: 4px solid var(--primary-color-dark) !important;
        }
        
        /* Sidebar en mode sombre */
        .stSidebar {
            background: linear-gradient(180deg, #1a1d23 0%, #262730 100%) !important;
            border-right: 1px solid var(--border-dark) !important;
        }
        
        /* Contrôles de formulaire en mode sombre - SPÉCIFIQUE SIDEBAR */
        .stSidebar .stSelectbox > div > div,
        .stSidebar .stMultiSelect > div > div {
            background: var(--background-card-dark) !important;
            color: var(--text-light) !important;
            border: 1px solid var(--border-dark) !important;
        }
        
        .stSidebar .stButton > button {
            background: var(--background-card-dark) !important;
            color: var(--text-light) !important;
            border: 1px solid var(--border-dark) !important;
        }
        
        .stSidebar .stButton > button:hover {
            background: var(--primary-color-dark) !important;
            color: white !important;
            border-color: var(--primary-color-dark) !important;
        }
        
        /* Labels et texte sidebar seulement */
        .stSidebar label,
        .stSidebar .stMarkdown,
        .stSidebar p,
        .stSidebar span {
            color: var(--text-light) !important;
        }
        
        /* Alertes en mode sombre */
        .alert-warning {
            background: rgba(255, 217, 61, 0.15) !important;
            border-color: var(--warning-color-dark) !important;
            color: var(--text-light) !important;
        }
        
        .alert-success {
            background: rgba(78, 205, 196, 0.15) !important;
            border-color: var(--success-color-dark) !important;
            color: var(--text-light) !important;
        }
        
        /* STYLES FORCÉS POUR METRICS EN MODE SOMBRE - PRIORITÉ MAXIMALE */
        .stApp[style*="rgb(14, 17, 23)"] .stMetric *,
        body[style*="rgb(14, 17, 23)"] .stMetric *,
        .st-emotion-cache-13k62yr .stMetric *,
        [data-theme="dark"] .stMetric * {
            color: #ffffff !important;
        }
        
        /* Force spécifiquement les valeurs numériques en mode sombre */
        .stApp[style*="rgb(14, 17, 23)"] .stMetric [data-testid="stMetricValue"] div,
        body[style*="rgb(14, 17, 23)"] [data-testid="stMetricValue"] div,
        .st-emotion-cache-13k62yr .stMetric .st-emotion-cache-1q82h82,
        .st-emotion-cache-13k62yr .stMetric .st-emotion-cache-efbu8t div {
            color: #ffffff !important;
            font-weight: 900 !important;
            font-size: 2.4rem !important;
            text-shadow: 0 2px 6px rgba(0, 0, 0, 0.4) !important;
        }
        
        /* Labels en mode sombre */
        .stApp[style*="rgb(14, 17, 23)"] .stMetric [data-testid="stMetricLabel"],
        .st-emotion-cache-13k62yr .stMetric label {
            color: #b0b0b0 !important;
        }
    </style>
    """

def get_light_theme_css() -> str:
    """Retourne le CSS pour le thème clair (version allégée de get_main_css)"""
    return get_main_css()
