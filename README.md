# MyWay CRM

Sistema de gestión de relaciones con clientes (CRM) empresarial desarrollado con Django, diseñado para empresas B2B que requieren control avanzado de pipeline, forecasting de ventas y seguridad basada en roles.

## Características Principales

### Sistema de Lead Scoring Inteligente
- Calificación automática de oportunidades (0-100 puntos)
- Metodología FIT + ENGAGEMENT con penalización por degradación
- Categorización: Hot (80+), Warm (60-79), Cold (40-59), Frozen (0-39)
- Actualización automática mediante signals de Django
- Visualización con badges de colores en panel de administración

### Forecasting de Ventas
- Probabilidades ponderadas por etapa del pipeline
- Dashboard con comparación valor nominal vs weighted
- Gráfico de funnel para análisis de conversión
- Cálculo automático de confianza del forecast
- Basado en probabilidades: Prospección (10%), Negociación (50%), Cerrado (100%)

### Control de Acceso Basado en Roles (RBAC)
- **Sales Representative**: Acceso limitado a registros propios
- **Sales Manager**: Supervisión de equipo de ventas
- **Administrator**: Acceso completo al sistema
- Filtrado automático de querysets según rol
- Prevención de exportación de datos sensibles para roles limitados

### Gestión Avanzada de Interacciones
- Tipos: Llamadas, Reuniones, Emails, Notas
- Dirección de comunicación: Inbound, Outbound, Internal
- Predicción de próxima fecha de contacto basada en patrones históricos
- Análisis de frecuencia e intervalos entre interacciones
- Integración con Contactos, Deals y Accounts

### Catálogo de Productos y Cotizaciones
- Gestión de productos con SKU, categorías y precios
- Sistema de descuentos por línea de producto
- Actualización automática del valor del Deal al modificar productos
- Cálculo de totales con cantidades y descuentos

### Auditoría y Trazabilidad
- Historial de cambios en Deals mediante django-simple-history
- Timestamps automáticos en todos los modelos
- Registro de última actualización de scores

## Stack Tecnológico

- **Backend**: Django 5.2.11
- **Base de Datos**: PostgreSQL
- **Admin Interface**: django-unfold 0.80.2 (UI moderna y responsive)
- **Auditoría**: django-simple-history 3.11.0
- **Frontend**: TailwindCSS + Chart.js (dashboard)
- **Python**: 3.10.11

## Arquitectura del Sistema

### Aplicaciones Django

#### `accounts`
- Modelo Account para empresas/cuentas cliente
- UserProfile con roles (manager/sales)
- Comandos de management para setup RBAC

#### `contacts`
- Gestión de contactos vinculados a cuentas
- Cargo, teléfono, email, redes sociales
- Cálculo de próxima fecha de contacto

#### `deals`
- Pipeline de oportunidades de venta
- Sistema de lead scoring automático
- Gestión de productos por deal (DealProduct)
- Forecasting con probabilidades ponderadas
- Comandos: `update_lead_scores`

#### `interactions`
- Registro de todas las comunicaciones
- Subtipos especializados: Call, Meeting
- Cálculo algorítmico de próxima interacción

#### `core`
- Dashboard principal con KPIs
- Mixins RBAC para admin
- Vistas de forecasting

## Instalación

### Requisitos Previos
- Python 3.10+
- PostgreSQL 12+
- Git

### Configuración

1. Clonar el repositorio:
```bash
git clone <repository_url>
cd my_way
```

2. Crear entorno virtual:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar base de datos PostgreSQL:
```bash
# Crear base de datos
createdb myway_db

# Actualizar config/settings.py con credenciales
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'myway_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

5. Ejecutar migraciones:
```bash
python manage.py migrate
```

6. Configurar grupos RBAC:
```bash
python manage.py setup_rbac
```

7. Crear superusuario:
```bash
python manage.py createsuperuser
```

8. (Opcional) Cargar datos de prueba:
```bash
python seed.py
```

9. Iniciar servidor:
```bash
python manage.py runserver
```

## Uso

### Panel de Administración
Acceder a: `http://localhost:8000/admin/`

Features:
- Gestión completa de Accounts, Contacts, Deals, Products
- Visualización de lead scores con colores
- Inlines de interacciones en cada registro
- Filtros avanzados por etapa, asignación, score

### Dashboard de Forecasting
Acceder a: `http://localhost:8000/`

