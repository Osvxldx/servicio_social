# 📖 Manual de Instalación y Uso
## Sistema de Gestión de Pago de Agua

### 📋 Tabla de Contenidos
1. [Requisitos del Sistema](#requisitos-del-sistema)
2. [Instalación](#instalación)
3. [Ejecución](#ejecución)
4. [Manual de Usuario](#manual-de-usuario)
5. [Solución de Problemas](#solución-de-problemas)
6. [Características del Sistema](#características-del-sistema)

---

## 🖥️ Requisitos del Sistema

### Requisitos Mínimos:
- **Sistema Operativo:** Windows 7/8/10/11, macOS 10.12+, o Linux Ubuntu 16.04+
- **RAM:** 2 GB mínimo (4 GB recomendado)
- **Almacenamiento:** 500 MB de espacio libre
- **Python:** Versión 3.8 o superior

### Requisitos Recomendados:
- **RAM:** 4 GB o más
- **Almacenamiento:** 1 GB de espacio libre
- **Resolución:** 1024x768 mínimo (1920x1080 recomendado)

---

## ⬇️ Instalación

### Opción 1: Instalación desde Código Fuente (Recomendada)

#### Paso 1: Descargar el Proyecto
```bash
# Clonar el repositorio
git clone https://github.com/Osvxldx/servicio_social.git

# O descargar como ZIP desde GitHub y extraer
```

#### Paso 2: Instalar Python
1. Descargar Python desde https://python.org/downloads/
2. Durante la instalación, marcar "Add Python to PATH"
3. Verificar instalación:
```bash
python --version
pip --version
```

#### Paso 3: Configurar el Entorno Virtual
```bash
# Navegar al directorio del proyecto
cd servicio_social

# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# En Windows:
.venv\Scripts\activate
# En macOS/Linux:
source .venv/bin/activate
```

#### Paso 4: Instalar Dependencias
```bash
# Instalar las librerías requeridas
pip install PyQt5 matplotlib
```

### Opción 2: Instalación Rápida con Requirements

Si existe un archivo `requirements.txt`:
```bash
pip install -r requirements.txt
```

---

## 🚀 Ejecución

### Ejecutar la Aplicación

#### Desde la Terminal/CMD:
```bash
# Asegurarse de estar en el directorio del proyecto
cd servicio_social

# Activar entorno virtual (si no está activado)
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Ejecutar la aplicación
python main.py
```

#### Desde el Explorador de Archivos:
1. Navegar a la carpeta del proyecto
2. Hacer doble clic en `main.py`
3. Si no funciona, hacer clic derecho → "Abrir con" → Python

### Primera Ejecución
1. El sistema mostrará una pantalla de carga
2. Se creará automáticamente la base de datos SQLite
3. Aparecerá la ventana de login
4. **PIN por defecto: `1234`**

---

## 📚 Manual de Usuario

### 🔐 Login
- **PIN por defecto:** `1234`
- Ingrese el PIN y presione "Ingresar"
- Para mayor seguridad, cambie el PIN después del primer uso

### 🏠 Dashboard Principal
El dashboard muestra:
- **Estadísticas generales:** Total de clientes, deudas, pagos del mes
- **Tabla de clientes** con estados de pago
- **Filtros de búsqueda** por nombre, dirección o ID
- **Filtros de estado:** Todos, con deuda, al corriente, exceso de consumo

#### Navegación:
- **📊 Dashboard:** Vista principal con estadísticas
- **👥 Clientes:** Gestión de clientes
- **📅 Calendario:** Consulta de pagos por fecha
- **💰 Pagos:** Gestión de pagos (en desarrollo)
- **🔧 Configuración:** Cambio de PIN

### 👥 Gestión de Clientes

#### Agregar Nuevo Cliente:
1. Ir a la sección "Clientes"
2. Clic en "➕ Agregar Cliente"
3. Completar:
   - **Nombre completo** (obligatorio)
   - **Dirección** (obligatorio)
   - **Estado:** activo/inactivo
4. Clic en "Guardar"

#### Editar Cliente:
1. Seleccionar cliente en la tabla
2. Clic en "✏️ Editar Cliente"
3. Modificar datos necesarios
4. Guardar cambios

#### Ver Perfil Completo:
1. Hacer **doble clic** en un cliente
2. El perfil muestra 3 pestañas:
   - **Información:** Datos básicos del cliente
   - **Pagos:** Historial completo de pagos
   - **Consumo:** Registros de consumo de agua

#### Eliminar Cliente:
1. Seleccionar cliente
2. Clic en "🗑️ Eliminar Cliente"
3. Confirmar eliminación
4. **Nota:** Solo se pueden eliminar clientes sin pagos registrados

### 💰 Gestión de Pagos

#### Registrar Pago:
1. Desde el perfil del cliente
2. Clic en "Registrar Pago"
3. Completar:
   - **Monto:** Cantidad a pagar
   - **Estado:** Pagado/Pendiente
   - **Notas:** Información adicional (opcional)

#### Estados de Pago:
- **✅ Pagado:** Cliente al corriente
- **❌ Pendiente:** Cliente con deuda
- **⚪ Sin registros:** Cliente nuevo sin pagos

### 💧 Gestión de Consumo

#### Registrar Consumo:
1. Desde el perfil del cliente
2. Clic en "Registrar Consumo"
3. Seleccionar tipo:
   - **Normal:** Consumo regular
   - **Exceso:** Consumo excesivo o desperdicio
4. Agregar notas descriptivas

#### Indicadores de Consumo:
- **✅ Normal:** Consumo dentro de parámetros
- **💧 Exceso:** Consumo excesivo registrado

### 📅 Calendario
- Seleccionar fecha en el calendario
- Ver pagos registrados para esa fecha
- Información incluye cliente, monto y estado

### 🔧 Configuración

#### Cambiar PIN:
1. Ir a "Configuración"
2. Ingresar PIN actual
3. Ingresar nuevo PIN (mínimo 4 dígitos)
4. Confirmar nuevo PIN
5. Guardar cambios

---

## 🔍 Características del Sistema

### ✅ Funcionalidades Implementadas:
- ✅ Login seguro con PIN
- ✅ CRUD completo de clientes
- ✅ Gestión de pagos con historial
- ✅ Registro de consumo de agua
- ✅ Dashboard con estadísticas en tiempo real
- ✅ Calendario de consulta de pagos
- ✅ Búsqueda y filtrado avanzado
- ✅ Interfaz responsive y accesible
- ✅ Base de datos SQLite local
- ✅ Validación de datos
- ✅ Gestión de errores

### 🎨 Características de Diseño:
- **Interfaz moderna** con PyQt5
- **Estilos CSS personalizados** con tema azul agua
- **Iconos descriptivos** para mejor UX
- **Diseño responsive** adaptable
- **Animaciones suaves** sin sobrecargar
- **Accesibilidad** para equipos de bajos recursos

### 🔒 Seguridad:
- **Autenticación por PIN**
- **Validación de datos** en tiempo real
- **Gestión de errores** sin exposición de datos
- **Base de datos local** sin conexión externa

---

## 🔧 Solución de Problemas

### Problemas Comunes:

#### Error: "No module named 'PyQt5'"
```bash
# Instalar PyQt5
pip install PyQt5
```

#### Error: "No module named 'matplotlib'"
```bash
# Instalar matplotlib
pip install matplotlib
```

#### Error de Base de Datos:
- Verificar que el directorio `database/` tenga permisos de escritura
- En caso extremo, eliminar el archivo `agua_system.db` para regenerarlo

#### La aplicación no inicia:
1. Verificar que Python esté instalado correctamente
2. Asegurarse de que el entorno virtual esté activado
3. Verificar que todas las dependencias estén instaladas
4. Ejecutar desde terminal para ver errores específicos

#### PIN olvidado:
1. Cerrar la aplicación
2. Eliminar el archivo `database/agua_system.db`
3. Reiniciar la aplicación (PIN vuelve a `1234`)
4. **Nota:** Esto eliminará todos los datos

### 📞 Soporte:
- **GitHub Issues:** https://github.com/Osvxldx/servicio_social/issues
- **Documentación:** README.md en el repositorio

---

## 📊 Estructura del Proyecto

```
servicio_social/
├── main.py                    # Archivo principal
├── database/
│   ├── database_manager.py    # Gestión de base de datos
│   └── agua_system.db         # Base de datos SQLite (se crea automáticamente)
├── ui/
│   ├── login_window.py        # Ventana de login
│   ├── main_window.py         # Ventana principal
│   └── client_dialogs.py      # Diálogos de clientes
├── models/
│   └── data_models.py         # Modelos de datos
├── controllers/
│   └── app_controller.py      # Controlador principal
├── styles/
│   └── app_styles.py          # Estilos CSS
├── utils/
│   └── helpers.py             # Utilidades generales
└── README.md                  # Documentación del proyecto
```

---

## 🎯 Próximas Versiones

### Funcionalidades Planificadas:
- 📈 Gráficos avanzados con Matplotlib
- 📄 Exportación de reportes a PDF/Excel
- 🔄 Sistema de respaldos automáticos
- 📧 Notificaciones de pagos vencidos
- 🌐 Interfaz web opcional
- 📱 Versión móvil

---

**¡Sistema listo para usar! 🎉**

Para cualquier duda o problema, consulte la documentación o abra un issue en GitHub.
