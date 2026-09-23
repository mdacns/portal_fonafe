import streamlit as st
import pandas as pd
import requests

# Configuración inicial de la página
st.set_page_config(
    page_title="Gestión de stock e inventario — Fonafe 09",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# CONTROL DE NAVEGACIÓN ESTRICTO POR SESSION_STATE
# ---------------------------------------------------------
if 'seccion_actual' not in st.session_state:
    st.session_state.seccion_actual = "Home"

def cambiar_seccion(nueva_seccion):
    st.session_state.seccion_actual = nueva_seccion
    st.rerun()

# ---------------------------------------------------------
# ESTILOS GLOBALES Y DISEÑO CORPORATIVO (CÁPSULAS Y TABLAS COMPACTAS)
# ---------------------------------------------------------
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    .custom-hero-banner {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #1e3a8a 100%);
        border-radius: 16px;
        padding: 28px 32px;
        color: #ffffff;
        box-shadow: 0 10px 25px -5px rgba(30, 27, 75, 0.3);
        margin-bottom: 25px;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .hero-title {
        font-size: 1.8rem;
        font-weight: 800;
        color: #ffffff;
        margin: 0;
        letter-spacing: -0.03em;
    }
    .hero-subtitle {
        font-size: 0.9rem;
        color: #cbd5e1;
        margin-top: 5px;
        font-weight: 400;
    }

    .custom-card {
        flex: 1;
        height: 210px !important;
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        border: 1.5px solid #cbd5e1;
        border-radius: 18px;
        box-shadow: 0 6px 12px -2px rgba(0, 0, 0, 0.05);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 24px 15px;
        cursor: pointer;
        transition: all 0.25s ease-in-out;
        text-decoration: none !important;
        color: #1e293b !important;
        font-family: 'Inter', sans-serif;
    }
    .custom-card:hover {
        border-color: #6366f1;
        box-shadow: 0 14px 28px -4px rgba(99, 102, 241, 0.2);
        transform: translateY(-5px);
        background: linear-gradient(180deg, #ffffff 0%, #f1f5f9 100%);
        color: #4f46e5 !important;
        text-decoration: none !important;
    }
    .card-icon {
        font-size: 44px !important;
        margin-bottom: 12px;
        line-height: 1;
    }
    .card-title {
        font-size: 17px !important;
        font-weight: 700;
        margin-bottom: 6px;
        text-decoration: none !important;
    }
    .card-desc {
        font-size: 13px !important;
        color: #64748b;
        text-decoration: none !important;
        line-height: 1.3;
    }

    .stSelectbox label, .stTextInput label {
        font-size: 11px !important;
        font-weight: 600 !important;
        color: #334155 !important;
    }

    .stDataFrame {
        font-size: 10px !important;
    }

    div.stButton > button {
        padding: 3px 8px !important;
        font-size: 11px !important;
        min-height: 26px !important;
        border-radius: 12px !important;
        line-height: 1.2 !important;
        margin-bottom: 2px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# CARGA Y LIMPIEZA DE DATOS (MODELO RELACIONAL POWER PIVOT)
# ---------------------------------------------------------
SHEET_ID = "1cO4HHhkYgUdZ3nzXakg860QbBSGTS79oc4ZXUhcuvVQ"
GID_STOCK = "1687656253"
GID_ENTIDADES = "2131527669"
GID_INVENTARIO = "895956054"
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwHGCi_cdedHpF5a2eqwHPXvzcBFRD7jLPg8f7oPJyn_rzc6UYg0CwbNyOYT5FoJHZx/exec"

def limpiar_dataframe_power_pivot(df):
    if df is None or df.empty:
        return pd.DataFrame()
    df = df.loc[:, ~df.columns.astype(str).str.contains('Unnamed', case=False, na=False)]
    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(how='all')
    return df

def cargar_csv_seguro(url, fallback_dict):
    try:
        df = pd.read_csv(url, header=0)
        primera_col = str(df.columns[0]).lower()
        if 'unnamed' in primera_col or any(str(c).isdigit() for c in df.columns):
            df.columns = df.iloc[0]
            df = df.iloc[1:].reset_index(drop=True)
            
        df = df.dropna(how='all').dropna(axis=1, how='all')
        df = limpiar_dataframe_power_pivot(df)
        if df.empty or len(df.columns) <= 1:
            raise Exception("CSV vacío o inválido")
        return df
    except Exception:
        fallback_df = pd.DataFrame(fallback_dict)
        return limpiar_dataframe_power_pivot(fallback_df)

# 1. Stock Almacén
if 'df_global_stock' not in st.session_state:
    url_stock = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid={GID_STOCK}"
    fallback_stock = {
        'Id Item': [1, 2, 3, 4], 'Fec. Ingreso': ['2026-01-10', '2026-01-12', '2026-02-01', '2026-02-05'],
        'Item': ['Laptop', 'Monitor', 'Docking', 'Teclado'], 'Marca': ['Lenovo', 'Dell', 'HP', 'Logitech'],
        'Part number': ['21TCS1DM00', 'DEL-24', 'HP-DC', 'K-100'], 'Tipo Item': ['Hardware', 'Periférico', 'Accesorio', 'Periférico'],
        'Descripción': ['Laptop Lenovo ThinkPad T14s Gen6 16 gb', 'Monitor 24 pulg', 'USB-C Dock', 'Kit Teclado Mouse'],
        'Serie': ['GM1C8J7K', 'SN002', 'SN003', 'SN004'], 'Entidad': ['Empresa A', 'Empresa B', 'Empresa A', 'Empresa C'],
        'Región': ['Puno', 'Arequipa', 'Lima', 'Piura'], 'Provincia': ['Puno', 'Arequipa', 'Callao', 'Piura'],
        'Distrito': ['Puno-Mariano Cornejo', 'Yanahuara', 'Bellavista', 'Castilla'], 'Tipo estado': ['Asignado', 'Disponible', 'Stock Bajo', 'Disponible'],
        'RMA': ['N/A', 'RMA-001', 'N/A', 'N/A'], 'SN CAMBIO': ['N/A', 'N/A', 'SN-CAMB-01', 'N/A'],
        'Imagen requerida': ['IMG_A.tib', 'IMG_B.tib', 'IMG_C.tib', 'IMG_C.tib'],
        'OBSERVACIONES': ['Ninguna', 'Revisado', 'Pendiente cambio', 'Ok']
    }
    st.session_state.df_global_stock = cargar_csv_seguro(url_stock, fallback_stock)

# 2. Entidades y RUC
if 'df_entidades_ruc' not in st.session_state:
    url_ent = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid={GID_ENTIDADES}"
    fallback_ent = {
        'Entidad': ['Empresa A', 'Empresa B', 'Empresa C'],
        'Razón social': ['Empresa A SAC', 'Empresa B SRL', 'Empresa C SA'],
        'RUC': ['20111111111', '20222222222', '20333333333'],
        'Dirección': ['Av. Larco 123', 'Calle Portal 456', 'Av. Colonial 789'],
        'Responsable': ['Juan Pérez', 'María Gómez', 'Carlos Ruiz'],
        'Cargo': ['Jefe TI', 'Administradora', 'Soporte'],
        'Correo': ['jperez@empresa.com', 'mgomez@empresa.com', 'cruiz@empresa.com'],
        'Celular': ['911111111', '922222222', '933333333'],
        'Horario de atención': ['08:00 - 18:00', '09:00 - 17:00', '08:30 - 17:30'],
        'Tiempo o SLA': ['4 Horas', '24 Horas', '12 Horas'],
        'Imagen requerida': ['IMG_A.tib', 'IMG_B.tib', 'IMG_C.tib']
    }
    st.session_state.df_entidades_ruc = cargar_csv_seguro(url_ent, fallback_ent)

# 3. Inventario
if 'df_inventario_sedes' not in st.session_state:
    url_inv = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid={GID_INVENTARIO}"
    fallback_inv = {
        'Entidad': ['Empresa A', 'Empresa B', 'Empresa A', 'Empresa C'],
        'Región': ['Lima', 'Arequipa', 'Lima', 'Piura'],
        'Provincia': ['Lima', 'Arequipa', 'Callao', 'Piura'],
        'Dirección': ['Av. Larco 123', 'Calle Portal 456', 'Av. Colonial 789', 'Jr. Lima 321'],
        'Modelo CPU/NB': ['ThinkPad T14', 'Latitude 5420', 'ThinkPad T14', 'ProBook 440'],
        'SN CPU/NB': ['SN12345', 'SN67890', 'SN11121', 'SN31415']
    }
    st.session_state.df_inventario_sedes = cargar_csv_seguro(url_inv, fallback_inv)

def obtener_nombre_columna(df, posibles_nombres):
    cols_lower = {c.lower().strip(): c for c in df.columns}
    for pos in posibles_nombres:
        if pos.lower().strip() in cols_lower:
            return cols_lower[pos.lower().strip()]
    return None

# ---------------------------------------------------------
# RENDERIZADO CONDICIONAL POR PANTALLA
# ---------------------------------------------------------

if st.session_state.seccion_actual == "Home":
    st.markdown("""
        <div class="custom-hero-banner">
            <div class="hero-title">Gestión de Stock e Inventario — Fonafe 09</div>
            <div class="hero-subtitle">Sistema centralizado de control de activos tecnológicos, sedes y operaciones de proyectos.</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<p style='color: #475569; font-size: 0.95rem; margin-bottom: 20px; font-weight: 600;'>Seleccione el módulo al que desea acceder:</p>", unsafe_allow_html=True)

    st.markdown("""
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-top: 10px;">
            <a href="?seccion=Inventario" target="_self" class="custom-card">
                <div class="card-icon">📦</div>
                <div class="card-title">Inventario</div>
                <div class="card-desc">Consulta cruzada y reporte por sedes</div>
            </a>
            <a href="?seccion=Stock" target="_self" class="custom-card">
                <div class="card-icon">📊</div>
                <div class="card-title">Control de stock</div>
                <div class="card-desc">Disponibilidad en almacén</div>
            </a>
            <a href="?seccion=Averias" target="_self" class="custom-card">
                <div class="card-icon">🛠️</div>
                <div class="card-title">Averías y cambios</div>
                <div class="card-desc">Incidencias y garantías</div>
            </a>
            <a href="?seccion=GeneradorGR" target="_self" class="custom-card">
                <div class="card-icon">📄</div>
                <div class="card-title">Generador GR</div>
                <div class="card-desc">Visor de guías de remisión</div>
            </a>
        </div>
    """, unsafe_allow_html=True)
    
    if 'seccion' in st.query_params:
        sec_query = st.query_params['seccion']
        if sec_query in ["Inventario", "Stock", "Averias", "GeneradorGR"]:
            st.session_state.seccion_actual = sec_query
            st.query_params.clear()
            st.rerun()

elif st.session_state.seccion_actual == "Inventario":
    # --- MÓDULO INVENTARIO MAESTRO ---
    col_h1, col_h2 = st.columns([5, 5])
    with col_h1:
        st.markdown("<p style='font-size: 1.15rem; font-weight: 700; color: #0f172a; margin: 0;'>📦 Módulo de Inventario Maestro (Modelo Relacional)</p>", unsafe_allow_html=True)
    with col_h2:
        sub_c1, sub_c2 = st.columns(2)
        with sub_c1:
            if st.button("🗑️ Limpiar", key="btn_limpiar_cols", use_container_width=True):
                st.session_state.cols_inv_maestro = []
                st.rerun()
        with sub_c2:
            if st.button("⬅️ Volver al Menú", key="btn_inv_home", use_container_width=True):
                cambiar_seccion("Home")
            
    st.markdown("<hr style='margin: 4px 0 10px 0;'>", unsafe_allow_html=True)

    df_inv = limpiar_dataframe_power_pivot(st.session_state.df_inventario_sedes.copy())
    df_ent = limpiar_dataframe_power_pivot(st.session_state.df_entidades_ruc.copy())
    df_stk = limpiar_dataframe_power_pivot(st.session_state.df_global_stock.copy())

    # Filtrar estrictamente las columnas requeridas de la pestaña de Entidades y RUC
    cols_validas_en_df = []
    for c in df_ent.columns:
        c_clean = c.strip().lower()
        if any(p.lower() == c_clean for p in ['entidad', 'empresa', 'cliente', 'razón social', 'razon social', 'ruc', 'dirección', 'direccion', 'responsable', 'cargo', 'correo', 'celular', 'horario de atención', 'horario de atencion', 'tiempo o sla', 'tiempo sla', 'imagen requerida']):
            cols_validas_en_df.append(c)
            
    if cols_validas_en_df:
        df_ent = df_ent[cols_validas_en_df]

    col_ent_inv = obtener_nombre_columna(df_inv, ['Entidad', 'Empresa', 'Cliente'])
    if not col_ent_inv and not df_inv.empty:
        col_ent_inv = df_inv.columns[0]

    col_ent_ent = obtener_nombre_columna(df_ent, ['Entidad', 'Empresa', 'Cliente'])
    if not col_ent_ent and not df_ent.empty:
        col_ent_ent = df_ent.columns[0]

    col_sn_inv = obtener_nombre_columna(df_inv, ['SN CPU/NB', 'Serie', 'Serial'])
    col_sn_stk = obtener_nombre_columna(df_stk, ['Serie', 'SN', 'Serial'])

    # CRUCE ROBUSTO CON ENTIDADES Y RUC
    if col_ent_inv and col_ent_ent:
        df_inv_temp = df_inv.copy()
        df_ent_temp = df_ent.copy()

        df_inv_temp['_key_join'] = df_inv_temp[col_ent_inv].astype(str).str.strip().str.lower()
        df_ent_temp['_key_join'] = df_ent_temp[col_ent_ent].astype(str).str.strip().str.lower()

        cols_a_traer = [c for c in df_ent_temp.columns if c not in [col_ent_ent, '_key_join'] and c not in df_inv_temp.columns]
        
        df_master = pd.merge(
            df_inv_temp, 
            df_ent_temp[['_key_join'] + cols_a_traer], 
            on='_key_join', 
            how='left'
        )
        if '_key_join' in df_master.columns:
            df_master = df_master.drop(columns=['_key_join'])
        df_master = limpiar_dataframe_power_pivot(df_master)
    else:
        df_master = df_inv.copy()

    # Cruce complementario con Stock si aplica (ACTUALIZADO CON 'Tipo estado')
    if not df_stk.empty:
        cols_stock_requeridas = []
        for c_req in ['Part number', 'Tipo Item', 'Tipo estado', 'RMA', 'SN CAMBIO', 'Imagen requerida']:
            c_encontrada = obtener_nombre_columna(df_stk, [c_req])
            if c_encontrada and c_encontrada not in cols_stock_requeridas and c_encontrada not in df_master.columns:
                cols_stock_requeridas.append(c_encontrada)
        
        if cols_stock_requeridas and col_sn_inv and col_sn_stk:
            df_stk_subset = df_stk[[col_sn_stk] + cols_stock_requeridas].copy()
            df_stk_subset = df_stk_subset.drop_duplicates(subset=[col_sn_stk])
            
            df_master = pd.merge(
                df_master,
                df_stk_subset,
                left_on=col_sn_inv,
                right_on=col_sn_stk,
                how='left',
                suffixes=('', '_stock')
            )
            df_master = limpiar_dataframe_power_pivot(df_master)
            df_master = df_master.loc[:, ~df_master.columns.str.endswith('_stock')]

    df_master = limpiar_dataframe_power_pivot(df_master)
    df_master = df_master.loc[:, ~df_master.columns.duplicated()]

    for col in df_master.columns:
        df_master[col] = df_master[col].astype(str).str.strip().replace(['nan', 'None', 'NAT', 'nan'], '')

    c_ent = obtener_nombre_columna(df_master, ['Entidad', 'Empresa'])
    c_reg = obtener_nombre_columna(df_master, ['Región', 'Region'])
    c_prov = obtener_nombre_columna(df_master, ['Provincia'])
    c_dist = obtener_nombre_columna(df_master, ['Distrito'])

    st.markdown("<p style='font-size: 11px; font-weight: 700; color: #475569; margin-bottom: 4px;'>Filtros en Cascada (Modelo de Datos)</p>", unsafe_allow_html=True)
    
    f1, f2, f3, f4 = st.columns(4)
    
    with f1:
        if c_ent:
            entidades_disp = ["Todas"] + sorted([str(x) for x in df_master[c_ent].dropna().unique() if str(x) != ''])
            sel_entidad = st.selectbox("1. Entidad", entidades_disp, key="cascada_entidad")
            if sel_entidad != "Todas":
                df_master = df_master[df_master[c_ent] == sel_entidad]
        else:
            st.selectbox("1. Entidad", ["No disponible"], key="cascada_entidad_na")

    with f2:
        if c_reg:
            regiones_disp = ["Todas"] + sorted([str(x) for x in df_master[c_reg].dropna().unique() if str(x) != ''])
            sel_region = st.selectbox("2. Región", regiones_disp, key="cascada_region")
            if sel_region != "Todas":
                df_master = df_master[df_master[c_reg] == sel_region]
        else:
            st.selectbox("2. Región", ["No disponible"], key="cascada_region_na")

    with f3:
        if c_prov:
            provincias_disp = ["Todas"] + sorted([str(x) for x in df_master[c_prov].dropna().unique() if str(x) != ''])
            sel_provincia = st.selectbox("3. Provincia", provincias_disp, key="cascada_provincia")
            if sel_provincia != "Todas":
                df_master = df_master[df_master[c_prov] == sel_provincia]
        else:
            st.selectbox("3. Provincia", ["No disponible"], key="cascada_provincia_na")

    with f4:
        if c_dist:
            distritos_disp = ["Todas"] + sorted([str(x) for x in df_master[c_dist].dropna().unique() if str(x) != ''])
            sel_distrito = st.selectbox("4. Distrito", distritos_disp, key="cascada_distrito")
            if sel_distrito != "Todas":
                df_master = df_master[df_master[c_dist] == sel_distrito]
        else:
            st.selectbox("4. Distrito", ["No disponible"], key="cascada_distrito_na")

    st.markdown("<hr style='margin: 8px 0;'>", unsafe_allow_html=True)

    todas_columnas = [c for c in df_master.columns.tolist() if c.lower() not in ['serie', 'marca']]
    
    if 'cols_inv_maestro' not in st.session_state:
        st.session_state.cols_inv_maestro = []

    st.markdown("<p style='font-size: 11px; font-weight: 700; color: #475569; margin-bottom: 6px;'>Seleccione las columnas a mostrar (Cápsulas compactas):</p>", unsafe_allow_html=True)

    cols_chips = st.columns(min(len(todas_columnas), 6))
    
    for i, col_name in enumerate(todas_columnas):
        col_actual = cols_chips[i % len(cols_chips)]
        with col_actual:
            is_active = col_name in st.session_state.cols_inv_maestro
            label_chip = f"✓ {col_name}" if is_active else f"+ {col_name}"
            
            if st.button(label_chip, key=f"chip_{col_name}", use_container_width=True):
                if is_active:
                    st.session_state.cols_inv_maestro.remove(col_name)
                else:
                    st.session_state.cols_inv_maestro.append(col_name)
                st.rerun()

    st.markdown("---")

    if not st.session_state.cols_inv_maestro:
        st.info("ℹ️ Aún no ha seleccionado ninguna columna. Por favor, haga clic en las cápsulas superiores para elegir las columnas que desea visualizar.")
    elif df_master.empty:
        st.info("ℹ️ No hay registros coincidentes con los filtros seleccionados.")
    else:
        df_final_mostrar = df_master[st.session_state.cols_inv_maestro].copy()
        df_final_mostrar.columns = [str(c).strip() for c in df_final_mostrar.columns]
        
        if not df_final_mostrar.empty and str(df_final_mostrar.iloc[0, 0]).strip() == str(df_final_mostrar.columns[0]).strip():
            df_final_mostrar = df_final_mostrar.iloc[1:]

        df_final_mostrar.reset_index(drop=True, inplace=True)

        st.markdown(f"<p style='font-size: 11px; color: #64748b; font-weight: 500; margin-bottom: 6px;'>Mostrando <b>{len(df_final_mostrar)}</b> registros coincidentes y <b>{len(st.session_state.cols_inv_maestro)}</b> columnas seleccionadas.</p>", unsafe_allow_html=True)
        
        st.dataframe(df_final_mostrar, use_container_width=True, height=380)

elif st.session_state.seccion_actual == "Stock":
    # --- MÓDULO 2: CONTROL DE STOCK ---
    col_h1, col_h2 = st.columns([7, 3])
    with col_h1:
        st.markdown("<p style='font-size: 1.15rem; font-weight: 700; color: #0f172a; margin: 0;'>📊 Control de Stock e Inventario General</p>", unsafe_allow_html=True)
    with col_h2:
        if st.button("⬅️ Volver al Menú Principal", key="btn_volver_stock"):
            cambiar_seccion("Home")
            
    st.markdown("<hr style='margin: 4px 0 10px 0;'>", unsafe_allow_html=True)

    df_stock = limpiar_dataframe_power_pivot(st.session_state.df_global_stock)

    if df_stock.empty:
        st.info("ℹ️ No se pudieron recuperar registros de stock.")
    else:
        df_f = df_stock.copy()
        for col in df_f.columns:
            df_f[col] = df_f[col].astype(str).str.strip().replace(['nan', 'None', 'NAT', 'nan'], '')

        with st.expander("🔍 Filtros avanzados", expanded=True):
            fc1, fc2, fc3 = st.columns(3)
            
            with fc1:
                entidades_stk = ["Todas"] + sorted([str(x) for x in df_f['Entidad'].dropna().unique() if str(x).strip() != '' and str(x).lower() != 'nan'])
                sel_ent_stk = st.selectbox("1. Entidad", entidades_stk, key="filtro_ent_stk")

                regiones_stk = ["Todas"] + sorted([str(x) for x in df_f['Región'].dropna().unique() if str(x).strip() != '' and str(x).lower() != 'nan'])
                sel_reg_stk = st.selectbox("2. Región", regiones_stk, key="filtro_reg_stk")

                provincias_stk = ["Todas"] + sorted([str(x) for x in df_f['Provincia'].dropna().unique() if str(x).strip() != '' and str(x).lower() != 'nan'])
                sel_prov_stk = st.selectbox("3. Provincia", provincias_stk, key="filtro_prov_stk")

            with fc2:
                distritos_stk = ["Todas"] + sorted([str(x) for x in df_f['Distrito'].dropna().unique() if str(x).strip() != '' and str(x).lower() != 'nan'])
                sel_dist_stk = st.selectbox("4. Distrito", distritos_stk, key="filtro_dist_stk")

                tipos_item = ["Todos"] + sorted([str(x) for x in df_f['Tipo Item'].dropna().unique() if str(x).strip() != '' and str(x).lower() != 'nan'])
                sel_tipo_item = st.selectbox("5. Tipo item", tipos_item, key="filtro_tipo_item")

                part_numbers = ["Todos"] + sorted([str(x) for x in df_f['Part number'].dropna().unique() if str(x).strip() != '' and str(x).lower() != 'nan'])
                sel_pn = st.selectbox("6. Part number", part_numbers, key="filtro_pn")

            with fc3:
                estados_stk = ["Todos"] + sorted([str(x) for x in df_f['Tipo estado'].dropna().unique() if str(x).strip() != '' and str(x).lower() != 'nan'])
                sel_estado = st.selectbox("7. Tipo estado", estados_stk, key="filtro_estado")

                sn_cambios = ["Todos"] + sorted([str(x) for x in df_f['SN CAMBIO'].dropna().unique() if str(x).strip() != '' and str(x).lower() != 'nan'])
                sel_sn_cambio = st.selectbox("8. SN CAMBIO", sn_cambios, key="filtro_sn_cambio")

                filtro_obs = st.text_input("9. OBSERVACIONES (Texto)", "", key="filtro_obs_text")

        if sel_ent_stk != "Todas":
            df_f = df_f[df_f['Entidad'] == sel_ent_stk]
        if sel_reg_stk != "Todas":
            df_f = df_f[df_f['Región'] == sel_reg_stk]
        if sel_prov_stk != "Todas":
            df_f = df_f[df_f['Provincia'] == sel_prov_stk]
        if sel_dist_stk != "Todas":
            df_f = df_f[df_f['Distrito'] == sel_dist_stk]
        if sel_tipo_item != "Todos":
            df_f = df_f[df_f['Tipo Item'] == sel_tipo_item]
        if sel_pn != "Todos":
            df_f = df_f[df_f['Part number'] == sel_pn]
        if sel_estado != "Todos":
            df_f = df_f[df_f['Tipo estado'] == sel_estado]
        if sel_sn_cambio != "Todos":
            df_f = df_f[df_f['SN CAMBIO'] == sel_sn_cambio]
        if filtro_obs:
            df_f = df_f[df_f['OBSERVACIONES'].str.contains(filtro_obs, case=False, na=False)]

        cols_todas = df_stock.columns.tolist()

        if 'stock_cols_ocultas' not in st.session_state:
            st.session_state.stock_cols_ocultas = []

        with st.expander("⚙️ Personalizar columnas visibles", expanded=False):
            exp_cols = st.columns(4)
            for i, col_name in enumerate(cols_todas):
                with exp_cols[i % 4]:
                    ocultar = st.checkbox(f"{col_name}", value=col_name not in st.session_state.stock_cols_ocultas, key=f"stock_show_{col_name}")
                    if not ocultar and col_name not in st.session_state.stock_cols_ocultas:
                        st.session_state.stock_cols_ocultas.append(col_name)
                    elif ocultar and col_name in st.session_state.stock_cols_ocultas:
                        st.session_state.stock_cols_ocultas.remove(col_name)

        cols_visibles = [c for c in cols_todas if c not in st.session_state.stock_cols_ocultas]

        st.markdown("---")

        if not cols_visibles:
            st.info("ℹ️ Has ocultado todas las columnas. Por favor marca al menos una.")
        elif df_f.empty:
            st.info("ℹ️ No se encontraron registros con la combinación de filtros seleccionados.")
        else:
            df_stock_final = df_f[cols_visibles].copy()
            df_stock_final.columns = [str(c).strip() for c in df_stock_final.columns]
            df_stock_final.reset_index(drop=True, inplace=True)

            st.markdown(f"<p style='font-size: 11px; color: #64748b; font-weight: 500; margin-bottom: 6px;'>Mostrando <b>{len(df_f)}</b> registros filtrados y <b>{len(cols_visibles)}</b> columnas activas.</p>", unsafe_allow_html=True)
            st.dataframe(df_stock_final, use_container_width=True, height=380)

elif st.session_state.seccion_actual == "Averias":
    # --- MÓDULO 3: AVERÍAS Y CAMBIOS ---
    col_h1, col_h2 = st.columns([7, 3])
    with col_h1:
        st.markdown("<p style='font-size: 1.15rem; font-weight: 700; color: #0f172a; margin: 0;'>🛠️ Gestión de averías y cambios</p>", unsafe_allow_html=True)
    with col_h2:
        if st.button("⬅️ Volver al Menú Principal", key="btn_av_home"):
            cambiar_seccion("Home")
            
    st.markdown("<hr style='margin: 4px 0 10px 0;'>", unsafe_allow_html=True)

    df_averias = limpiar_dataframe_power_pivot(st.session_state.df_global_stock)

    c_input, c_vacio = st.columns([2, 5])
    with c_input:
        serie_a_validar = st.text_input(
            "Validar equipo por número de serie", 
            max_chars=15, 
            placeholder="Ingrese serie a validar", 
            key="input_serie_validar",
            label_visibility="collapsed"
        )

    if 'mensaje_exito_cambio' in st.session_state and st.session_state.mensaje_exito_cambio:
        st.success(st.session_state.mensaje_exito_cambio)
        st.session_state.mensaje_exito_cambio = None

    if serie_a_validar:
        if df_averias.empty:
            st.info("ℹ️ No hay datos cargados para realizar la validación.")
        else:
            df_averias['Serie_clean'] = df_averias['Serie'].astype(str).str.strip()
            busqueda_clean = serie_a_validar.strip()

            match_df = df_averias[df_averias['Serie_clean'].str.lower() == busqueda_clean.lower()]

            if not match_df.empty:
                st.info(f"ℹ️ Se encontró coincidencia para la serie: **{serie_a_validar}**")
                
                campos_deseados = [
                    'Part number', 'Tipo Item', 'Descripción', 'Serie', 
                    'Entidad', 'Región', 'Provincia', 'Distrito', 'Tipo estado', 'SN CAMBIO', 'Imagen requerida'
                ]
                
                campos_disponibles = [c for c in campos_deseados if c in match_df.columns]
                df_resultado = match_df[campos_disponibles].head(1)

                st.dataframe(df_resultado, use_container_width=True, hide_index=True)

                st.markdown("<hr style='margin: 2px 0 6px 0;'>", unsafe_allow_html=True)
                st.markdown("<p style='font-weight: 600; color: #1e293b; margin-bottom: 2px;'>¿Deseas cambiar el equipo?</p>", unsafe_allow_html=True)
                
                opcion_cambio = st.radio(
                    "Seleccione una opción de respaldo",
                    options=["Backup despliegue", "Backup incidencias"],
                    index=None,
                    key="radio_cambio_equipo",
                    label_visibility="collapsed",
                    horizontal=True
                )

                if opcion_cambio:
                    part_number_buscado = str(match_df['Part number'].values[0]).strip()
                    
                    df_averias['Part_number_clean'] = df_averias['Part number'].astype(str).str.strip()
                    df_averias['Entidad_clean'] = df_averias['Entidad'].astype(str).str.strip()
                    
                    df_filtrado_backup = df_averias[
                        (df_averias['Part_number_clean'].str.lower() == part_number_buscado.lower()) &
                        (df_averias['Entidad_clean'].str.lower() == opcion_cambio.lower())
                    ]
                    
                    st.info("Mostrando stock de respaldo")
                    
                    if not df_filtrado_backup.empty:
                        campos_respaldo = [
                            'Part number', 'Tipo Item', 'Descripción', 'Serie', 
                            'Entidad', 'Región', 'Provincia', 'Distrito', 'Tipo estado', 'RMA', 'SN CAMBIO', 'Imagen requerida'
                        ]
                        campos_respaldo_disp = [c for c in campos_respaldo if c in df_filtrado_backup.columns]
                        
                        df_res_backup = df_filtrado_backup[campos_respaldo_disp].copy()
                        df_res_backup.insert(0, 'Seleccionar', False)
                        
                        edited_backup_df = st.data_editor(
                            df_res_backup,
                            use_container_width=True,
                            hide_index=True,
                            key="editor_tabla_backup",
                            column_config={
                                "Seleccionar": st.column_config.CheckboxColumn("Seleccionar", required=True)
                            }
                        )
                        
                        filas_seleccionadas = edited_backup_df[edited_backup_df['Seleccionar'] == True]
                        
                        if not filas_seleccionadas.empty:
                            serie_seleccionada = str(filas_seleccionadas.iloc[0]['Serie'])
                            
                            if st.button("🚀 Proceder con el cambio", key="btn_proceder_cambio"):
                                idx_buscado = match_df.index[0]
                                st.session_state.df_global_stock.loc[idx_buscado, 'Tipo estado'] = 'Averiado'
                                st.session_state.df_global_stock.loc[idx_buscado, 'SN CAMBIO'] = serie_seleccionada
                                
                                idx_seleccionado = df_averias[df_averias['Serie'].astype(str).str.strip() == serie_seleccionada].index[0]
                                st.session_state.df_global_stock.loc[idx_seleccionado, 'Entidad'] = match_df.iloc[0]['Entidad']
                                st.session_state.df_global_stock.loc[idx_seleccionado, 'Región'] = match_df.iloc[0]['Región']
                                st.session_state.df_global_stock.loc[idx_seleccionado, 'Provincia'] = match_df.iloc[0]['Provincia']
                                st.session_state.df_global_stock.loc[idx_seleccionado, 'Distrito'] = match_df.iloc[0]['Distrito']
                                st.session_state.df_global_stock.loc[idx_seleccionado, 'Tipo estado'] = 'Asignado'
                                
                                payload = {
                                    "accion": "ejecutar_reemplazo",
                                    "serie_afectada": serie_a_validar,
                                    "serie_nueva": serie_seleccionada,
                                    "val_k": str(match_df.iloc[0].get('Entidad', '')),
                                    "val_l": str(match_df.iloc[0].get('Región', '')),
                                    "val_m": str(match_df.iloc[0].get('Provincia', '')),
                                    "val_n": str(match_df.iloc[0].get('Distrito', ''))
                                }
                                
                                try:
                                    response = requests.post(APPS_SCRIPT_URL, json=payload, timeout=30)
                                    res_json = response.json()
                                    if res_json.get("status") == "success":
                                        st.session_state.mensaje_exito_cambio = "Cambio realizado"
                                    else:
                                        st.session_state.mensaje_exito_cambio = f"⚠️ Se actualizó localmente, pero Apps Script reportó un error: {res_json.get('message')}"
                                except requests.exceptions.Timeout:
                                    st.session_state.mensaje_exito_cambio = "Cambio realizado"
                                except Exception as err:
                                    st.session_state.mensaje_exito_cambio = f"⚠️ Se actualizó localmente, pero falló la conexión con Apps Script: {err}"
                                
                                st.rerun()
                    else:
                        st.info(f"ℹ️ No se encontraron registros con Part Number **{part_number_buscado}** y Entidad **{opcion_cambio}**.")
            else:
                st.info(f"ℹ️ No se encontró ningún registro asociado a la serie **'{serie_a_validar}'** en el sistema.")

elif st.session_state.seccion_actual == "GeneradorGR":
    # --- MÓDULO 4: GENERADOR GR ---
    col_h1, col_h2 = st.columns([7, 3])
    with col_h1:
        st.markdown("<p style='font-size: 1.15rem; font-weight: 700; color: #0f172a; margin: 0;'>📄 Generador GR — Visor y Editor de Hoja de Cálculo</p>", unsafe_allow_html=True)
    with col_h2:
        if st.button("⬅️ Volver al Menú Principal", key="btn_gr_home"):
            cambiar_seccion("Home")
            
    st.markdown("<hr style='margin: 4px 0 10px 0;'>", unsafe_allow_html=True)
    
    sheet_url = "https://docs.google.com/spreadsheets/d/15j0BzgH5jIXuKUjo25nxdDoAKrcI1GHA9pLH8gUe6ws/edit?gid=0#gid=0"
    embed_url = sheet_url.replace("/edit?gid=0#gid=0", "/edit?embedded=true&gid=0")
    if "embedded=true" not in embed_url:
        embed_url = sheet_url + ("&" if "?" in sheet_url else "?") + "embedded=true"

    st.markdown(
        f"""
        <iframe src="{embed_url}" width="100%" height="520px" style="border:none; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);"></iframe>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    col_b1, col_b2 = st.columns([1, 1])
    with col_b1:
        if st.button("🔄 Actualizar visor"):
            st.rerun()
    with col_b2:
        st.markdown(f"<div style='text-align: right;'><a href='{sheet_url}' target='_blank'>Abrir en Google Sheets a pantalla completa ↗</a></div>", unsafe_allow_html=True)
