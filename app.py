"""
Streamlit Interface for OR-Tools Shift Scheduler

Interactive web interface for generating and visualizing shift schedules.
"""

import streamlit as st
import pandas as pd
import calendar
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go
from scheduler import ShiftScheduler


def main():
    st.set_page_config(
        page_title="Gestor de Turnos",
        page_icon="📅",
        layout="wide"
    )
    
    st.title("📅 Gestor de Turnos OR-Tools")
    st.markdown("Gere horários mensais de turnos para 5 trabalhadores com restrições otimizadas")
    
    # Initialize scheduler (will be recreated with new parameters when needed)
    
    # Sidebar controls
    with st.sidebar:
        st.header("⚙️ Configuração do Horário")
        
        # Month/Year selector
        col1, col2 = st.columns(2)
        with col1:
            month = st.selectbox(
                "Mês",
                options=list(range(1, 13)),
                format_func=lambda x: calendar.month_name[x],
                index=datetime.now().month - 1
            )
        with col2:
            year = st.selectbox(
                "Ano",
                options=list(range(2024, 2030)),
                index=0
            )
        
        st.markdown("---")
        st.markdown("### 👥 Configurações da Equipa")
        
        # Configurable parameters
        num_workers = st.slider(
            "Número de Trabalhadores",
            min_value=3,
            max_value=10,
            value=4,
            help="Número total de trabalhadores no sistema"
        )
        
        workers_per_shift = st.slider(
            "Trabalhadores por Turno",
            min_value=1,
            max_value=1,
            value=1,
            help="Número de trabalhadores por turno (sempre 1 por turno)"
        )
        
        st.markdown("### 📅 Dias de Trabalho por Semana")
        col1, col2 = st.columns(2)
        with col1:
            min_working_days = st.slider(
                "Dias Mínimos",
                min_value=1,
                max_value=6,
                value=1,
                help="Dias mínimos de trabalho por semana"
            )
        with col2:
            max_working_days = st.slider(
                "Dias Máximos",
                min_value=2,
                max_value=7,
                value=7,
                help="Dias máximos de trabalho por semana"
            )
        
        # Validate min/max
        if min_working_days >= max_working_days:
            st.error("Os dias mínimos devem ser inferiores aos dias máximos")
            st.stop()
        
        st.markdown("### 🔧 Opções Avançadas")
        
        # Strict pattern checkbox
        strict_pattern = st.checkbox(
            "Aplicar padrão estrito 4+2 dias",
            value=True,
            help="OBRIGATÓRIO: Trabalhadores devem trabalhar 4 dias consecutivos seguidos de 2 dias de folga"
        )
        
        if not strict_pattern:
            st.info("💡 **Modo Flexível Ativo**: O padrão estrito 4+2 dias está desativado. Isto aumenta significativamente as hipóteses de encontrar um horário viável.")
        else:
            st.success("✅ **Padrão 4+2 Obrigatório**: Trabalhadores trabalham 4 dias consecutivos seguidos de 2 dias de folga.")
        
        # Check for problematic configurations
        if num_workers < 4:
            st.error("⚠️ **Configuração Insuficiente**: São necessários pelo menos 4 trabalhadores.")
        elif num_workers == 4 and workers_per_shift == 1:
            st.warning("⚠️ **Configuração Mínima**: 4 trabalhadores com 1 por turno é o mínimo viável.")
        elif num_workers >= 5 and workers_per_shift == 1:
            st.success("✅ **Configuração Recomendada**: Esta configuração deve funcionar bem.")
        elif num_workers >= 6:
            st.success("✅ **Configuração Excelente**: Boa cobertura e flexibilidade.")
        
        # Generate button
        generate_btn = st.button("🚀 Gerar Horário", type="primary", use_container_width=True)
        
        # Display shift information
        st.markdown("---")
        st.markdown("### 📋 Informação dos Turnos")
        st.markdown("""
        **Dias Úteis (Seg-Sáb):**
        - 7h-16h (Manhã)
        - 15h-00h (Tarde)
        - 00h-08h (Noite)
        - 9h-21h (Estendido)
        
        **Domingos:**
        - 7h-16h (Manhã)
        - 15h-00h (Tarde)
        - 00h-08h (Noite)
        """)
        
        st.markdown("### 📊 Restrições")
        st.markdown("""
        - **Cobertura por Turno**: 1 trabalhador por turno
        - **Cobertura por Dia**:
          - Dias úteis: 4 turnos (3 normais + 1 estendido) = 4 trabalhadores
          - Domingos: 3 turnos (3 normais) = 3 trabalhadores
        - **Padrão de Trabalho**: **OBRIGATÓRIO** - 4 dias consecutivos, depois 2 dias de folga
        - **Consistência de Turno**: **OBRIGATÓRIA** - Trabalhadores mantêm o mesmo turno durante o período de trabalho até folgarem (depois podem mudar de turno)
        - **Restrições**: Sem semana completa de folga
        """)
        
        st.markdown("""
        ## 🎯 Soluções Recomendadas
        
        ### Solução A: Configuração Mínima
        - ✅ **4 trabalhadores, 1 por turno, 1-7 dias/semana** (mínimo viável com consistência)
        - ⚠️ **5+ trabalhadores**: Pode não funcionar com consistência obrigatória
        
        ### Solução B: Configuração Flexível
        - ✅ **4 trabalhadores, 1 por turno, 1-7 dias/semana** (recomendado)
        - 💡 **Nota**: Com consistência obrigatória, 4 trabalhadores é o ideal
        
        ### Solução C: Configuração Alternativa
        - 🔧 **Para mais trabalhadores**: Considere desativar o padrão estrito 4+2 dias
        - 🔧 **Para maior flexibilidade**: Ajuste os dias de trabalho por semana
        
        ## 🎛️ Recomendações da Interface Streamlit
        
        A interface atual permite-lhe experimentar com estes parâmetros:
        - **Use 4 trabalhadores, 1 por turno** para sucesso garantido com consistência
        - **Para mais trabalhadores**: Pode ser necessário relaxar restrições
        - **Ajuste os dias de trabalho para 1-7** para máxima flexibilidade
        - **Use meses diferentes** para encontrar um melhor alinhamento
        
        > ⚠️ **Nota Importante**: O padrão de 4 dias de trabalho/2 dias de folga é a restrição mais rigorosa e a principal razão para a inviabilidade em cenários de menor força de trabalho.
        """)
    
    # Main content area
    if generate_btn:
        # Create scheduler with current parameters
        scheduler = ShiftScheduler(
            num_workers=num_workers,
            workers_per_shift=workers_per_shift,
            min_working_days=min_working_days,
            max_working_days=max_working_days,
            strict_pattern=strict_pattern
        )
        
        with st.spinner("A gerar horário... Isto pode demorar alguns momentos."):
            result = scheduler.solve_schedule(year, month)
        
        if result:
            st.success(f"✅ Horário gerado com sucesso para {calendar.month_name[month]} {year}")
            
            # Store result in session state
            st.session_state.schedule_result = result
            st.session_state.scheduler = scheduler
            
            # Create tabs for different views
            tab1, tab2, tab3, tab4 = st.tabs(["📅 Vista do Calendário", "👥 Vista dos Trabalhadores", "📊 Análise de Cobertura", "📁 Exportar"])
            
            with tab1:
                st.subheader("📅 Horário por Dia e Turno")
                schedule_df = scheduler.format_schedule(result)
                
                if not schedule_df.empty:
                    # Filter out unassigned shifts
                    assigned_df = schedule_df[schedule_df['Contagem'] > 0].copy()
                    
                    # Color code the shifts
                    def color_shift(val):
                        colors = {
                            '7h-16h': 'background-color: #e8f5e8',    # Light green
                            '15h-00h': 'background-color: #fff3cd',  # Light yellow
                            '00h-08h': 'background-color: #d1ecf1',  # Light blue
                            '9h-21h': 'background-color: #f8d7da'   # Light red
                        }
                        return colors.get(val, '')
                    
                    # Apply styling
                    styled_df = assigned_df.style.applymap(color_shift, subset=['Turno'])
                    st.dataframe(styled_df, use_container_width=True)
                    
                    # Summary statistics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total de Dias", len(schedule_df['Data'].unique()))
                    with col2:
                        st.metric("Total de Turnos", len(assigned_df))
                    with col3:
                        coverage = len(assigned_df[assigned_df['Contagem'] == 2]) / len(assigned_df) * 100
                        st.metric("Cobertura %", f"{coverage:.1f}%")
                else:
                    st.warning("Nenhum dado de horário disponível")
            
            with tab2:
                st.subheader("👥 Horário por Trabalhador")
                worker_df = scheduler.get_worker_schedule(result)
                
                if not worker_df.empty:
                    # Create worker selector
                    selected_worker = st.selectbox(
                        "Selecionar Trabalhador para Ver",
                        options=[f"Trabalhador {i+1}" for i in range(scheduler.num_workers)],
                        key="worker_selector"
                    )
                    
                    # Filter data for selected worker
                    worker_data = worker_df[worker_df['Trabalhador'] == selected_worker]
                    
                    # Display worker schedule
                    st.dataframe(worker_data, use_container_width=True)
                    
                    # Worker statistics
                    working_days = len(worker_data[worker_data['Estado'] == 'Trabalho'])
                    off_days = len(worker_data[worker_data['Estado'] == 'Folga'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Dias de Trabalho", working_days)
                    with col2:
                        st.metric("Dias de Folga", off_days)
                    
                    # Visualize worker pattern
                    fig = px.bar(
                        worker_data, 
                        x='Data', 
                        y='Estado',
                        color='Estado',
                        title=f"Padrão de Horário - {selected_worker}",
                        color_discrete_map={'Trabalho': '#2E8B57', 'Folga': '#DC143C'}
                    )
                    fig.update_layout(xaxis_tickangle=45)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Nenhum dado de horário de trabalhador disponível")
            
            with tab3:
                st.subheader("📊 Análise de Cobertura")
                
                if 'schedule_result' in st.session_state:
                    schedule_df = scheduler.format_schedule(result)
                    
                    if not schedule_df.empty:
                        # Shift coverage analysis
                        shift_coverage = schedule_df.groupby('Turno')['Contagem'].agg(['sum', 'mean', 'count']).reset_index()
                        shift_coverage.columns = ['Turno', 'Total Trabalhadores', 'Média Trabalhadores', 'Dias']
                        shift_coverage['Cobertura %'] = (shift_coverage['Total Trabalhadores'] / (shift_coverage['Dias'] * 2) * 100).round(1)
                        
                        st.subheader("Resumo da Cobertura de Turnos")
                        st.dataframe(shift_coverage, use_container_width=True)
                        
                        # Visualize coverage
                        fig = px.bar(
                            shift_coverage,
                            x='Turno',
                            y='Cobertura %',
                            title='Percentagem de Cobertura por Turno',
                            color='Cobertura %',
                            color_continuous_scale='RdYlGn'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Daily coverage heatmap
                        daily_coverage = schedule_df.pivot_table(
                            index='Data', 
                            columns='Turno', 
                            values='Contagem', 
                            fill_value=0
                        )
                        
                        fig = px.imshow(
                            daily_coverage.T,
                            title='Mapa de Calor - Cobertura Diária de Turnos',
                            color_continuous_scale='RdYlGn',
                            aspect='auto'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("Nenhum dado de cobertura disponível")
            
            with tab4:
                st.subheader("📁 Exportar Horário")
                
                if 'schedule_result' in st.session_state:
                    schedule_df = scheduler.format_schedule(result)
                    worker_df = scheduler.get_worker_schedule(result)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**📅 Horário Diário (CSV)**")
                        csv_schedule = schedule_df.to_csv(index=False)
                        st.download_button(
                            label="Descarregar Horário Diário",
                            data=csv_schedule,
                            file_name=f"horario_{year}_{month:02d}.csv",
                            mime="text/csv"
                        )
                    
                    with col2:
                        st.markdown("**👥 Horário dos Trabalhadores (CSV)**")
                        csv_workers = worker_df.to_csv(index=False)
                        st.download_button(
                            label="Descarregar Horário dos Trabalhadores",
                            data=csv_workers,
                            file_name=f"trabalhadores_{year}_{month:02d}.csv",
                            mime="text/csv"
                        )
                    
                    # Display preview of data to export
                    st.markdown("**Pré-visualização dos Dados para Exportar:**")
                    preview_tab1, preview_tab2 = st.tabs(["Horário Diário", "Horário dos Trabalhadores"])
                    
                    with preview_tab1:
                        st.dataframe(schedule_df.head(10), use_container_width=True)
                    
                    with preview_tab2:
                        st.dataframe(worker_df.head(10), use_container_width=True)
        else:
            st.error("❌ Impossível gerar um horário viável. As restrições podem ser demasiado restritivas para este mês.")
            st.markdown("""
            **Soluções possíveis:**
            - Experimente um mês diferente
            - O padrão de 4 dias de trabalho/2 dias de folga pode não se alinhar bem com o calendário deste mês
            - Considere ajustar as restrições se necessário
            """)
    
    # Display instructions if no schedule generated yet
    if 'schedule_result' not in st.session_state:
        st.markdown("""
        ## 🚀 Como Começar
        
        1. **Selecionar Mês/Ano** na barra lateral
        2. **Clicar em "Gerar Horário"** para criar o horário
        3. **Ver Resultados** nos diferentes separadores:
           - **Vista do Calendário**: Ver quais trabalhadores estão atribuídos a cada turno
           - **Vista dos Trabalhadores**: Ver o horário individual de cada trabalhador
           - **Análise de Cobertura**: Analisar a cobertura de turnos e padrões
           - **Exportar**: Descarregar horários como ficheiros CSV
        
        ## 📋 Sobre o Gestor de Horários
        
        Este sistema utiliza o Google OR-Tools para resolver restrições complexas de horários:
        - **5 Trabalhadores** com horários rotativos
        - **4 Tipos de Turno** (3 aos domingos)
        - **2 Trabalhadores por Turno** para cobertura adequada
        - **Padrão de 4 Dias de Trabalho, 2 Dias de Folga**
        - **Tipos de Turno Consistentes** durante os períodos de trabalho
        """)
        
        # Show example of what the schedule looks like
        st.markdown("### 📊 Pré-visualização do Exemplo de Horário")
        example_data = {
            'Date': ['2024-01-01', '2024-01-01', '2024-01-01', '2024-01-01'],
            'Day': ['Segunda-feira', 'Segunda-feira', 'Segunda-feira', 'Segunda-feira'],
            'Shift': ['7h-16h', '15h-00h', '00h-08h', '9h-21h'],
            'Workers': ['Trabalhador 1, Trabalhador 2', 'Trabalhador 3, Trabalhador 4', 'Trabalhador 5, Trabalhador 1', 'Trabalhador 2, Trabalhador 3'],
            'Count': [2, 2, 2, 2]
        }
        example_df = pd.DataFrame(example_data)
        st.dataframe(example_df, use_container_width=True)


if __name__ == "__main__":
    main()
