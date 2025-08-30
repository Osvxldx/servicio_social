# 💧 Sistema de Gestión de Pago de Agua

Un sistema de escritorio desarrollado en Python con PyQt5 para gestionar pagos de agua municipal de manera eficiente y accesible.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)
![SQLite](https://img.shields.io/badge/Database-SQLite-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🌟 Características Principales

- ✅ **Login seguro** con PIN personalizable
- 👥 **Gestión completa de clientes** (CRUD)
- 💰 **Registro y seguimiento de pagos**
- 💧 **Control de consumo de agua**
- 📊 **Dashboard con estadísticas en tiempo real**
- 📅 **Calendario de consulta de pagos**
- 🔍 **Búsqueda y filtrado avanzado**
- 🎨 **Interfaz moderna y responsive**
- 🗄️ **Base de datos local SQLite**
- 🚀 **Optimizado para equipos de bajos recursos**

## 📸 Capturas de Pantalla

### Login
![Login](docs/screenshots/login.png)

### Dashboard Principal
![Dashboard](docs/screenshots/dashboard.png)

### Gestión de Clientes
![Clientes](docs/screenshots/clientes.png)

## 🚀 Instalación Rápida

### 1. Clonar el Repositorio
```bash
git clone https://github.com/Osvxldx/servicio_social.git
cd servicio_social
```

### 2. Crear Entorno Virtual
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar la Aplicación
```bash
python main.py
```

**PIN por defecto:** `1234`

## 📖 Documentación Completa

Para instrucciones detalladas de instalación, configuración y uso, consulte:
- 📋 [**Manual de Instalación Completo**](MANUAL_INSTALACION.md)

## 🏗️ Arquitectura del Proyecto

```
servicio_social/
├── 🚀 main.py                     # Punto de entrada principal
├── 📁 database/
│   ├── database_manager.py        # Gestión de base de datos SQLite
│   └── agua_system.db             # Base de datos (auto-generada)
├── 📁 ui/
│   ├── login_window.py            # Ventana de autenticación
│   ├── main_window.py             # Interfaz principal
│   └── client_dialogs.py          # Diálogos de gestión
├── 📁 models/
│   └── data_models.py             # Modelos de datos
├── 📁 controllers/
│   └── app_controller.py          # Lógica de negocio
├── 📁 styles/
│   └── app_styles.py              # Estilos CSS personalizados
├── 📁 utils/
│   └── helpers.py                 # Utilidades y herramientas
└── 📋 requirements.txt            # Dependencias del proyecto
```

## 🔧 Requisitos del Sistema

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| **SO** | Windows 7+ / macOS 10.12+ / Ubuntu 16.04+ | Windows 10+ / macOS 12+ / Ubuntu 20.04+ |
| **Python** | 3.8+ | 3.10+ |
| **RAM** | 2 GB | 4 GB |
| **Almacenamiento** | 500 MB | 1 GB |
| **Resolución** | 1024x768 | 1920x1080 |

## 🎯 Funcionalidades por Módulo

### 🔐 Sistema de Autenticación
- Login con PIN numérico
- Cambio de PIN desde configuración
- Validación de seguridad

### 👥 Gestión de Clientes
- Agregar clientes con ID autogenerado
- Editar información del cliente
- Eliminar clientes (sin pagos asociados)
- Búsqueda en tiempo real
- Estados: Activo/Inactivo

### 💰 Gestión de Pagos
- Registro de pagos con fecha automática
- Estados: Pagado/Pendiente
- Historial completo por cliente
- Notas adicionales

### 💧 Control de Consumo
- Registro de consumo normal/exceso
- Seguimiento de desperdicio de agua
- Notas descriptivas
- Historial por cliente

### 📊 Dashboard y Reportes
- Estadísticas en tiempo real
- Filtros avanzados
- Vista de calendario
- Indicadores visuales con iconos

## 🔌 Tecnologías Utilizadas

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **Python** | 3.8+ | Lenguaje principal |
| **PyQt5** | 5.15+ | Interfaz gráfica |
| **SQLite** | 3.x | Base de datos local |
| **Matplotlib** | 3.7+ | Gráficos y visualizaciones |

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Para contribuir:

1. Fork el proyecto
2. Crea tu rama de característica (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### 📋 Guías de Contribución
- Seguir las convenciones de código Python (PEP 8)
- Documentar nuevas funcionalidades
- Incluir pruebas cuando sea posible
- Actualizar documentación relevante

## 🐛 Reportar Problemas

Si encuentras un bug o tienes una sugerencia:

1. Verifica que no exista un issue similar
2. Abre un [nuevo issue](https://github.com/Osvxldx/servicio_social/issues)
3. Incluye detalles del problema:
   - SO y versión de Python
   - Pasos para reproducir
   - Capturas de pantalla si aplica

## 📋 Roadmap

### Versión Actual (v1.0) ✅
- [x] Sistema base de gestión
- [x] CRUD de clientes y pagos
- [x] Dashboard con estadísticas
- [x] Interfaz PyQt5 completa

### Próximas Versiones 🚧
- [ ] Gráficos avanzados con Matplotlib
- [ ] Exportación a PDF/Excel
- [ ] Sistema de respaldos
- [ ] Notificaciones automáticas
- [ ] API REST opcional
- [ ] Versión web complementaria

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 👨‍💻 Autor

**Osvaldo** - *Desarrollo Principal* - [@Osvxldx](https://github.com/Osvxldx)

## 🙏 Agradecimientos

- Inspirado en las necesidades reales de gestión municipal
- Diseñado para ser accesible en equipos de bajos recursos
- Interfaz optimizada para administradores únicos

---

**💧 Sistema de Gestión de Agua - Desarrollado con ❤️ para la gestión municipal eficiente**

[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?logo=github)](https://github.com/Osvxldx/servicio_social)
[![Documentation](https://img.shields.io/badge/Docs-Manual-blue?logo=gitbook)](MANUAL_INSTALACION.md)
