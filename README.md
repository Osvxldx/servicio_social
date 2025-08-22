# Sistema de Gestión de Pago de Agua

Una aplicación de escritorio desarrollada con Electron, SQLite y TailwindCSS para la gestión de pagos de agua de clientes.

## 🚀 Características

- **Login seguro**: Acceso mediante PIN numérico (por defecto: 1234)
- **Dashboard interactivo**: Vista general con estadísticas y filtros
- **Gestión de clientes**: Agregar, editar y consultar información completa
- **Búsqueda en tiempo real**: Por nombre, ID o dirección
- **Historial de pagos**: Registro completo que nunca se elimina
- **Calendario**: Consultas por fechas específicas
- **Indicadores de consumo**: Seguimiento de exceso de agua
- **Interfaz moderna**: Diseño limpio con animaciones suaves
- **Funciona offline**: No requiere conexión a internet

## 📋 Requisitos del Sistema

- Windows 10 o superior
- 4 GB de RAM mínimo
- 500 MB de espacio en disco

## 🛠️ Instalación para Desarrollo

### 1. Instalar Node.js
Descarga e instala Node.js desde [nodejs.org](https://nodejs.org/) (versión 16 o superior).

### 2. Clonar o descargar el proyecto
```bash
# Si tienes git instalado
git clone <url-del-repositorio>

# O simplemente descarga y extrae los archivos del proyecto
```

### 3. Instalar dependencias
Abre una terminal en la carpeta del proyecto y ejecuta:
```bash
npm install
```

### 4. Ejecutar en modo desarrollo
```bash
npm run dev
```

## 📦 Crear Ejecutable para Windows

### 1. Instalar dependencias (si no lo has hecho)
```bash
npm install
```

### 2. Compilar la aplicación
```bash
npm run build:win
```

El ejecutable se generará en la carpeta `dist/` con el nombre `Sistema de Agua Setup.exe`.

### 3. Instalar la aplicación
- Ejecuta el archivo `Sistema de Agua Setup.exe`
- Sigue las instrucciones del instalador
- La aplicación se instalará en `Archivos de programa`
- Se creará un acceso directo en el escritorio

## 🔧 Configuración Inicial

### PIN de Administrador
- **PIN por defecto**: `1234`
- Para cambiar el PIN, modifica la base de datos SQLite en `data/agua.db`
- O implementa la funcionalidad de cambio de PIN en la página de ajustes

### Base de Datos
- La base de datos SQLite se crea automáticamente en `data/agua.db`
- Incluye las siguientes tablas:
  - `admin`: Información del administrador
  - `clients`: Datos de los clientes
  - `payments`: Historial de pagos
  - `consumption`: Registro de consumo de agua

## 📖 Guía de Uso

### 1. Inicio de Sesión
- Ejecuta la aplicación
- Ingresa el PIN: `1234`
- Haz clic en "Ingresar"

### 2. Dashboard Principal
- **Estadísticas**: Total de clientes, pagados, con deuda, exceso de consumo
- **Filtros**: Todos, Al corriente, Con deuda, Exceso consumo
- **Vistas**: Tabla o gráficas
- **Tabla de clientes**: Lista completa con estado de pagos

### 3. Gestión de Clientes
- **Agregar cliente**: Botón "Agregar Cliente"
- **Buscar**: Escribe en tiempo real por nombre, ID o dirección
- **Ver detalles**: Clic en el ícono de ojo
- **Editar**: Clic en el ícono de lápiz
- **Historial**: Ver todos los pagos del cliente

### 4. Calendario
- **Seleccionar fecha**: Usa el selector de fecha
- **Botón "Hoy"**: Volver a la fecha actual
- **Estadísticas diarias**: Pagos del día y total recaudado
- **Lista de pagos**: Todos los pagos de la fecha seleccionada

### 5. Navegación
- **Menú lateral**: Dashboard, Clientes, Calendario, Ajustes
- **Responsive**: Se adapta a diferentes tamaños de pantalla
- **Animaciones**: Transiciones suaves entre páginas

## 🗂️ Estructura del Proyecto

```
agua-dashboard/
├── src/
│   ├── main.js                 # Proceso principal de Electron
│   ├── database/
│   │   └── db.js              # Manejo de base de datos SQLite
│   └── renderer/
│       ├── index.html         # Interfaz principal
│       └── js/
│           ├── app.js         # Lógica principal de la aplicación
│           ├── clients.js     # Gestión de clientes
│           └── calendar.js    # Funcionalidad del calendario
├── data/                      # Base de datos (se crea automáticamente)
├── assets/                    # Iconos y recursos
├── package.json              # Configuración del proyecto
├── tailwind.config.js        # Configuración de TailwindCSS
└── README.md                 # Este archivo
```

## 🔍 Funcionalidades Detalladas

### Estados de Pago
- **✅ Pagado**: Cliente al corriente
- **❌ Pendiente**: Cliente con deuda
- **💧 Exceso**: Cliente con consumo excesivo de agua

### Búsqueda Inteligente
- Busca en tiempo real mientras escribes
- Funciona con nombres parciales
- Busca por ID numérico
- Busca por dirección completa o parcial

### Historial Completo
- Todos los pagos se guardan permanentemente
- Fechas exactas de cada transacción
- Montos y estados de pago
- Notas de consumo excesivo

## 🚨 Solución de Problemas

### La aplicación no inicia
- Verifica que Node.js esté instalado
- Ejecuta `npm install` nuevamente
- Revisa que no haya procesos de Electron ejecutándose

### Error de base de datos
- La carpeta `data/` debe tener permisos de escritura
- Si hay corrupción, elimina `data/agua.db` (se recreará automáticamente)

### PIN incorrecto
- El PIN por defecto es `1234`
- Verifica que no tengas Bloq Num activado
- Reinicia la aplicación si persiste el problema

### Problemas de rendimiento
- Cierra otras aplicaciones pesadas
- La aplicación funciona mejor con al menos 4GB de RAM
- Considera limpiar el historial si tienes miles de registros

## 📞 Soporte

Para reportar problemas o solicitar nuevas funcionalidades:
1. Describe el problema detalladamente
2. Incluye capturas de pantalla si es posible
3. Menciona la versión de Windows que usas

## 📝 Notas de Desarrollo

### Tecnologías Utilizadas
- **Electron**: Framework para aplicaciones de escritorio
- **SQLite**: Base de datos local ligera
- **TailwindCSS**: Framework de CSS para diseño
- **Chart.js**: Librería para gráficas
- **Node.js**: Entorno de ejecución

### Próximas Mejoras
- Exportar reportes a PDF/Excel
- Backup automático de la base de datos
- Configuración de tarifas personalizables
- Notificaciones de pagos vencidos
- Modo oscuro para la interfaz

---

**Versión**: 1.0.0  
**Desarrollado para**: Sistema de Gestión de Agua  
**Compatibilidad**: Windows 10/11
