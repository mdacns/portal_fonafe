import streamlit as st
import pandas as pd
import requests
import json

# ==========================================
# CONFIGURACIÓN GENERAL Y DISEÑO EXPANDIDO
# ==========================================
st.set_page_config(
    page_title="Portal de Servicios - FONAFE 09",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS PERSONALIZADO ---
st.markdown("""
    <style>
    header {visibility: hidden !important; height: 0px !important;}
    footer {visibility: hidden !important;}
    
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 100% !important;
    }
    
    .contenedor-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-end;
        margin-bottom: 0px !important;
    }
    .izq-header {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    .icono-header {
        font-size: 2.5rem;
        line-height: 1;
    }
    .titulo-principal {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        color: #0f172a;
        line-height: 1.1;
        margin: 0 !important;
        letter-spacing: -0.03em;
    }
    .subtitulo-principal {
        font-size: 1.05rem !important;
        font-weight: 500 !important;
        color: #64748b;
        margin-top: 4px !important;
        margin-bottom: 0 !important;
        letter-spacing: 0.01em;
    }
    .texto-selector-alineado {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e293b;
        text-align: right;
        margin-bottom: 2px;
    }

    hr {
        margin-top: 1rem !important;
        margin-bottom: 1.5rem !important;
    }

    .card-link {
        text-decoration: none !important;
        display: block;
    }
    .card-container {
        background-color: #ffffff;
        border: 2px solid #cbd5e1;
        border-radius: 20px;
        height: 175px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        transition: all 0.25s ease-in-out;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04);
    }

    .card-inv:hover { background-color: #d1fae5 !important; border-color: #10b981 !important; transform: translateY(-4px); box-shadow: 0 12px 20px -3px rgba(16, 185, 129, 0.2); }
    .card-stock:hover { background-color: #ffedd5 !important; border-color: #f97316 !important; transform: translateY(-4px); box-shadow: 0 12px 20px -3px rgba(249, 115, 22, 0.2); }
    .card-cambios:hover { background-color: #dbeafe !important; border-color: #3b82f6 !important; transform: translateY(-4px); box-shadow: 0 12px 20px -3px rgba(59, 130, 246, 0.2); }
    .card-gr:hover { background-color: #ede9fe !important; border-color: #8b5cf6 !important; transform: translateY(-4px); box-shadow: 0 12px 20px -3px rgba(139, 92, 246, 0.2); }
    .card-dash:hover { background-color: #fce7f3 !important; border-color: #db2777 !important; transform: translateY(-4px); box-shadow: 0 12px 20px -3px rgba(219, 39, 119, 0.2); }
    .card-entidades:hover { background-color: #cffafe !important; border-color: #0e7490 !important; transform: translateY(-4px); box-shadow: 0 12px 20px -3px rgba(14, 116, 144, 0.2); }

    .icon-box {
        width: 60px;
        height: 60px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 30px;
        margin-bottom: 12px;
    }

    .card-text {
        font-size: 16px;
        font-weight: 700;
        color: #1e293b;
        text-align: center;
        margin: 0;
    }

    .enlace-volver {
        text-align: right;
        font-size: 14px;
        font-weight: 600;
        padding-top: 5px;
    }
    .enlace-volver a {
        color: #2563eb;
        text-decoration: none;
    }
    .enlace-volver a:hover {
        color: #1d4ed8;
        text-decoration: underline;
    }

    .asset-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #3b82f6;
        border-radius: 10px;
        padding: 10px 14px;
        box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        margin-top: 10px;
        margin-bottom: 8px;
    }
    .asset-header {
        font-size: 0.95rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .field-label {
        font-size: 0.68rem;
        text-transform: uppercase;
        font-weight: 700;
        color: #64748b;
        letter-spacing: 0.04em;
        margin-bottom: 1px;
    }
    .field-value {
        font-size: 0.83rem;
        font-weight: 600;
        color: #0f172a;
        background: #f8fafc;
        padding: 4px 8px;
        border-radius: 5px;
        border: 1px solid #e2e8f0;
        margin-bottom: 6px;
        word-break: break-word;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# CONFIGURACIÓN DE IDs DE GOOGLE SHEETS
# ==========================================
ID_HOJA = "1cO4HHhkYgUdZ3nzXakg860QbBSGTS79oc4ZXUhcuvVQ"
GID_INVENTARIO = "895956054"       
GID_CONTROL_STOCK = "1687656253" 
GID_ENTIDADES = "2131527669"  

ID_HOJA_GR = "15j0BzgH5jIXuKUjo25nxdDoAKrcI1GHA9pLH8gUe6ws" 

WEB_APP_URL = "https://script.google.com/macros/s/AKfycbw5ydQRJtR1fk1R7RgXobSBmp0QXT7zvnxCoC3M-xdK9kjPeQZlHpSxNtbMyF6ACxjv/exec"

# Manejo de estado de navegación
if 'seccion_activa' not in st.session_state:
    st.session_state.seccion_activa = None  

params = st.query_params
if "seccion" in params:
    st.session_state.seccion_activa = params["seccion"]
elif "volver" in params:
    st.session_state.seccion_activa = None
    st.query_params.clear()
    st.rerun()

# ==========================================
# VISTA PRINCIPAL (MENÚ DE TARJETAS)
# ==========================================
if st.session_state.seccion_activa is None:
    st.markdown("""
        <div class="contenedor-header">
            <div class="izq-header">
                <div class="icono-header">🌐</div>
                <div>
                    <p class="titulo-principal">Portal de Servicios - FONAFE 09</p>
                    <p class="subtitulo-principal">Plataforma de Control de Activos e Inventario</p>
                </div>
            </div>
            <div class="texto-selector-alineado">
                Seleccione el Módulo de Gestión:
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    
    with c1:
        st.markdown("""
            <a href="?seccion=Inventario" target="_self" class="card-link">
                <div class="card-container card-inv">
                    <div class="icon-box" style="background-color: #d1fae5;">📦</div>
                    <p class="card-text">Inventario</p>
                </div>
            </a>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown("""
            <a href="?seccion=Control Stock" target="_self" class="card-link">
                <div class="card-container card-stock">
                    <div class="icon-box" style="background-color: #ffedd5;">📋</div>
                    <p class="card-text">Control Stock</p>
                </div>
            </a>
        """, unsafe_allow_html=True)
        
    with c3:
        st.markdown("""
            <a href="?seccion=Gestión Cambios" target="_self" class="card-link">
                <div class="card-container card-cambios">
                    <div class="icon-box" style="background-color: #dbeafe;">🔄</div>
                    <p class="card-text">Gestión Cambios</p>
                </div>
            </a>
        """, unsafe_allow_html=True)
        
    with c4:
        st.markdown("""
            <a href="?seccion=Generador GR" target="_self" class="card-link">
                <div class="card-container card-gr">
                    <div class="icon-box" style="background-color: #ede9fe;">📄</div>
                    <p class="card-text">Generador GR</p>
                </div>
            </a>
        """, unsafe_allow_html=True)
        
    with c5:
        st.markdown("""
            <a href="?seccion=Dashboard" target="_self" class="card-link">
                <div class="card-container card-dash">
                    <div class="icon-box" style="background-color: #fce7f3;">📊</div>
                    <p class="card-text">Dashboard</p>
                </div>
            </a>
        """, unsafe_allow_html=True)

    with c6:
        st.markdown("""
            <a href="?seccion=Entidades y RUC" target="_self" class="card-link">
                <div class="card-container card-entidades">
                    <div class="icon-box" style="background-color: #cffafe;">🏢</div>
                    <p class="card-text">Entidades y RUC</p>
                </div>
            </a>
        """, unsafe_allow_html=True)

else:
    col_tit, col_link = st.columns([3, 1])
    
    with col_tit:
        if st.session_state.seccion_activa == "Inventario":
            st.subheader("📦 Módulo de Inventario")
        elif st.session_state.seccion_activa == "Control Stock":
            st.subheader("📋 Módulo de Control de Stock")
        elif st.session_state.seccion_activa == "Gestión Cambios":
            st.subheader("🔄 Módulo de Gestión de Cambios")
        elif st.session_state.seccion_activa == "Generador GR":
            st.subheader("📄 Generador de Guías de Remisión (GR)")
        elif st.session_state.seccion_activa == "Dashboard":
            st.subheader("📊 Dashboard de Indicadores")
        elif st.session_state.seccion_activa == "Entidades y RUC":
            st.subheader("🏢 Directorio de Entidades y RUC")

    with col_link:
        st.markdown('<div class="enlace-volver"><a href="?volver=true" target="_self">Volver a inicio ⬅️</a></div>', unsafe_allow_html=True)

    st.markdown("---")

    # ==========================================
    # 1. MÓDULO INVENTARIO
    # ==========================================
    if st.session_state.seccion_activa == "Inventario":
        url_csv = f"https://docs.google.com/spreadsheets/d/{ID_HOJA}/export?format=csv&gid={GID_INVENTARIO}"
        try:
            with st.spinner("📥 Sincronizando datos de Inventario..."):
                df = pd.read_csv(url_csv, header=6)
                df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
                
            if not df.empty:
                col_cpu_real = 'Modelo CPU/N' if 'Modelo CPU/N' in df.columns else ('Modelo CPU/NB' if 'Modelo CPU/NB' in df.columns else None)
                
                with st.expander("🔍 Panel de Búsqueda y Filtros en Cascada", expanded=True):
                    col_b1, col_b2 = st.columns([1, 1])
                    with col_b1:
                        buscado = st.text_input("🔍 Búsqueda general:", placeholder="Ej: Serie, código, usuario...")
                    
                    st.markdown("---")
                    df_c = df.copy()
                    col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns(5)
                    
                    with col_f1:
                        opt_entidad = ["Todos"] + sorted(list(df_c['Entidad'].dropna().unique())) if 'Entidad' in df_c.columns else ["Todos"]
                        f_entidad = st.selectbox("🏢 Entidad", opt_entidad)
                    if f_entidad != "Todos" and 'Entidad' in df_c.columns:
                        df_c = df_c[df_c['Entidad'] == f_entidad]
                        
                    with col_f2:
                        opt_region = ["Todos"] + sorted(list(df_c['Región'].dropna().unique())) if 'Región' in df_c.columns else ["Todos"]
                        f_region = st.selectbox("🗺️ Región", opt_region)
                    if f_region != "Todos" and 'Región' in df_c.columns:
                        df_c = df_c[df_c['Región'] == f_region]
                        
                    with col_f3:
                        opt_provincia = ["Todos"] + sorted(list(df_c['Provincia'].dropna().unique())) if 'Provincia' in df_c.columns else ["Todos"]
                        f_provincia = st.selectbox("📍 Provincia", opt_provincia)
                    if f_provincia != "Todos" and 'Provincia' in df_c.columns:
                        df_c = df_c[df_c['Provincia'] == f_provincia]
                        
                    with col_f4:
                        opt_distrito = ["Todos"] + sorted(list(df_c['Distrito/sede'].dropna().unique())) if 'Distrito/sede' in df_c.columns else ["Todos"]
                        f_distrito = st.selectbox("🏢 Distrito/sede", opt_distrito)
                    if f_distrito != "Todos" and 'Distrito/sede' in df_c.columns:
                        df_c = df_c[df_c['Distrito/sede'] == f_distrito]

                    with col_f5:
                        opt_cpu = ["Todos"] + sorted(list(df_c[col_cpu_real].dropna().unique())) if col_cpu_real else ["Todos"]
                        f_cpu = st.selectbox("💻 Modelo CPU/NB", opt_cpu)

                df_filtrado = df.copy()
                if buscado:
                    df_filtrado = df_filtrado[df_filtrado.astype(str).apply(lambda x: x.str.contains(buscado, case=False)).any(axis=1)]
                if f_entidad != "Todos" and 'Entidad' in df_filtrado.columns:
                    df_filtrado = df_filtrado[df_filtrado['Entidad'] == f_entidad]
                if f_region != "Todos" and 'Región' in df_filtrado.columns:
                    df_filtrado = df_filtrado[df_filtrado['Región'] == f_region]
                if f_provincia != "Todos" and 'Provincia' in df_filtrado.columns:
                    df_filtrado = df_filtrado[df_filtrado['Provincia'] == f_provincia]
                if f_distrito != "Todos" and 'Distrito/sede' in df_filtrado.columns:
                    df_filtrado = df_filtrado[df_filtrado['Distrito/sede'] == f_distrito]
                if f_cpu != "Todos" and col_cpu_real:
                    df_filtrado = df_filtrado[df_filtrado[col_cpu_real] == f_cpu]

                st.info(f"📊 Mostrando **{len(df_filtrado)}** registros coincidentes (de un total de {len(df)}).")
                df_estilizado = df_filtrado.style.set_table_styles([
                    {'selector': 'th', 'props': [('background-color', '#1e293b'), ('color', '#ffffff'), ('font-size', '13px'), ('font-weight', 'bold'), ('text-align', 'center')]}
                ]).hide(axis="index")
                st.dataframe(df_estilizado, use_container_width=True, height=450)
            else:
                st.warning("La pestaña se leyó pero no se encontraron datos.")
        except Exception as e:
            st.error("⚠️ No se pudo leer la pestaña de Google Sheets.")
            with st.expander("Ver detalles técnicos"):
                st.write(e)

    # ==========================================
    # 2. MÓDULO CONTROL STOCK
    # ==========================================
    elif st.session_state.seccion_activa == "Control Stock":
        url_csv = f"https://docs.google.com/spreadsheets/d/{ID_HOJA}/export?format=csv&gid={GID_CONTROL_STOCK}"
        try:
            with st.spinner("📥 Sincronizando datos de Stock..."):
                df = pd.read_csv(url_csv, header=0) 
                df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
                
            if not df.empty:
                c_pn = 'PN' if 'PN' in df.columns else None
                c_tipo = 'Tipo' if 'Tipo' in df.columns else None
                c_desc = 'Descripción' if 'Descripción' in df.columns else ('Descripcion' if 'Descripcion' in df.columns else None)
                c_est_ent = 'Estado/Entidad' if 'Estado/Entidad' in df.columns else None
                c_reg = 'Región' if 'Región' in df.columns else ('Region' if 'Region' in df.columns else None)
                c_prov = 'Provincia' if 'Provincia' in df.columns else None
                c_dist = 'Distrito' if 'Distrito' in df.columns else ('Distrito/sede' if 'Distrito/sede' in df.columns else None)
                c_tstock = 'Tipo stock' if 'Tipo stock' in df.columns else ('Tipo Stock' if 'Tipo Stock' in df.columns else None)

                with st.expander("🔍 Panel de Búsqueda y Filtros en Cascada (Control Stock)", expanded=True):
                    col_b1, col_b2 = st.columns([1, 1])
                    with col_b1:
                        buscado = st.text_input("🔍 Búsqueda general:", placeholder="Escriba para buscar en cualquier columna...")
                    
                    st.markdown("---")
                    df_cs = df.copy()
                    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                    
                    with col_s1:
                        opt_pn = ["Todos"] + sorted(list(df_cs[c_pn].dropna().unique())) if c_pn else ["Todos"]
                        f_pn = st.selectbox("🏷️ PN", opt_pn)
                    if f_pn != "Todos" and c_pn:
                        df_cs = df_cs[df_cs[c_pn] == f_pn]
                        
                    with col_s2:
                        opt_tipo = ["Todos"] + sorted(list(df_cs[c_tipo].dropna().unique())) if c_tipo else ["Todos"]
                        f_tipo = st.selectbox("📂 Tipo", opt_tipo)
                    if f_tipo != "Todos" and c_tipo:
                        df_cs = df_cs[df_cs[c_tipo] == f_tipo]
                        
                    with col_s3:
                        opt_desc = ["Todos"] + sorted(list(df_cs[c_desc].dropna().unique())) if c_desc else ["Todos"]
                        f_desc = st.selectbox("📝 Descripción", opt_desc)
                    if f_desc != "Todos" and c_desc:
                        df_cs = df_cs[df_cs[c_desc] == f_desc]
                        
                    with col_s4:
                        opt_est_ent = ["Todos"] + sorted(list(df_cs[c_est_ent].dropna().unique())) if c_est_ent else ["Todos"]
                        f_est_ent = st.selectbox("🏢 Estado/Entidad", opt_est_ent)
                    if f_est_ent != "Todos" and c_est_ent:
                        df_cs = df_cs[df_cs[c_est_ent] == f_est_ent]

                    col_s5, col_s6, col_s7, col_s8 = st.columns(4)
                    with col_s5:
                        opt_reg = ["Todos"] + sorted(list(df_cs[c_reg].dropna().unique())) if c_reg else ["Todos"]
                        f_reg = st.selectbox("🗺️ Región", opt_reg)
                    if f_reg != "Todos" and c_reg:
                        df_cs = df_cs[df_cs[c_reg] == f_reg]
                        
                    with col_s6:
                        opt_prov = ["Todos"] + sorted(list(df_cs[c_prov].dropna().unique())) if c_prov else ["Todos"]
                        f_prov = st.selectbox("📍 Provincia", opt_prov)
                    if f_prov != "Todos" and c_prov:
                        df_cs = df_cs[df_cs[c_prov] == f_prov]
                        
                    with col_s7:
                        opt_dist = ["Todos"] + sorted(list(df_cs[c_dist].dropna().unique())) if c_dist else ["Todos"]
                        f_dist = st.selectbox("🏢 Distrito", opt_dist)
                    if f_dist != "Todos" and c_dist:
                        df_cs = df_cs[df_cs[c_dist] == f_dist]
                        
                    with col_s8:
                        opt_tstock = ["Todos"] + sorted(list(df_cs[c_tstock].dropna().unique())) if c_tstock else ["Todos"]
                        f_tstock = st.selectbox("📦 Tipo stock", opt_tstock)

                df_stock_filtrado = df.copy()
                if buscado:
                    df_stock_filtrado = df_stock_filtrado[df_stock_filtrado.astype(str).apply(lambda x: x.str.contains(buscado, case=False)).any(axis=1)]
                if f_pn != "Todos" and c_pn:
                    df_stock_filtrado = df_stock_filtrado[df_stock_filtrado[c_pn] == f_pn]
                if f_tipo != "Todos" and c_tipo:
                    df_stock_filtrado = df_stock_filtrado[df_stock_filtrado[c_tipo] == f_tipo]
                if f_desc != "Todos" and c_desc:
                    df_stock_filtrado = df_stock_filtrado[df_stock_filtrado[c_desc] == f_desc]
                if f_est_ent != "Todos" and c_est_ent:
                    df_stock_filtrado = df_stock_filtrado[df_stock_filtrado[c_est_ent] == f_est_ent]
                if f_reg != "Todos" and c_reg:
                    df_stock_filtrado = df_stock_filtrado[df_stock_filtrado[c_reg] == f_reg]
                if f_prov != "Todos" and c_prov:
                    df_stock_filtrado = df_stock_filtrado[df_stock_filtrado[c_prov] == f_prov]
                if f_dist != "Todos" and c_dist:
                    df_stock_filtrado = df_stock_filtrado[df_stock_filtrado[c_dist] == f_dist]
                if f_tstock != "Todos" and c_tstock:
                    df_stock_filtrado = df_stock_filtrado[df_stock_filtrado[c_tstock] == f_tstock]

                st.info(f"📊 Mostrando **{len(df_stock_filtrado)}** registros coincidentes (de un total de {len(df)}).")
                df_estilizado = df_stock_filtrado.style.set_table_styles([
                    {'selector': 'th', 'props': [('background-color', '#1e293b'), ('color', '#ffffff'), ('font-size', '13px'), ('font-weight', 'bold'), ('text-align', 'center')]}
                ]).hide(axis="index")
                st.dataframe(df_estilizado, use_container_width=True, height=450)
            else:
                st.warning("La pestaña se leyó pero no se encontraron datos.")
        except Exception as e:
            st.error("⚠️ No se pudo leer la pestaña de Google Sheets.")
            with st.expander("Ver detalles técnicos"):
                st.write(e)

    # ==========================================
    # 3. MÓDULO GESTIÓN DE CAMBIOS
    # ==========================================
    elif st.session_state.seccion_activa == "Gestión Cambios":
        url_csv = f"https://docs.google.com/spreadsheets/d/{ID_HOJA}/export?format=csv&gid={GID_CONTROL_STOCK}"
        
        st.markdown("Ingrese el número de serie del equipo o componente afectado para iniciar el proceso de reemplazo.")
        
        col_input, col_btn, col_espacio = st.columns([2, 1, 3])
        with col_input:
            serie_a_buscar = st.text_input("Ingrese serie a revisar:", placeholder="Ej: ZVV84125", label_visibility="collapsed")
        with col_btn:
            buscar_serie = st.button("🔍 Buscar Serie", use_container_width=True)

        if buscar_serie or serie_a_buscar:
            if not serie_a_buscar.strip():
                st.warning("⚠️ Por favor, ingrese un número de serie válido.")
            else:
                try:
                    with st.spinner("🔍 Consultando registros..."):
                        df_cambios = pd.read_csv(url_csv, header=0)
                        df_cambios = df_cambios.loc[:, ~df_cambios.columns.str.contains('^Unnamed')]

                    df_cambios.columns = df_cambios.columns.astype(str).str.strip().str.upper()

                    col_serie_real = None
                    for col in df_cambios.columns:
                        if col in ["SERIE", "SERIAL"]:
                            col_serie_real = col
                            break
                    
                    if col_serie_real:
                        serie_limpia = serie_a_buscar.strip()
                        resultado = df_cambios[df_cambios[col_serie_real].astype(str).str.strip().str.upper() == serie_limpia.upper()]

                        if not resultado.empty:
                            st.success(f"¡Se encontró 1 registro asociado a la serie afectada: **{serie_a_buscar}**!")
                            
                            def obtener_valor(row, posibles_nombres):
                                for nombre in posibles_nombres:
                                    nombre_norm = nombre.strip().upper()
                                    if nombre_norm in row.index:
                                        val = row[nombre_norm]
                                        return str(val) if pd.notna(val) else "N/A"
                                return "N/A"

                            for idx, row in resultado.iterrows():
                                item_val = obtener_valor(row, ['ITEM'])
                                pn_val = obtener_valor(row, ['PN', 'PART NUMBER'])
                                tipo_val = obtener_valor(row, ['TIPO'])
                                desc_val = obtener_valor(row, ['DESCRIPCIÓN', 'DESCRIPCION'])
                                serie_val = obtener_valor(row, ['SERIE'])
                                est_ent_val = obtener_valor(row, ['ESTADO/ENTIDAD', 'ESTADO / ENTIDAD'])
                                reg_val = obtener_valor(row, ['REGIÓN', 'REGION'])
                                prov_val = obtener_valor(row, ['PROVINCIA'])
                                dist_val = obtener_valor(row, ['DISTRITO', 'DISTRITO/SEDE'])
                                tstock_val = obtener_valor(row, ['TIPO STOCK'])
                                obs_val = obtener_valor(row, ['OBSERVACIONES', 'OBSERVACIÓN', 'OBSERVACION'])

                                st.markdown(f"""
                                    <div class="asset-card">
                                        <div class="asset-header">
                                            <span>🗂️</span> Ficha Técnica del Activo Afectado: <strong style="color: #2563eb;">{serie_val}</strong>
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)

                                rc1, rc2, rc3 = st.columns(3)
                                with rc1:
                                    st.markdown(f"""
                                        <div class="field-label">Item</div>
                                        <div class="field-value">{item_val}</div>
                                        <div class="field-label">PN</div>
                                        <div class="field-value">{pn_val}</div>
                                        <div class="field-label">Tipo</div>
                                        <div class="field-value">{tipo_val}</div>
                                        <div class="field-label">Descripción</div>
                                        <div class="field-value">{desc_val}</div>
                                    """, unsafe_allow_html=True)
                                with rc2:
                                    st.markdown(f"""
                                        <div class="field-label">Serie</div>
                                        <div class="field-value">{serie_val}</div>
                                        <div class="field-label">Estado / Entidad</div>
                                        <div class="field-value">{est_ent_val}</div>
                                        <div class="field-label">Región</div>
                                        <div class="field-value">{reg_val}</div>
                                        <div class="field-label">Provincia</div>
                                        <div class="field-value">{prov_val}</div>
                                    """, unsafe_allow_html=True)
                                with rc3:
                                    st.markdown(f"""
                                        <div class="field-label">Distrito</div>
                                        <div class="field-value">{dist_val}</div>
                                        <div class="field-label">Tipo Stock</div>
                                        <div class="field-value">{tstock_val}</div>
                                        <div class="field-label">Observaciones</div>
                                        <div class="field-value">{obs_val}</div>
                                    """, unsafe_allow_html=True)

                                st.markdown("---")
                                
                                with st.expander("🔄 ¿Procedemos con el cambio del equipo?", expanded=True):
                                    opcion_stock = st.radio(
                                        "Seleccione el stock destino para el cambio:",
                                        options=["Stock Incidencias", "Stock Despliegue"],
                                        horizontal=True,
                                        key=f"radio_stock_{serie_val}"
                                    )
                                    
                                    if st.button("🚀 Buscar coincidencias para cambio", key=f"btn_cambio_{serie_val}", type="primary"):
                                        col_pn_busq = None
                                        for c in df_cambios.columns:
                                            if c in ["PN", "PART NUMBER"]:
                                                col_pn_busq = c
                                                break
                                                
                                        col_est_busq = None
                                        for c in df_cambios.columns:
                                            if c in ["ESTADO/ENTIDAD", "ESTADO / ENTIDAD"]:
                                                col_est_busq = c
                                                break

                                        if col_pn_busq and col_est_busq:
                                            df_match = df_cambios[
                                                (df_cambios[col_pn_busq].astype(str).str.strip().str.upper() == pn_val.strip().upper()) &
                                                (df_cambios[col_est_busq].astype(str).str.strip().str.upper().str.contains(opcion_stock.upper().replace("STOCK ", "")))
                                            ]

                                            if not df_match.empty:
                                                st.session_state[f"df_match_{serie_val}"] = df_match
                                                st.session_state[f"busqueda_activa_{serie_val}"] = True
                                            else:
                                                st.warning(f"⚠️ No se encontraron elementos en **{opcion_stock}** que hagan match con el PN **{pn_val}**.")
                                                st.session_state[f"busqueda_activa_{serie_val}"] = False

                                    if st.session_state.get(f"busqueda_activa_{serie_val}", False):
                                        df_match = st.session_state[f"df_match_{serie_val}"]
                                        st.success(f"Se encontraron **{len(df_match)}** registros disponibles en stock para el PN: **{pn_val}**")

                                        columnas_deseadas_map = {
                                            'PN': ['PN', 'PART NUMBER'],
                                            'TIPO': ['TIPO'],
                                            'SERIE': ['SERIE', 'SERIAL'],
                                            'DESCRIPCIÓN': ['DESCRIPCIÓN', 'DESCRIPCION'],
                                            'ESTADO/ENTIDAD': ['ESTADO/ENTIDAD', 'ESTADO / ENTIDAD'],
                                            'REGIÓN': ['REGIÓN', 'REGION'],
                                            'PROVINCIA': ['PROVINCIA'],
                                            'DISTRITO': ['DISTRITO', 'DISTRITO/SEDE'],
                                            'TIPO STOCK': ['TIPO STOCK'],
                                            'OBSERVACIONES': ['OBSERVACIONES', 'OBSERVACIÓN', 'OBSERVACION']
                                        }

                                        cols_finales_presentes = []
                                        renombrar_dict = {}
                                        for k, posibles in columnas_deseadas_map.items():
                                            for p in posibles:
                                                if p in df_match.columns:
                                                    cols_finales_presentes.append(p)
                                                    renombrar_dict[p] = k
                                                    break

                                        df_mostrar = df_match[cols_finales_presentes].rename(columns=renombrar_dict)
                                        df_mostrar.insert(0, "SELECCIONAR", False)

                                        st.markdown("### 📋 Marque el equipo a usar en la tabla:")
                                        
                                        df_editado = st.data_editor(
                                            df_mostrar,
                                            use_container_width=True,
                                            height=300,
                                            hide_index=True,
                                            disabled=[c for c in df_mostrar.columns if c != "SELECCIONAR"],
                                            key=f"editor_stock_{serie_val}"
                                        )

                                        filas_seleccionadas = df_editado[df_editado["SELECCIONAR"] == True]
                                        
                                        serie_seleccionada = None
                                        if not filas_seleccionadas.empty:
                                            serie_seleccionada = filas_seleccionadas.iloc[0]["SERIE"]
                                            st.info(f"👉 Equipo seleccionado para el reemplazo: **{serie_seleccionada}**")

                                        if st.button("⚡ Confirmar y Reemplazar Equipo", key=f"btn_ejecutar_reemplazo_{serie_val}", type="primary"):
                                            if not serie_seleccionada:
                                                st.warning("⚠️ Por favor, marque la casilla (checkbox) del equipo que desea utilizar en la tabla superior.")
                                            else:
                                                val_k = row.iloc[10] if len(row) > 10 else ""
                                                val_l = row.iloc[11] if len(row) > 11 else ""
                                                val_m = row.iloc[12] if len(row) > 12 else ""
                                                val_n = row.iloc[13] if len(row) > 13 else ""

                                                payload = {
                                                    "accion": "ejecutar_reemplazo",
                                                    "serie_afectada": serie_val,
                                                    "serie_nueva": serie_seleccionada,
                                                    "val_k": str(val_k),
                                                    "val_l": str(val_l),
                                                    "val_m": str(val_m),
                                                    "val_n": str(val_n)
                                                }
                                                
                                                try:
                                                    with st.spinner("✍️ Escribiendo cambios en Google Sheets..."):
                                                        r = requests.post(
                                                            WEB_APP_URL,
                                                            data=json.dumps(payload),
                                                            headers={"Content-Type": "text/plain;charset=utf-8"},
                                                            timeout=30
                                                        )
                                                        try:
                                                            resultado_json = r.json()
                                                        except Exception:
                                                            st.error("⚠️ El servidor de Google no devolvió un JSON válido.")
                                                            resultado_json = None
                                                            
                                                        if resultado_json and resultado_json.get("status") == "success":
                                                            st.success("¡Reemplazo procesado exitosamente en Google Sheets!")
                                                        elif resultado_json:
                                                            st.error(f"❌ Error: {resultado_json.get('message')}")
                                                except Exception as ex:
                                                    st.error("⚠️ No se pudo conectar con el Web App de Google Apps Script.")
                                                    with st.expander("Ver detalles técnicos"):
                                                        st.write(ex)
                        else:
                            st.error(f"❌ No se encontró ningún equipo con la serie **'{serie_a_buscar}'**.")
                    else:
                        st.error("⚠️ No se encontró la columna 'SERIE' en la estructura de la pestaña.")
                except Exception as e:
                    st.error("⚠️ Ocurrió un error al procesar la búsqueda.")
                    with st.expander("Ver detalles técnicos"):
                        st.write(e)

    # ==========================================
    # 4. MÓDULO GENERADOR GR
    # ==========================================
    elif st.session_state.seccion_activa == "Generador GR":
        @st.dialog("📄 Generador de Guías de Remisión (GR)", width="large")
        def modal_generador_gr():
            st.write("Interactúa a continuación con tu hoja de cálculo integrada (con sus pestañas, fórmulas y macros para la emisión de guías):")
            url_embed = f"https://docs.google.com/spreadsheets/d/{ID_HOJA_GR}/edit?usp=sharing&widget=true&headers=false"
            st.components.v1.iframe(url_embed, height=550, scrolling=True)
            
            col_cerrar, _ = st.columns([1, 4])
            with col_cerrar:
                if st.button("Cerrar Ventana ❌", use_container_width=True):
                    st.session_state.seccion_activa = None
                    st.query_params.clear()
                    st.rerun()

        modal_generador_gr()

    # ==========================================
    # 5. MÓDULO DASHBOARD
    # ==========================================
    elif st.session_state.seccion_activa == "Dashboard":
        st.markdown("### 📊 Dashboard de Indicadores")
        st.info("🚧 Módulo de indicadores en desarrollo.")

    # ==========================================
    # 6. MÓDULO ENTIDADES Y RUC
    # ==========================================
    elif st.session_state.seccion_activa == "Entidades y RUC":
        st.write("Consulta y busca la información oficial de las entidades, razones sociales y números de RUC registrados.")
        url_csv = f"https://docs.google.com/spreadsheets/d/{ID_HOJA}/export?format=csv&gid={GID_ENTIDADES}"
        
        try:
            with st.spinner("📥 Sincronizando directorio de Entidades y RUC..."):
                df_dir = pd.read_csv(url_csv)
                df_dir = df_dir.loc[:, ~df_dir.columns.str.contains('^Unnamed')]

            if not df_dir.empty:
                buscado_dir = st.text_input("🔍 Buscar entidad o RUC:", placeholder="Escribe Razón Social, RUC, UBIGEO o contacto...")
                
                df_filtrado = df_dir.copy()
                if buscado_dir:
                    df_filtrado = df_filtrado[df_filtrado.astype(str).apply(lambda x: x.str.contains(buscado_dir, case=False)).any(axis=1)]

                st.markdown("---")

                df_est_dir = df_filtrado.style.set_table_styles([
                    {'selector': 'th', 'props': [('background-color', '#0e7490'), ('color', '#ffffff'), ('font-size', '13px'), ('font-weight', 'bold'), ('text-align', 'center')]}
                ]).hide(axis="index")
                
                st.dataframe(df_est_dir, use_container_width=True, height=500)
                
                csv_export = df_filtrado.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Descargar reporte filtrado (CSV)",
                    data=csv_export,
                    file_name="entidades_y_ruc_filtrado.csv",
                    mime="text/csv"
                )
            else:
                st.warning("⚠️ La pestaña 'Entidades y RUC' está vacía o no se encontraron datos.")
                
        except Exception as e:
            st.error("⚠️ No se pudo conectar o leer la pestaña 'Entidades y RUC'.")
            with st.expander("Ver detalles técnicos"):
                st.write(e)