Métricas disponibles:
- Ingresos cerrados totales
- Win rate (tasa de conversión)
- Oportunidades activas en pipeline
- Pipeline nominal vs ponderado
- Tabla de distribución por etapa
- Gráfico de funnel comparativo

### Comandos de Management

#### Recalcular Lead Scores
```bash
python manage.py update_lead_scores --verbose
```

Output:
- Estadísticas de deals actualizados
- Distribución por categoría (Hot/Warm/Cold/Frozen)
- Top 5 hot leads

#### Configurar RBAC
```bash
python manage.py setup_rbac
```

Crea automáticamente:
- Sales Representative (15 permisos)
- Sales Manager (22 permisos)
- Administrator (24 permisos)

## Metodología de Lead Scoring

### Componentes del Score (0-100 puntos)

**FIT Score (50 puntos máx):**
- Industria objetivo (20 pts)
- Tamaño del deal (15 pts)
- Cargo del contacto (15 pts)

**ENGAGEMENT Score (50 puntos máx):**
- Recencia de interacción (20 pts)
- Frecuencia de interacciones (15 pts)
- Velocidad en el pipeline (15 pts)

**DEGRADACIÓN (hasta -30 pts):**
- Penalización por inactividad prolongada
- Máximo -30 pts por deals sin actividad > 60 días

### Actualización Automática
El score se recalcula automáticamente cuando:
- Se modifica un Deal
- Se crea/edita/elimina una Interacción
- Se agregan/eliminan Productos del Deal

## Sistema de Forecasting

### Probabilidades por Etapa
| Etapa | Probabilidad | Interpretación |
|-------|-------------|----------------|
| Prospección | 10% | Contacto inicial, calificación |
| Negociación | 50% | Propuesta enviada, discusión activa |
| Cerrado Ganado | 100% | Deal convertido |
| Cerrado Perdido | 0% | Oportunidad perdida |

### Cálculo de Valor Ponderado
```
Weighted Value = Deal Value × Stage Probability
```

### Confianza del Forecast
```
Confidence = (Total Weighted / Total Nominal) × 100
```

## Seguridad y Permisos

### Sales Representative
- Ver/editar: Propios deals, contactos, interacciones
- Sin acceso a: Deals de otros vendedores
- Sin permisos: Exportar datos, configuración

### Sales Manager
- Ver/editar: Todos los deals del equipo
- Gestión de: Productos, reportes
- Sin acceso: Configuración de usuarios

### Administrator
- Acceso completo a todas las funcionalidades
- Gestión de usuarios y permisos
- Configuración del sistema

## Personalización

### Ajustar Probabilidades de Forecasting
Editar `deals/models.py`:
```python
STAGE_PROBABILITIES = {
    'prospecting': 0.15,  # Ajustar según industria
    'negotiation': 0.60,
    'closed_won': 1.00,
    'closed_lost': 0.00,
}
```

### Modificar Paleta de Colores
Editar `config/settings.py`:
```python
UNFOLD = {
    "COLORS": {
        "primary": {
            "500": "#1A3263",  # Azul oscuro
        },
        # ... más colores
    }
}
```

### Agregar Etapas de Pipeline
1. Modificar `Deal.STAGES` en `deals/models.py`
2. Agregar probabilidad en `STAGE_PROBABILITIES`
3. Ejecutar `python manage.py makemigrations`
4. Ejecutar `python manage.py migrate`

## Estructura de Archivos
```
my_way/
├── accounts/           # Cuentas y usuarios
├── contacts/           # Contactos
├── deals/             # Oportunidades y productos
├── interactions/      # Comunicaciones
├── core/              # Dashboard y utilities
├── config/            # Configuración Django
├── static/            # Assets estáticos
├── docs/              # Documentación técnica
│   ├── LEAD_SCORING.md
│   └── FORECASTING.md
├── manage.py
├── seed.py           # Script de datos de prueba
└── requirements.txt
```

## Documentación Adicional

- **Lead Scoring Detallado**: `docs/LEAD_SCORING.md`
- **Forecasting Técnico**: `docs/FORECASTING.md`
- **RBAC Setup**: Ver código en `accounts/management/commands/setup_rbac.py`

## Soporte y Contribuciones

Para reportar bugs o solicitar features, abrir un issue en el repositorio.

## Licencia

Propietario: Definir según necesidades del proyecto.

---

**Versión**: 1.0  
**Última Actualización**: Febrero 2026