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
            --text-dark: #2c3e50;
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
        }
        
        .stSidebar .stExpander:hover {
            border-color: var(--primary-color);
            box-shadow: var(--shadow-hover);
            transform: translateY(-2px);
        }
        
        .stSidebar .stExpander summary {
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
            background-color: var(--background-white);
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid #e9ecef;
            box-shadow: var(--shadow);
            transition: var(--transition);
        }
        
        .stMetric:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-hover);
        }
        
        .stMetric > div {
            color: var(--text-dark);
            background-color: var(--background-white);
        }
        
        .stMetric label {
            color: var(--text-muted);
            font-weight: 500;
        }
        
        .stMetric [data-testid="metric-value"] {
            color: var(--text-dark);
            font-weight: 600;
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
    </style>
    """

def get_dark_theme_css() -> str:
    """Retourne le CSS pour le thème sombre (simplifié)"""
    return """
    <style>
        .stApp {
            background-color: #0E1117;
            color: white;
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
        
        .stMetric {
            background-color: #262730;
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid #404040;
        }
    </style>
    """

def get_light_theme_css() -> str:
    """Retourne le CSS pour le thème clair (version allégée de get_main_css)"""
    return get_main_css()
