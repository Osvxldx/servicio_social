# Documentación de Requisitos - Sistema de Gestión de Pago de Agua

## 1. Tecnologías a Usar

-   **Framework principal**: Python + PyQt (aplicación de escritorio ligera y multiplataforma).  
-   **Base de datos**: SQLite (local, portátil y sin necesidad de servidor).  
-   **Frontend**: PyQt Designer + estilos CSS de Qt (interfaz limpia y personalizable).  
-   **Gráficas**: Matplotlib (para reportes simples de consumo y pagos).  
-   **Animaciones**: Transiciones básicas y fluidas, sin sobrecargar el sistema.  

## 2. Seguridad y Acceso

-   **Login**:
    -   Un solo **administrador**.  
    -   Acceso mediante **PIN numérico**.  
-   No se requieren múltiples roles de usuario.  

## 3. Gestión de Clientes

-   **Registro**:
    -   Se podrán agregar clientes manualmente desde la aplicación.  
    -   Datos obligatorios:  
        -   Nombre completo.  
        -   Dirección.  
        -   ID autogenerado único.  
        -   Estado (activo/inactivo).  
-   **Identificación de clientes**:
    -   El sistema autogenerará un ID único incremental (no editable).  
    -   Búsqueda de clientes en tiempo real:  
        -   Por **nombre**.  
        -   Por **dirección**.  
        -   Por **ID**.  

## 4. Dashboard Principal

-   **Vista general** de los clientes:  
    -   Nombre, dirección, estado de pago (✅ Pagado / ❌ Pendiente / 💧 Exceso de consumo).  
-   **Filtros**:  
    -   Ver solo clientes con deuda.  
    -   Ver solo clientes al corriente.  
-   **Botón de cambio de vista**: Tabla ↔ Gráficas simples.  

## 5. Calendario

-   Incluido en el dashboard.  
-   Permite al admin **consultar por fechas**:  
    -   Quién pagó.  
    -   Quién debe.  
    -   Quién tiene exceso de consumo.  

## 6. Perfil del Cliente

Al abrir un cliente desde el buscador o el dashboard, se mostrará:  
-   Datos completos: Nombre, dirección, ID, estado.  
-   Historial de pagos:  
    -   Montos.  
    -   Fechas exactas.  
    -   Estado del pago.  
-   Consumo de agua:  
    -   Normal.  
    -   Exceso (con registro en caso de desperdicio).  
-   Opciones:  
    -   Editar datos.  
    -   Actualizar pagos.  
    -   Marcar exceso de consumo.  

## 7. Funciones Extra

-   **Historial completo** de cada cliente (no se borra nada, solo se actualiza con nuevos registros).  
-   **Indicador de consumo extra** en caso de desperdicio de agua.  
-   **Menú lateral sencillo** con accesos a:  
    -   Dashboard.  
    -   Clientes.  
    -   Calendario.  
    -   Ajustes.  

## 8. Estilo y Usabilidad

-   Diseño **ligero y accesible** en cualquier computadora.  
-   Uso de **PyQt Designer y CSS** para personalizar colores y estilos.  
-   Animaciones simples y funcionales.  
-   Interfaz amigable para un **solo administrador**.  

---

✅ Este documento reúne todos los requisitos en su versión optimizada con **PyQt**, garantizando ligereza, accesibilidad y funcionamiento en equipos de bajos recursos.  
